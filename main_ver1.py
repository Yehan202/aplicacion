import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
from data.dao.dao_productos import DaoProducto, DaoEmpleado, DaoVentas, DaoTicket
from data.database import database
from data.modelo.producto import Producto
from PIL import Image, ImageTk
from fpdf import FPDF
import os
from datetime import datetime
from tkcalendar import DateEntry

class MainApp:
    def __init__(self, root, empleado_id=None, empleado_nombre=None):
        self.root = root
        self.root.title("Aplicación Principal")
        self.root.geometry("1200x800")
        self.empleado_id = empleado_id
        self.empleado_nombre = empleado_nombre

        # 顶部导航栏
        nav_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        nav_frame.pack(side="top", fill="x")
        nav_frame.grid_propagate(False)

        tk.Button(nav_frame, text="Inicio", command=self.show_inicio, bg="#3498db", fg="white", font=("Arial", 12), relief="flat", padx=20).pack(side="left", padx=5, pady=10)
        tk.Button(nav_frame, text="Gestión de Productos", command=self.show_gestion, bg="#4a90e2", fg="white").pack(side="left", padx=5, pady=5)
        tk.Button(nav_frame, text="Cobrar", command=self.show_cobrar, bg="#4a90e2", fg="white").pack(side="left", padx=5, pady=5)
        tk.Button(nav_frame, text="Transacciones", command=self.show_financia, bg="#4a90e2", fg="white").pack(side="left", padx=5, pady=5)
        tk.Label(nav_frame, text=f"Empleado: {empleado_nombre}", bg="#4a90e2", fg="white", font=("Arial", 10, "italic")).pack(side="right", padx=10)

        # 主内容区
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True)

        # 初始化各个页面Frame
        self.frames = {}
        for F in (InicioFrame, GestionProductosFrame, CobrarFrame, FinanciaFrame):
            page_name = F.__name__
            frame = F(parent=self.content_frame, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_inicio()

    def show_inicio(self):
        self.frames["InicioFrame"].tkraise()

    def show_gestion(self):
        self.frames["GestionProductosFrame"].tkraise()
        self.frames["GestionProductosFrame"].load_productos()

    def show_cobrar(self):
        self.frames["CobrarFrame"].tkraise()

    def show_financia(self):
        self.frames["FinanciaFrame"].tkraise()

class InicioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Bienvenido al sistema", font=("Arial", 18)).pack(pady=50)
        tk.Label(self, text="Sistema de Gestión de Productos", font=("Arial", 14)).pack(pady=20)
        tk.Label(self, text="Desarrollado por Yehan Xue", font=("Arial", 12)).pack(pady=10)
        # 添加logo图片
        try:
            from PIL import Image, ImageTk
            logo_img = Image.open("logo.png")  # 请将logo图片命名为logo.png并放在项目根目录或指定路径
            logo_img = logo_img.resize((200, 200))  # 根据需要调整大小
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            tk.Label(self, image=self.logo_photo).pack(pady=20)
        except Exception as e:
            tk.Label(self, text="(Logo no disponible)", font=("Arial", 12, "italic")).pack(pady=20)
        

class GestionProductosFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.dao = DaoProducto()
        tk.Label(self, text="Gestión de Productos", font=("Arial", 16)).pack(pady=10)

        self.tree = ttk.Treeview(
            self,
            columns=("ID", "Nombre", "Categoria", "Precio", "CantidadStock"),
            show="headings"
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Categoria", text="Categoría")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("CantidadStock", text="Cantidad Stock")
        self.tree.pack(pady=10)

        tk.Button(self, text="Cargar Productos", command=self.load_productos).pack(pady=5)
        tk.Button(self, text="Añadir Producto", command=self.add_producto).pack(pady=5)
        tk.Button(self, text="Eliminar Producto", command=self.delete_producto).pack(pady=5)

    def load_productos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        productos = self.dao.get_all(database)
        for producto in productos:
            self.tree.insert(
                "",
                "end",
                values=(
                    producto.id,
                    producto.nombre,
                    producto.categoria,
                    producto.precio,
                    producto.cantidad_stock
                )
            )

    def add_producto(self):
        add_window = tk.Toplevel(self)
        add_window.title("Añadir Producto")
        tk.Label(add_window, text="Nombre:").pack(pady=5)
        nombre_entry = tk.Entry(add_window)
        nombre_entry.pack(pady=5)
        tk.Label(add_window, text="Categoría:").pack(pady=5)
        categoria_entry = tk.Entry(add_window)
        categoria_entry.pack(pady=5)
        tk.Label(add_window, text="Precio:").pack(pady=5)
        precio_entry = tk.Entry(add_window)
        precio_entry.pack(pady=5)
        tk.Label(add_window, text="Cantidad Stock:").pack(pady=5)
        cantidad_entry = tk.Entry(add_window)
        cantidad_entry.pack(pady=5)

        def save_producto():
            nombre = nombre_entry.get()
            categoria = categoria_entry.get()
            precio = float(precio_entry.get())
            cantidad_stock = int(cantidad_entry.get())
            producto = Producto(None, nombre, categoria, precio, cantidad_stock)
            self.dao.insert(database, producto)
            add_window.destroy()
            self.load_productos()

        tk.Button(add_window, text="Guardar", command=save_producto).pack(pady=10)

    def delete_producto(self):
        selected_item = self.tree.selection()
        if selected_item:
            producto_id = self.tree.item(selected_item)["values"][0]
            self.dao.delete(database, producto_id)
            self.load_productos()

class CobrarFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.dao = DaoProducto()
        self.dao_ventas = DaoVentas()
        self.dao_ticket = DaoTicket()
        tk.Label(self, text="Cobrar", font=("Arial", 16)).pack(pady=10)

        # 购物车栏和按钮框架
        cart_frame = tk.Frame(self)
        cart_frame.pack(pady=10, fill="x")

        # 购物车表格
        self.cart_items = defaultdict(lambda: {"categoria": "", "precio": 0, "cantidad": 0, "subtotal": 0})
        self.total_amount = tk.DoubleVar(value=0.0)

        self.cart_tree = ttk.Treeview(
            cart_frame,
            columns=("Nombre", "Categoria", "Precio", "Cantidad", "Subtotal"),
            show="headings",
            height=10
        )
        self.cart_tree.heading("Nombre", text="Nombre")
        self.cart_tree.heading("Categoria", text="Categoría")
        self.cart_tree.heading("Precio", text="Precio")
        self.cart_tree.heading("Cantidad", text="Cantidad")
        self.cart_tree.heading("Subtotal", text="Subtotal")
        self.cart_tree.pack(side="left", pady=10, padx=5, fill="x", expand=True)

        # 按钮区放在购物车右边
        button_frame = tk.Frame(cart_frame)
        button_frame.pack(side="left", padx=10, fill="y")
        self.total_label = tk.Label(button_frame, text="Total: $0.00", font=("Arial", 14))
        self.total_label.pack(pady=5)
        tk.Button(button_frame, text="Eliminar Seleccionado", command=self.remove_from_cart).pack(pady=5, fill="x")
        tk.Button(button_frame, text="Vaciar", command=self.clear_cart).pack(pady=5, fill="x")
        tk.Button(button_frame, text="Cobrar", command=self.realizar_cobro, bg="green", fg="white").pack(pady=10, fill="x")

        # 商品按钮
        productos = self.dao.get_all(database)
        button_frame = tk.Frame(self)
        button_frame.pack(fill="y", padx=10)
        row_frame = None
        for index, producto in enumerate(productos):
            if index % 4 == 0:
                row_frame = tk.Frame(button_frame)
                row_frame.pack(fill="x", pady=5)
            product_button = tk.Button(
                row_frame,
                text=f"{producto.nombre} - ${producto.precio}",
                command=lambda p=producto: self.add_to_cart(p),
                width=30
            )
            product_button.pack(side="left", padx=5)

    def add_to_cart(self, p):
        if p.cantidad_stock <= 0:
            tk.messagebox.showwarning("Sin stock", f"El producto '{p.nombre}' no tiene stock disponible.")
            return
        if self.cart_items[p.nombre]["cantidad"] >= p.cantidad_stock:
            tk.messagebox.showwarning("Sin stock", f"No hay más stock disponible para '{p.nombre}'.")
            return
        if self.cart_items[p.nombre]["cantidad"] == 0:
            self.cart_items[p.nombre]["categoria"] = p.categoria
            self.cart_items[p.nombre]["precio"] = p.precio
        self.cart_items[p.nombre]["cantidad"] += 1
        self.cart_items[p.nombre]["subtotal"] += p.precio
        self.refresh_cart_tree()

    def refresh_cart_tree(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        for nombre, info in self.cart_items.items():
            if info["cantidad"] > 0:
                self.cart_tree.insert(
                    "", "end",
                    values=(
                        nombre,
                        info["categoria"],
                        f"${info['precio']:.2f}",
                        info["cantidad"],
                        f"${info['subtotal']:.2f}"
                    )
                )
        total = sum(info["subtotal"] for info in self.cart_items.values())
        self.total_amount.set(total)
        self.total_label.config(text=f"Total: ${total:.2f}")

    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        for item in selected:
            values = self.cart_tree.item(item, "values")
            nombre = values[0]
            if self.cart_items[nombre]["cantidad"] > 1:
                self.cart_items[nombre]["cantidad"] -= 1
                self.cart_items[nombre]["subtotal"] -= self.cart_items[nombre]["precio"]
            else:
                self.cart_items[nombre] = {"categoria": "", "precio": 0, "cantidad": 0, "subtotal": 0}
        self.refresh_cart_tree()

    def clear_cart(self):
        self.cart_items.clear()
        self.refresh_cart_tree()

    def realizar_cobro(self):
        total = self.total_amount.get()
        if total == 0:
            tk.messagebox.showwarning("Advertencia", "No hay productos seleccionados.")
            return

        cliente_id_text = self.cliente_id_entry.get().strip()
        cliente_id = int(cliente_id_text) if cliente_id_text else None

        cobrar_popup = tk.Toplevel(self)
        cobrar_popup.title("Realizar Cobro")

        tk.Label(cobrar_popup, text=f"Total a pagar: ${total:.2f}", font=("Arial", 12)).pack(pady=10)
        tk.Label(cobrar_popup, text="Monto recibido:", font=("Arial", 12)).pack(pady=5)
        recibido_entry = tk.Entry(cobrar_popup)
        recibido_entry.pack(pady=5)
        recibido_entry.bind("<Return>", lambda event: calcular_cambio())

        def calcular_cambio():
            try:
                recibido = float(recibido_entry.get())
                if recibido < total:
                    tk.messagebox.showerror("Error", "El monto recibido es menor al total.")
                    return

                cambio = recibido - total
                tk.messagebox.showinfo("Cambio", f"El cambio es: ${cambio:.2f}")

                from datetime import datetime
                fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                empleado_id = self.controller.empleado_id

                # 写入 financia.srv 文件
                with open("financia.srv", "a") as file:
                    file.write(f"{fecha_hora} - EmpleadoID: {empleado_id} - ClienteID: {cliente_id} - Total: ${total:.2f}, Recibido: ${recibido:.2f}, Cambio: ${cambio:.2f}\n")

                # 写入 ventas 表
                self.dao_ventas.insert(database, fecha_hora, cliente_id, total, empleado_id)

                # Restar stock
                productos = self.dao.get_all(database)
                nombre_a_id = {p.nombre: p.id for p in productos}
                for nombre, info in self.cart_items.items():
                    producto_id = nombre_a_id.get(nombre)
                    if producto_id:
                        for _ in range(info["cantidad"]):
                            self.dao.restar_stock(database, producto_id)

                # 生成小票内容
                ticket_lines = []
                ticket_lines.append("====== TICKET DE COMPRA ======")
                ticket_lines.append(f"empresa (nombre de la empresa)")
                ticket_lines.append(f"lugar (dirección de la empresa)")
                ticket_lines.append(f"Fecha y hora: {fecha_hora}")
                ticket_lines.append(f"Empleado ID: {empleado_id}")
                ticket_lines.append(f"Cliente ID: {cliente_id}")
                ticket_lines.append("-----------------------------")
                ticket_lines.append("Producto     Cant.   Subtotal")
                for nombre, info in self.cart_items.items():
                    if info["cantidad"] > 0:
                        ticket_lines.append(f"{nombre:15} {info['cantidad']:>3}   ${info['subtotal']:.2f}")
                ticket_lines.append("-----------------------------")
                ticket_lines.append(f"TOTAL: ${total:.2f}")
                ticket_lines.append(f"Recibido: ${recibido:.2f}")
                ticket_lines.append(f"Cambio: ${cambio:.2f}")
                ticket_lines.append("=============================")

                # 生成唯一发票名
                fecha_str = datetime.now().strftime("%Y%m%d")
                ticket_dir = "tickets"
                os.makedirs(ticket_dir, exist_ok=True)
                existing = [f for f in os.listdir(ticket_dir) if f.startswith(f"ticket_{fecha_str}_")]
                ticket_num = len(existing) + 1
                ticket_name = f"ticket_{fecha_str}_{ticket_num:03d}.pdf"
                ticket_path = os.path.join(ticket_dir, ticket_name)

                # 生成 PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in ticket_lines:
                    pdf.cell(0, 10, line, ln=True)
                pdf.output(ticket_path)

                # 保存 PDF 到数据库
                with open(ticket_path, "rb") as f:
                   ticket = f.read()
                self.dao_ticket.insert(database, ticket, cliente_id)

                cobrar_popup.destroy()
                self.clear_cart()
            except ValueError:
                tk.messagebox.showerror("Error", "Por favor, ingrese un monto válido.")

        tk.Button(cobrar_popup, text="Calcular Cambio", command=calcular_cambio).pack(pady=10)

class FinanciaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Transacciones Registradas", font=("Arial", 16)).pack(pady=10)

        # 日期选择栏
        filtro_frame = tk.Frame(self)
        filtro_frame.pack(pady=5)
        tk.Label(filtro_frame, text="Desde:").pack(side="left")
        self.fecha_inicio = DateEntry(filtro_frame, width=12, date_pattern="yyyy-mm-dd")
        self.fecha_inicio.pack(side="left", padx=5)
        tk.Label(filtro_frame, text="Hasta:").pack(side="left")
        self.fecha_fin = DateEntry(filtro_frame, width=12, date_pattern="yyyy-mm-dd")
        self.fecha_fin.pack(side="left", padx=5)
        tk.Button(filtro_frame, text="Consultar", command=self.consultar_periodo).pack(side="left", padx=10)

        columns = ("ID", "FechaHora", "EmpleadoID", "ClienteID", "Total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.total_label = tk.Label(self, text="", font=("Arial", 12, "bold"), fg="blue")
        self.total_label.pack(pady=5)

        self.sort_orders = {col: False for col in columns}  # False: 降序, True: 升序

        self.cargar_todas()

    def sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        # 判断类型
        if col == "Total":
            data.sort(key=lambda t: float(t[0]), reverse=not self.sort_orders[col])
        elif col == "ID":
            data.sort(key=lambda t: int(t[0]), reverse=not self.sort_orders[col])
        elif col == "FechaHora":
            data.sort(key=lambda t: t[0], reverse=not self.sort_orders[col])
        else:
            data.sort(reverse=not self.sort_orders[col])
        # 翻转排序顺序
        self.sort_orders[col] = not self.sort_orders[col]
        # 重新排列
        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)

    def cargar_todas(self):
        self.tree.delete(*self.tree.get_children())
        cursor = database.cursor()
        cursor.execute("SELECT id, fecha_hora, empleado_id, cliente_id, total FROM ventas ORDER BY fecha_hora DESC")
        total_sum = 0.0
        for row in cursor.fetchall():
            id_, fecha_hora, empleado_id, cliente_id, total = row
            self.tree.insert("", "end", values=(id_, fecha_hora, empleado_id, cliente_id, f"{total:.2f}"))
            total_sum += float(total)
        cursor.close()
        self.total_label.config(text=f"Total seleccionado: ${total_sum:.2f}")

    def consultar_periodo(self):
        inicio = self.fecha_inicio.get_date()
        fin = self.fecha_fin.get_date()
        self.tree.delete(*self.tree.get_children())
        cursor = database.cursor()
        sql = "SELECT id, fecha_hora, empleado_id, cliente_id, total FROM ventas WHERE DATE(fecha_hora) >= %s AND DATE(fecha_hora) <= %s ORDER BY fecha_hora DESC"
        cursor.execute(sql, (inicio, fin))
        total_sum = 0.0
        for row in cursor.fetchall():
            id_, fecha_hora, empleado_id, cliente_id, total = row
            self.tree.insert("", "end", values=(id_, fecha_hora, empleado_id, cliente_id, f"{total:.2f}"))
            total_sum += float(total)
        cursor.close()
        self.total_label.config(text=f"Total seleccionado: ${total_sum:.2f}")

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Empleado")
        self.dao = DaoEmpleado()
        self.root.geometry("700x500")

        # 设置背景图片
        try:
            bg_image = Image.open("back.jpeg")  # 请将背景图片命名为background.jpg并放在项目根目录或指定路径
            bg_image = bg_image.resize((1200, 800))  # 根据窗口大小调整图片大小
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(root, image=self.bg_photo)
            bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")

        # 显示日期和时间
        self.date_time_label = tk.Label(root, text="", font=("Arial", 20, "bold"), bg="#ffffff", fg="#000000")
        self.date_time_label.pack(anchor="nw", padx=10, pady=5)
        self.update_date_time_id = None  # 保存 after 调用的 ID
        self.update_date_time()

        # 加载 logo 图片
        try:
            logo_img = Image.open("logo.png")  # 请将 logo 图片命名为 logo.png 并放在项目根目录或指定路径
            logo_img = logo_img.resize((200, 200))  # 根据需要调整大小
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            tk.Label(root, image=self.logo_photo).pack(pady=20)
        except Exception as e:
            tk.Label(root, text="(Logo no disponible)", font=("Arial", 12, "italic")).pack(pady=20)

        # 输入框
        form_frame = tk.Frame(root, bg="#ffffff")
        form_frame.pack(pady=20)
        self.nombre_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=5)
        self.nombre_entry.focus_set()

        tk.Label(form_frame, text="Nombre de Empleado:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.nombre_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.nombre_entry.focus()

        self.msg_label = tk.Label(root, text="", fg="black", font=("Calibri", 10, "italic"), anchor="center", bg="#ffffff")
        self.msg_label.pack(pady=10, anchor="center")

        # Botones de acción
        button_frame = tk.Frame(root, bg="#ffffff")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Entrar", command=self.login, bg="#4a90e2", fg="white", font=("Arial", 15, "bold"), relief="groove", bd=3).pack(side="left", padx=5, pady=5)
        tk.Button(button_frame, text="Crear Nuevo Empleado", command=self.crear_empleado, bg="#4a90e2", fg="white", font=("Arial", 15, "bold"), relief="groove", bd=3).pack(side="left", padx=5, pady=5)
        self.nombre_entry.bind("<Return>", lambda event: self.login())

    def update_date_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_time_label.config(text=now)
        # 保存 after 调用的 ID
        self.update_date_time_id = self.root.after(1000, self.update_date_time)

    def cancel_update_date_time(self):
        if self.update_date_time_id:
            self.root.after_cancel(self.update_date_time_id)
            self.update_date_time_id = None

    def login(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            self.msg_label.config(text="Ingrese un nombre.", anchor="center")
            return
        empleado = self.dao.get_by_nombre(database, nombre)
        if empleado:
            self.cancel_update_date_time()  # 在销毁窗口前取消 after 调用
            self.root.destroy()
            main_root = tk.Tk()
            MainApp(main_root, empleado_id=empleado[0], empleado_nombre=empleado[1])
            main_root.mainloop()
        else:
            self.msg_label.config(text="Empleado no encontrado.", anchor="center")

    def crear_empleado(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            self.msg_label.config(text="Ingrese un nombre para crear.", anchor="center")
            return
        if self.dao.get_by_nombre(database, nombre):
            self.msg_label.config(text="El empleado ya existe.", anchor="center")
            return
        self.dao.insert(database, nombre)
        self.msg_label.config(text="Empleado creado. Ahora puede iniciar sesión.", fg="green", anchor="center")

# 启动
if __name__ == "__main__":
    login_root = tk.Tk()
    LoginWindow(login_root)
    login_root.mainloop()