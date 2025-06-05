from data.modelo.producto import Producto,Venta

class DaoProducto:
    
    def get_all(self, db) -> list[Producto]:
        cursor = db.cursor()
        cursor.execute("SELECT id, nombre, Categoría, precio, CantidadStock FROM producto")
        productos_en_db = cursor.fetchall()
        productos: list[Producto] = []
        for producto in productos_en_db:
            prod = Producto(producto[0], producto[1], producto[2], producto[3], producto[4])
            productos.append(prod)
        cursor.close()
        return productos
    
    def insert(self, db, producto: Producto):
        cursor = db.cursor()
        sql = "INSERT INTO producto (nombre, Categoría, precio, CantidadStock) VALUES (%s, %s, %s, %s)"
        data = (producto.nombre, producto.categoria, producto.precio, producto.cantidad_stock)
        cursor.execute(sql, data)
        db.commit()
        cursor.close()

    def delete(self, db, producto_id: int):
        cursor = db.cursor()
        sql = "DELETE FROM producto WHERE id = %s"
        data = (producto_id,)
        cursor.execute(sql, data)
        db.commit()
        cursor.close()

    def restar_stock(self, db, producto_id: int):
        cursor = db.cursor()
        sql = "UPDATE producto SET CantidadStock = CantidadStock - 1 WHERE id = %s"
        data = (producto_id,)
        cursor.execute(sql, data)
        db.commit()
        cursor.close()
    def get_by_id(self, db, producto_id: int) -> Producto:
        cursor = db.cursor()
        sql = "SELECT id, nombre, Categoría, precio, CantidadStock FROM producto WHERE id = %s"
        cursor.execute(sql, (producto_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Producto(*row)
        return None
    def update (self, db, producto: Producto):
        cursor = db.cursor()
        sql = "UPDATE producto SET nombre = %s, Categoría = %s, precio = %s, CantidadStock = %s WHERE id = %s"
        data = (producto.nombre, producto.categoria, producto.precio, producto.cantidad_stock, producto.id)
        cursor.execute(sql, data)
        db.commit()
        cursor.close()

class DaoEmpleado:
    def get_by_nombre(self, db, nombre):
        cursor = db.cursor()
        cursor.execute("SELECT id, nombre FROM empleado WHERE nombre = %s", (nombre,))
        row = cursor.fetchone()
        cursor.close()
        return row

    def insert(self, db, nombre):
        cursor = db.cursor()
        sql = "INSERT INTO empleado (nombre) VALUES (%s)"
        cursor.execute(sql, (nombre,))
        db.commit()
        cursor.close()
    


class DaoVentas:
    def insert(self, db, fecha_hora, cliente_id, total, empleado_id):
        cursor = db.cursor()
        sql = "INSERT INTO ventas (fecha_hora, cliente_id, total, empleado_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (fecha_hora, cliente_id, total, empleado_id))
        db.commit()
        cursor.close()

    def get_all(self, database):
        cursor = database.cursor()
        query = "SELECT id, fecha_hora, cliente_id, total, empleado_id FROM ventas ORDER BY fecha_hora DESC"
        cursor.execute(query)
        ventas = []
        for row in cursor.fetchall():
            ventas.append(Venta(*row))  # 假设 Venta 是一个数据模型类
        cursor.close()
        return ventas
    def get_by_categoria(self, db, categoria):
        cursor = db.cursor()
        sql = "SELECT id, fecha_hora, cliente_id, total, empleado_id FROM ventas WHERE categoria = %s"
        cursor.execute(sql, (categoria,))
        ventas = []
        for row in cursor.fetchall():
            ventas.append(Venta(*row))  # Assuming Venta is a data model class
        cursor.close()
        return ventas

    def get_categories(self, db):
        cursor = db.cursor()
        query = "SELECT DISTINCT categoria FROM producto"
        cursor.execute(query)
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return categories

    def get_by_category(self, db, categoria):
        cursor = db.cursor()
        query = "SELECT id, nombre, categoria, precio, CantidadStock FROM producto WHERE categoria = %s"
        cursor.execute(query, (categoria,))
        productos = []
        for row in cursor.fetchall():
            productos.append(Producto(*row))
        cursor.close()
        return productos
    
    def get_by_period(self, database, fecha_inicio, fecha_fin):
        cursor = database.cursor()
        query = """SELECT id, fecha_hora, cliente_id, total, empleado_id 
                   FROM ventas 
                   WHERE DATE(fecha_hora) >= %s AND DATE(fecha_hora) <= %s 
                   ORDER BY fecha_hora DESC"""
        cursor.execute(query, (fecha_inicio, fecha_fin))
        ventas = []
        for row in cursor.fetchall():
            ventas.append(Venta(*row))
        cursor.close()
        return ventas

class DaoTicket:
    def insert(self, db, ticket, cliente_id):
        cursor = db.cursor()
        sql = "INSERT INTO ticket (ticket, cliente_id) VALUES (%s, %s)"
        cursor.execute(sql, (ticket, cliente_id))
        db.commit()
        cursor.close()

class DaoCliente:
    def __init__(self, database):
        self.database = database

    def insert(self, nombre, contacto, fecha_registro):
        cursor = self.database.cursor()
        query = "INSERT INTO cliente (nombre, contacto, fecha_registro) VALUES (%s, %s, %s)"
        cursor.execute(query, (nombre, contacto, fecha_registro))
        self.database.commit()
        cliente_id = cursor.lastrowid
        cursor.close()
        return cliente_id
    
    def get_by_nombre(self, nombre):
        cursor = self.database.cursor()
        query = "SELECT id, nombre, contacto, fecha_registro FROM cliente WHERE nombre = %s"
        cursor.execute(query, (nombre,))
        row = cursor.fetchone()
        cursor.close()
        return row










