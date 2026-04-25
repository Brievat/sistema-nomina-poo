
# SISTEMA DE NÓMINA 

from abc import ABC, abstractmethod



# CONSTANTES DE NEGOCIO (código limpio: sin "números mágicos")

PORCENTAJE_SEGURO_PENSION = 0.04    # 4 % del salario bruto
PORCENTAJE_ARL            = 0.00522 # 0.522 % (riesgo mínimo clase I, Colombia)
HORAS_REGULARES_SEMANA    = 40      # Límite de horas sin recargo
FACTOR_HORA_EXTRA         = 1.5     # Recargo horas extras
PORCENTAJE_BONO_ANTIGUEDAD = 0.10   # 10 % bono si > 5 años
UMBRAL_BONO_VENTAS        = 20_000_000  # $20.000.000
PORCENTAJE_BONO_VENTAS    = 0.03    # 3 % bono sobre ventas
BONO_ALIMENTACION         = 1_000_000   # $1.000.000 mensual
PORCENTAJE_FONDO_AHORRO   = 0.02    # 2 % fondo ahorro empleados por horas
ANIOS_BONO_ANTIGUEDAD     = 5       # Años mínimos para bono de antigüedad
ANIOS_FONDO_AHORRO        = 1       # Años mínimos para acceder al fondo



# INTERFACES — Principio I (Interface Segregation)


class CalculadorSalario(ABC):
    """Interfaz que obliga a implementar el cálculo del salario bruto."""

    @abstractmethod
    def calcular_salario_bruto(self) -> float:
        """Retorna el salario bruto del empleado antes de deducciones."""
        pass


class CalculadorBonos(ABC):
    """Interfaz que obliga a implementar el cálculo de bonos y beneficios."""

    @abstractmethod
    def calcular_bonos(self) -> float:
        """Retorna el total de bonos aplicables al empleado."""
        pass


class CalculadorDeducciones(ABC):
    """Interfaz que obliga a implementar el cálculo de deducciones."""

    @abstractmethod
    def calcular_deducciones(self) -> float:
        """Retorna el total de deducciones del empleado."""
        pass



# SERVICIO DE DEDUCCIONES — Principio S y D


class ServicioDeducciones:
    """
    Servicio responsable de calcular las deducciones obligatorias de ley.
    Principio S: única responsabilidad → calcular deducciones.
    """

    def calcular(self, salario_bruto: float) -> float:
        """
        Calcula seguro social/pensión (4 %) + ARL (0.522 %) sobre el bruto.

        Args:
            salario_bruto: Valor del salario antes de deducciones.

        Returns:
            Total de deducciones obligatorias.
        """
        seguro_pension = salario_bruto * PORCENTAJE_SEGURO_PENSION
        arl            = salario_bruto * PORCENTAJE_ARL
        return seguro_pension + arl



# CLASE BASE — Principio O y L


