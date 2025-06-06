class Producto:
    def __init__(self, id: int, nombre: str, categoria: str, precio: float, cantidad_stock: int):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.cantidad_stock = cantidad_stock

class Cliente:
    def __init__(self, id: int, nombre: str, contacto: str, estado_membresia: str, fecha_registro: str):
        self.id = id
        self.nombre = nombre
        self.contacto = contacto
        self.fecha_registro = fecha_registro

class Empleado:
    def __init__(self, id: int, nombre: str):
        self.id = id
        self.nombre = nombre
        
class Venta:
    def __init__(self, id: int, fecha_venta: str, cliente_id: int, total: float, empleado_id: int):
        self.id = id
        self.fecha_venta = fecha_venta
        self.cliente_id = cliente_id
        self.total = total
        self.empleado_id = empleado_id

class Orden:
    def __init__(self, id: int, fecha: str, detalles: str, cliente_id: int = None):
        self.id = id
        self.fecha = fecha
        self.detalles = detalles
        self.cliente_id = cliente_id

