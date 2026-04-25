# ==========================
# SISTEMA DE NÓMINA - POO
# ==========================
# Cumple: POO, SOLID, validaciones, deducciones, beneficios y pruebas básicas

# --------------------------
# CLASE BASE
# --------------------------
class Empleado:
    def __init__(self, nombre):
        self.nombre = nombre

    def calcular_salario(self):
        raise NotImplementedError("Debe implementar este método")


# --------------------------
# EMPLEADOS
# --------------------------
class Asalariado(Empleado):
    def __init__(self, nombre, salario, años):
        super().__init__(nombre)
        self.salario = salario
        self.años = años

    def calcular_salario(self):
        bono = 0
        if self.años > 5:
            bono = self.salario * 0.10
        return self.salario + bono + Beneficios.bono_alimentacion()


class PorHoras(Empleado):
    def __init__(self, nombre, horas, tarifa, años=0, fondo=False):
        super().__init__(nombre)
        self.horas = horas
        self.tarifa = tarifa
        self.años = años
        self.fondo = fondo

    def calcular_salario(self):
        if self.horas < 0:
            raise ValueError("Horas no pueden ser negativas")

        if self.horas <= 40:
            salario = self.horas * self.tarifa
        else:
            extras = self.horas - 40
            salario = (40 * self.tarifa) + (extras * self.tarifa * 1.5)

        if self.años > 1 and self.fondo:
            salario += salario * 0.02

        return salario


class Comision(Empleado):
    def __init__(self, nombre, salario_base, ventas):
        super().__init__(nombre)
        self.salario_base = salario_base
        self.ventas = ventas

    def calcular_salario(self):
        if self.ventas < 0:
            raise ValueError("Ventas no pueden ser negativas")

        comision = self.ventas * 0.05
        bono = 0

        if self.ventas > 20000000:
            bono = self.ventas * 0.03

        return self.salario_base + comision + bono + Beneficios.bono_alimentacion()


class Temporal(Empleado):
    def __init__(self, nombre, salario):
        super().__init__(nombre)
        self.salario = salario

    def calcular_salario(self):
        return self.salario


# --------------------------
# DEDUCCIONES
# --------------------------
class Deducciones:
    @staticmethod
    def aplicar(salario):
        seguro_pension = salario * 0.04
        salario_neto = salario - seguro_pension

        if salario_neto < 0:
            return 0

        return salario_neto


# --------------------------
# BENEFICIOS
# --------------------------
class Beneficios:
    @staticmethod
    def bono_alimentacion():
        return 1000000


# --------------------------
# SISTEMA DE NÓMINA
# --------------------------
class Nomina:
    def __init__(self):
        self.empleados = []

    def agregar_empleado(self, empleado):
        self.empleados.append(empleado)

    def calcular_nomina(self):
        print("\n===== NÓMINA =====")
        for emp in self.empleados:
            salario_bruto = emp.calcular_salario()
            salario_neto = Deducciones.aplicar(salario_bruto)

            print(f"Empleado: {emp.nombre}")
            print(f"Salario Bruto: {salario_bruto}")
            print(f"Salario Neto: {salario_neto}")
            print("----------------------")


# --------------------------
# PRUEBAS
# --------------------------
def pruebas():
    print("\n===== PRUEBAS =====")

    emp1 = Asalariado("Juan", 2000000, 6)
    assert emp1.calcular_salario() > 2000000

    emp2 = PorHoras("Ana", 45, 10000)
    assert emp2.calcular_salario() > 400000

    emp3 = Comision("Luis", 1000000, 25000000)
    assert emp3.calcular_salario() > 1000000

    emp4 = Temporal("Sofia", 1500000)
    assert emp4.calcular_salario() == 1500000

    print("Todas las pruebas pasaron correctamente")


# --------------------------
# MAIN (EJECUCIÓN)
# --------------------------
if __name__ == "__main__":
    pruebas()

    nomina = Nomina()

    nomina.agregar_empleado(Asalariado("Carlos", 3000000, 7))
    nomina.agregar_empleado(PorHoras("Maria", 50, 12000, años=2, fondo=True))
    nomina.agregar_empleado(Comision("Pedro", 1500000, 30000000))
    nomina.agregar_empleado(Temporal("Luisa", 1800000))

    nomina.calcular_nomina()