class Empleado(CalculadorSalario, CalculadorBonos, CalculadorDeducciones):
    """
    Clase base abstracta para todos los tipos de empleados.

    Principio O : cerrada a modificación; se extiende creando subclases.
    Principio L : cualquier subclase puede reemplazar a Empleado en Nomina.
    Principio D : recibe ServicioDeducciones por inyección de dependencias.
    """

    def __init__(
        self,
        nombre: str,
        meses_en_empresa: int,
        servicio_deducciones: ServicioDeducciones = None
    ):
        """
        Inicializa el empleado con validaciones de entrada.

        Args:
            nombre             : Nombre completo del empleado.
            meses_en_empresa   : Antigüedad en meses (debe ser >= 0).
            servicio_deducciones: Servicio inyectado para calcular deducciones.

        Raises:
            ValueError: Si el nombre está vacío o los meses son negativos.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del empleado no puede estar vacío.")
        if meses_en_empresa < 0:
            raise ValueError("Los meses en la empresa no pueden ser negativos.")

        self.nombre = nombre.strip()
        self.meses_en_empresa = meses_en_empresa
        # Inyección de dependencia (Principio D)
        self._servicio_deducciones = servicio_deducciones or ServicioDeducciones()

    @property
    def anios_en_empresa(self) -> float:
        """Calcula los años a partir de los meses de antigüedad."""
        return self.meses_en_empresa / 12

    def calcular_salario_neto(self) -> float:
        """
        Template Method: calcula el salario neto aplicando la fórmula:
            neto = salario_bruto + bonos - deducciones

        Regla de negocio: el salario neto nunca puede ser negativo.

        Returns:
            Salario neto del empleado (>= 0).
        """
        bruto      = self.calcular_salario_bruto()
        bonos      = self.calcular_bonos()
        deducciones = self.calcular_deducciones()

        neto = bruto + bonos - deducciones
        return max(0.0, neto)  # Regla: salario neto nunca negativo

    def __str__(self) -> str:
        """Representación en texto del resumen salarial del empleado."""
        return (
            f"Empleado : {self.nombre} ({self.__class__.__name__})\n"
            f"  Bruto      : ${self.calcular_salario_bruto():>13,.0f}\n"
            f"  Bonos      : ${self.calcular_bonos():>13,.0f}\n"
            f"  Deducciones: ${self.calcular_deducciones():>13,.0f}\n"
            f"  NETO       : ${self.calcular_salario_neto():>13,.0f}"
        )



# TIPOS DE EMPLEADOS — Principio O: extensión sin modificar la clase base


class Asalariado(Empleado):
    """
    Empleado con salario fijo mensual.

    Beneficios:
        - Bono del 10 % si lleva más de 5 años en la empresa.
        - Bono de alimentación ($1.000.000) por ser empleado permanente.
    Deducciones:
        - 4 % seguro social y pensión + ARL.
    """

    def __init__(self, nombre: str, meses_en_empresa: int, salario_mensual: float, **kwargs):
        """
        Args:
            nombre           : Nombre del empleado.
            meses_en_empresa : Antigüedad en meses.
            salario_mensual  : Salario fijo mensual (debe ser >= 0).

        Raises:
            ValueError: Si el salario mensual es negativo.
        """
        super().__init__(nombre, meses_en_empresa, **kwargs)
        if salario_mensual < 0:
            raise ValueError("El salario mensual no puede ser negativo.")
        self.salario_mensual = salario_mensual

    def calcular_salario_bruto(self) -> float:
        """Retorna el salario fijo mensual."""
        return self.salario_mensual

    def calcular_bonos(self) -> float:
        """
        Calcula bonos del asalariado:
          - 10 % del salario si lleva más de 5 años.
          - Bono de alimentación por ser empleado permanente.
        """
        bono_antiguedad = 0.0
        if self.anios_en_empresa > ANIOS_BONO_ANTIGUEDAD:
            bono_antiguedad = self.salario_mensual * PORCENTAJE_BONO_ANTIGUEDAD
        return bono_antiguedad + BONO_ALIMENTACION

    def calcular_deducciones(self) -> float:
        """Deducciones obligatorias: seguro/pensión + ARL sobre el bruto."""
        return self._servicio_deducciones.calcular(self.calcular_salario_bruto())


class PorHoras(Empleado):
    """
    Empleado que cobra según las horas trabajadas.

    Reglas:
        - Horas regulares (hasta 40 h/semana): tarifa normal.
        - Horas extras (más de 40 h): tarifa × 1.5.
        - Sin bonos monetarios.
    Beneficio:
        - Fondo de ahorro (2 % del bruto descontado) si lleva > 1 año y acepta.
    """

    def __init__(
        self,
        nombre: str,
        meses_en_empresa: int,
        tarifa_por_hora: float,
        horas_trabajadas: float,
        acepta_fondo_ahorro: bool = False,
        **kwargs
    ):
        """
        Args:
            nombre             : Nombre del empleado.
            meses_en_empresa   : Antigüedad en meses.
            tarifa_por_hora    : Valor pagado por cada hora (debe ser >= 0).
            horas_trabajadas   : Total de horas trabajadas en el periodo (>= 0).
            acepta_fondo_ahorro: True si el empleado acepta el descuento del fondo.

        Raises:
            ValueError: Si la tarifa o las horas son negativas.
        """
        super().__init__(nombre, meses_en_empresa, **kwargs)
        if tarifa_por_hora < 0:
            raise ValueError("La tarifa por hora no puede ser negativa.")
        if horas_trabajadas < 0:
            raise ValueError("Las horas trabajadas no pueden ser negativas.")

        self.tarifa_por_hora   = tarifa_por_hora
        self.horas_trabajadas  = horas_trabajadas
        self.acepta_fondo_ahorro = acepta_fondo_ahorro

    def calcular_salario_bruto(self) -> float:
        """
        Calcula el pago total:
          - Hasta 40 horas: tarifa normal.
          - Horas extras (> 40): tarifa × 1.5.
        """
        horas_regulares = min(self.horas_trabajadas, HORAS_REGULARES_SEMANA)
        horas_extras    = max(0.0, self.horas_trabajadas - HORAS_REGULARES_SEMANA)

        pago_regular = horas_regulares * self.tarifa_por_hora
        pago_extras  = horas_extras * self.tarifa_por_hora * FACTOR_HORA_EXTRA
        return pago_regular + pago_extras

    def calcular_bonos(self) -> float:
        """Sin bonos para empleados por horas."""
        return 0.0

    def calcular_deducciones(self) -> float:
        """
        Deducciones:
          - 4 % seguro/pensión + ARL (obligatorio).
          - 2 % fondo de ahorro si lleva > 1 año y acepta (descuento voluntario).
        """
        deduccion_base = self._servicio_deducciones.calcular(self.calcular_salario_bruto())
        fondo_ahorro   = self._calcular_fondo_ahorro()
        return deduccion_base + fondo_ahorro

    def _calcular_fondo_ahorro(self) -> float:
        """Descuento del fondo de ahorro (método privado)."""
        if self.anios_en_empresa > ANIOS_FONDO_AHORRO and self.acepta_fondo_ahorro:
            return self.calcular_salario_bruto() * PORCENTAJE_FONDO_AHORRO
        return 0.0


class Comision(Empleado):
    """
    Empleado con salario base más comisión sobre ventas.

    Reglas:
        - Salario bruto = salario_base + (ventas × porcentaje_comision).
        - Si ventas > $20.000.000: bono adicional del 3 % sobre ventas.
        - Bono de alimentación por ser empleado permanente.
    """

    def __init__(
        self,
        nombre: str,
        meses_en_empresa: int,
        salario_base: float,
        ventas_mensuales: float,
        porcentaje_comision: float = 0.05,
        **kwargs
    ):
        """
        Args:
            nombre              : Nombre del empleado.
            meses_en_empresa    : Antigüedad en meses.
            salario_base        : Salario base fijo mensual (>= 0).
            ventas_mensuales    : Monto de ventas del periodo (>= 0).
            porcentaje_comision : Fracción de comisión sobre ventas (0 a 1).

        Raises:
            ValueError: Si alguno de los valores incumple las reglas de negocio.
        """
        super().__init__(nombre, meses_en_empresa, **kwargs)
        if salario_base < 0:
            raise ValueError("El salario base no puede ser negativo.")
        if ventas_mensuales < 0:
            raise ValueError("Las ventas no pueden ser menores a $0.")
        if not (0 <= porcentaje_comision <= 1):
            raise ValueError("El porcentaje de comisión debe estar entre 0 y 1.")

        self.salario_base        = salario_base
        self.ventas_mensuales    = ventas_mensuales
        self.porcentaje_comision = porcentaje_comision

    def calcular_salario_bruto(self) -> float:
        """Retorna salario base + comisión sobre las ventas."""
        comision = self.ventas_mensuales * self.porcentaje_comision
        return self.salario_base + comision

    def calcular_bonos(self) -> float:
        """
        Bonos del empleado por comisión:
          - 3 % sobre ventas si superan $20.000.000.
          - Bono de alimentación por ser empleado permanente.
        """
        bono_ventas = 0.0
        if self.ventas_mensuales > UMBRAL_BONO_VENTAS:
            bono_ventas = self.ventas_mensuales * PORCENTAJE_BONO_VENTAS
        return bono_ventas + BONO_ALIMENTACION

    def calcular_deducciones(self) -> float:
        """Deducciones obligatorias: seguro/pensión + ARL sobre el bruto."""
        return self._servicio_deducciones.calcular(self.calcular_salario_bruto())


class Temporal(Empleado):
    """
    Empleado con contrato por tiempo definido.
    Salario fijo mensual. Sin bonos ni beneficios adicionales.
    """

    def __init__(
        self,
        nombre: str,
        meses_en_empresa: int,
        salario_mensual: float,
        duracion_contrato_meses: int,
        **kwargs
    ):
        """
        Args:
            nombre                  : Nombre del empleado.
            meses_en_empresa        : Antigüedad en meses.
            salario_mensual         : Salario fijo mensual (>= 0).
            duracion_contrato_meses : Duración del contrato en meses (> 0).

        Raises:
            ValueError: Si el salario es negativo o la duración del contrato es inválida.
        """
        super().__init__(nombre, meses_en_empresa, **kwargs)
        if salario_mensual < 0:
            raise ValueError("El salario mensual no puede ser negativo.")
        if duracion_contrato_meses <= 0:
            raise ValueError("La duración del contrato debe ser mayor a 0 meses.")

        self.salario_mensual            = salario_mensual
        self.duracion_contrato_meses    = duracion_contrato_meses

    def calcular_salario_bruto(self) -> float:
        """Retorna el salario fijo mensual."""
        return self.salario_mensual

    def calcular_bonos(self) -> float:
        """Sin bonos para empleados temporales."""
        return 0.0

    def calcular_deducciones(self) -> float:
        """Deducciones obligatorias: seguro/pensión + ARL sobre el bruto."""
        return self._servicio_deducciones.calcular(self.calcular_salario_bruto())



# SISTEMA DE NÓMINA — Principio S: única responsabilidad → gestionar empleados


class Nomina:
    """
    Servicio central del sistema de nómina.

    Responsabilidad: registrar empleados y generar el reporte de pago.
    Principio O: acepta cualquier subclase de Empleado sin modificarse.
    """

    def __init__(self):
        """Inicializa la nómina con lista vacía de empleados."""
        self._empleados: list[Empleado] = []

    def agregar_empleado(self, empleado: Empleado) -> None:
        """
        Agrega un empleado al sistema.

        Args:
            empleado: Cualquier instancia de Empleado o subclase.

        Raises:
            TypeError: Si el objeto no es una instancia de Empleado.
        """
        if not isinstance(empleado, Empleado):
            raise TypeError("Solo se pueden agregar instancias de Empleado.")
        self._empleados.append(empleado)

    def calcular_nomina(self) -> None:
        """Calcula e imprime el reporte detallado de toda la nómina."""
        if not self._empleados:
            print("No hay empleados registrados.")
            return

        total = 0.0
        print("\n" + "=" * 60)
        print("         REPORTE DE NÓMINA - CIPA SAN JACINTO 2")
        print("=" * 60)

        for emp in self._empleados:
            print(f"\n{emp}")
            print("-" * 60)
            total += emp.calcular_salario_neto()

        print(f"\n  TOTAL A PAGAR: ${total:>13,.0f}")
        print("=" * 60)

    @property
    def total_empleados(self) -> int:
        """Retorna el número de empleados registrados."""
        return len(self._empleados)



# PRUEBAS UNITARIAS FORMALES (unittest)


import unittest

class PruebasAsalariado(unittest.TestCase):
    """Pruebas del empleado asalariado."""

    def setUp(self):
        self.emp_nuevo    = Asalariado("Juan Perez",   meses_en_empresa=30, salario_mensual=2_000_000)
        self.emp_antiguo  = Asalariado("Carlos Lopez", meses_en_empresa=72, salario_mensual=4_000_000)

    def test_bruto_igual_a_salario_fijo(self):
        self.assertEqual(self.emp_nuevo.calcular_salario_bruto(), 2_000_000)

    def test_sin_bono_antiguedad_si_menos_de_5_anios(self):
        # Solo debe recibir bono de alimentación
        self.assertEqual(self.emp_nuevo.calcular_bonos(), BONO_ALIMENTACION)

    def test_bono_antiguedad_si_mas_de_5_anios(self):
        esperado = 4_000_000 * PORCENTAJE_BONO_ANTIGUEDAD + BONO_ALIMENTACION
        self.assertAlmostEqual(self.emp_antiguo.calcular_bonos(), esperado)

    def test_deduccion_incluye_seguro_y_arl(self):
        bruto    = 2_000_000
        esperado = bruto * (PORCENTAJE_SEGURO_PENSION + PORCENTAJE_ARL)
        self.assertAlmostEqual(self.emp_nuevo.calcular_deducciones(), esperado)

    def test_salario_neto_correcto(self):
        bruto  = self.emp_nuevo.calcular_salario_bruto()
        bonos  = self.emp_nuevo.calcular_bonos()
        deduc  = self.emp_nuevo.calcular_deducciones()
        self.assertAlmostEqual(self.emp_nuevo.calcular_salario_neto(), bruto + bonos - deduc)

    def test_error_salario_negativo(self):
        with self.assertRaises(ValueError):
            Asalariado("Test", 12, -1_000_000)


class PruebasPorHoras(unittest.TestCase):
    """Pruebas del empleado por horas."""

    def test_pago_sin_horas_extras(self):
        emp = PorHoras("Ana", 6, tarifa_por_hora=50_000, horas_trabajadas=40)
        self.assertAlmostEqual(emp.calcular_salario_bruto(), 40 * 50_000)

    def test_pago_con_horas_extras(self):
        emp = PorHoras("Ana", 6, tarifa_por_hora=40_000, horas_trabajadas=50)
        esperado = (40 * 40_000) + (10 * 40_000 * FACTOR_HORA_EXTRA)
        self.assertAlmostEqual(emp.calcular_salario_bruto(), esperado)

    def test_fondo_ahorro_se_descuenta(self):
        emp = PorHoras("Luis", 15, tarifa_por_hora=30_000, horas_trabajadas=40, acepta_fondo_ahorro=True)
        bruto        = emp.calcular_salario_bruto()
        deduc_base   = bruto * (PORCENTAJE_SEGURO_PENSION + PORCENTAJE_ARL)
        fondo        = bruto * PORCENTAJE_FONDO_AHORRO
        self.assertAlmostEqual(emp.calcular_deducciones(), deduc_base + fondo)

    def test_sin_fondo_ahorro_si_no_acepta(self):
        emp = PorHoras("Luis", 15, tarifa_por_hora=30_000, horas_trabajadas=40, acepta_fondo_ahorro=False)
        bruto  = emp.calcular_salario_bruto()
        esperado = bruto * (PORCENTAJE_SEGURO_PENSION + PORCENTAJE_ARL)
        self.assertAlmostEqual(emp.calcular_deducciones(), esperado)

    def test_sin_bonos(self):
        emp = PorHoras("Ana", 6, tarifa_por_hora=50_000, horas_trabajadas=40)
        self.assertEqual(emp.calcular_bonos(), 0.0)

    def test_error_horas_negativas(self):
        with self.assertRaises(ValueError):
            PorHoras("Test", 6, tarifa_por_hora=30_000, horas_trabajadas=-5)

    def test_error_tarifa_negativa(self):
        with self.assertRaises(ValueError):
            PorHoras("Test", 6, tarifa_por_hora=-10_000, horas_trabajadas=40)


class PruebasComision(unittest.TestCase):
    """Pruebas del empleado por comisión."""

    def test_bruto_es_base_mas_comision(self):
        emp = Comision("Pedro", 24, salario_base=2_000_000, ventas_mensuales=10_000_000)
        self.assertAlmostEqual(emp.calcular_salario_bruto(), 2_000_000 + 10_000_000 * 0.05)

    def test_sin_bono_ventas_bajo_umbral(self):
        emp = Comision("Pedro", 24, salario_base=2_000_000, ventas_mensuales=10_000_000)
        self.assertEqual(emp.calcular_bonos(), BONO_ALIMENTACION)

    def test_bono_ventas_sobre_umbral(self):
        emp = Comision("Pedro", 24, salario_base=2_000_000, ventas_mensuales=25_000_000)
        esperado = 25_000_000 * PORCENTAJE_BONO_VENTAS + BONO_ALIMENTACION
        self.assertAlmostEqual(emp.calcular_bonos(), esperado)

    def test_error_ventas_negativas(self):
        with self.assertRaises(ValueError):
            Comision("Test", 12, salario_base=1_000_000, ventas_mensuales=-500_000)

    def test_error_comision_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            Comision("Test", 12, salario_base=1_000_000, ventas_mensuales=0, porcentaje_comision=1.5)


class PruebasTemporal(unittest.TestCase):
    """Pruebas del empleado temporal."""

    def setUp(self):
        self.emp = Temporal("Sofia", meses_en_empresa=3, salario_mensual=1_500_000, duracion_contrato_meses=6)

    def test_bruto_es_salario_fijo(self):
        self.assertEqual(self.emp.calcular_salario_bruto(), 1_500_000)

    def test_sin_bonos(self):
        self.assertEqual(self.emp.calcular_bonos(), 0.0)

    def test_deduccion_correcta(self):
        esperado = 1_500_000 * (PORCENTAJE_SEGURO_PENSION + PORCENTAJE_ARL)
        self.assertAlmostEqual(self.emp.calcular_deducciones(), esperado)

    def test_error_duracion_contrato_cero(self):
        with self.assertRaises(ValueError):
            Temporal("Test", 2, 1_000_000, 0)

    def test_error_salario_negativo(self):
        with self.assertRaises(ValueError):
            Temporal("Test", 2, -500_000, 3)


class PruebasReglasNegocio(unittest.TestCase):
    """Pruebas de reglas de negocio generales."""

    def test_salario_neto_nunca_negativo(self):
        # Salario 0 + bono alimentación - deducciones: neto queda positivo (bono lo cubre)
        emp = Asalariado("Test", meses_en_empresa=1, salario_mensual=0)
        self.assertGreaterEqual(emp.calcular_salario_neto(), 0)

    def test_error_nombre_vacio(self):
        with self.assertRaises(ValueError):
            Asalariado("", 12, 2_000_000)

    def test_error_meses_negativos(self):
        with self.assertRaises(ValueError):
            Asalariado("Test", -1, 2_000_000)

    def test_nomina_rechaza_objeto_invalido(self):
        nomina = Nomina()
        with self.assertRaises(TypeError):
            nomina.agregar_empleado("no soy un empleado")



# PUNTO DE ENTRADA PRINCIPAL


if __name__ == "__main__":

    # 1) Ejecutar pruebas unitarias formales
    print("=" * 60)
    print("       EJECUTANDO PRUEBAS UNITARIAS (unittest)")
    print("=" * 60)
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)

    if resultado.wasSuccessful():

        # 2) Demostración del sistema con los integrantes del CIPA
        nomina = Nomina()

        nomina.agregar_empleado(Asalariado(
            "Abel Brieva Torres",
            meses_en_empresa=72,        # 6 años → recibe bono 10%
            salario_mensual=4_500_000
        ))
        nomina.agregar_empleado(Asalariado(
            "Alexis Gamarra Herrera",
            meses_en_empresa=30,        # 2.5 años → sin bono antigüedad
            salario_mensual=3_200_000
        ))
        nomina.agregar_empleado(PorHoras(
            "Fighter Ramirez Tejedor",
            meses_en_empresa=18,        # 1.5 años → accede al fondo de ahorro
            tarifa_por_hora=45_000,
            horas_trabajadas=50,        # 10 horas extras
            acepta_fondo_ahorro=True
        ))
        nomina.agregar_empleado(Comision(
            "Javier Fernandez Gamarra",
            meses_en_empresa=48,
            salario_base=2_500_000,
            ventas_mensuales=28_000_000,  # Supera $20M → bono 3%
            porcentaje_comision=0.06
        ))
        nomina.agregar_empleado(Temporal(
            "Wilson Rodriguez Carval",
            meses_en_empresa=2,
            salario_mensual=2_800_000,
            duracion_contrato_meses=6
        ))

        nomina.calcular_nomina()

        # 3) Demostración de validaciones
        print("\n" + "=" * 60)
        print("         DEMOSTRACIÓN DE VALIDACIONES")
        print("=" * 60)
        casos = [
            ("Horas negativas",   lambda: PorHoras("T", 6, 30_000, -10)),
            ("Ventas negativas",  lambda: Comision("T", 6, 1_000_000, -500_000)),
            ("Duración 0 meses",  lambda: Temporal("T", 2, 1_000_000, 0)),
            ("Nombre vacío",      lambda: Asalariado("", 12, 2_000_000)),
            ("Salario negativo",  lambda: Temporal("T", 2, -100_000, 3)),
        ]
        for descripcion, caso in casos:
            try:
                caso()
            except ValueError as e:
                print(f"  ✔ {descripcion:25s} → {e}")
