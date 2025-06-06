import tkinter as tk
from tkinter import ttk, messagebox
import os
from collections import defaultdict
import calendar
from datetime import datetime
from data.dao.dao_productos import DaoProducto, DaoEmpleado,DaoVentas,DaoTicket,DaoOrden
from data.database import database
from data.modelo.producto import Producto

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from PIL import Image, ImageTk




# 初始化 DAO


dao_producto = DaoProducto()
dao_empleado = DaoEmpleado()
dao_ventas = DaoVentas()

class MainApp:
    def __init__(self, root, empleado_id=None, empleado_nombre=None):
        self.root = root
        self.root.title("Sistema de Gestión de Productos")
        self.root.geometry("1200x800")
        self.empleado_id = empleado_id
        self.empleado_nombre = empleado_nombre

        # Configurar el grid del root
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Barra de navegación
        nav_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        nav_frame.grid(row=0, column=0, sticky="ew")
        nav_frame.grid_propagate(False)
        
        tk.Button(nav_frame, text="Inicio", command=self.show_inicio, bg="#3498db", fg="white", font=("Arial", 12), relief="flat", padx=20).pack(side="left", padx=5, pady=10)
        tk.Button(nav_frame, text="Gestión Productos", command=self.show_gestion, 
                 bg="#3498db", fg="white", font=("Arial", 12), 
                 relief="flat", padx=20).pack(side="left", padx=5, pady=10)
        tk.Button(nav_frame, text="Punto de Venta", command=self.show_cobrar, 
                 bg="#3498db", fg="white", font=("Arial", 12), 
                 relief="flat", padx=20).pack(side="left", padx=5, pady=10)
        tk.Button(nav_frame, text="Transacciones", command=self.show_financia, 
                 bg="#3498db", fg="white", font=("Arial", 12), 
                 relief="flat", padx=20).pack(side="left", padx=5, pady=10)
        tk.Button(nav_frame, text="Órdenes", command=self.show_ordenes, 
                 bg="#3498db", fg="white", font=("Arial", 12), 
                 relief="flat", padx=20).pack(side="left", padx=5, pady=10)
        
        tk.Label(nav_frame, text=f"Usuario: {empleado_nombre}", 
                bg="#2c3e50", fg="white", font=("Arial", 10)).pack(side="right", padx=10, pady=10)
        
        tk.Button(nav_frame, text="Cerrar Sesión", command=self.logout, 
                 bg="#e74c3c", fg="white", font=("Arial", 12), 
                 relief="flat", padx=20).pack(side="right", padx=10, pady=10)

        # Área de contenido
        self.content_frame = tk.Frame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Inicializar frames
        self.frames = {}
        for F in (InicioFrame, GestionProductosFrame, CobrarFrame, FinanciaFrame, OrdenFrame):
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
        self.frames["CobrarFrame"].refresh_products()

    def show_financia(self):
        self.frames["FinanciaFrame"].tkraise()
        self.frames["FinanciaFrame"].load_ventas()

    def show_ordenes(self):
        self.frames["OrdenFrame"].tkraise()
        self.frames["OrdenFrame"].load_ordenes()

    def logout(self):
        """Cerrar sesión y volver a la ventana de inicio de sesión"""
        self.root.destroy()  # Cierra la ventana principal
        login_root = tk.Tk()
        LoginWindow(login_root)  # Vuelve a mostrar la ventana de inicio de sesión
        login_root.mainloop()

class InicioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ecf0f1")
        self.controller = controller
        
        
        logo_img = Image.open('./server/logo.png')  # 请将logo图片命名为logo.png并放在项目根目录或指定路径
        logo_img = logo_img.resize((200, 200))  # 根据需要调整大小
        self.logo_photo = ImageTk.PhotoImage(logo_img)
        tk.Label(self, image=self.logo_photo).pack(pady=20)



        # Contenedor principal
        main_container = tk.Frame(self, bg="#ecf0f1")
        main_container.pack(expand=True, fill="both")
        
        # Título principal
        tk.Label(main_container, text="Sistema de Gestión de Productos", 
                font=("Arial", 24, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=50)
        # Imagen de bienvenida
             
        # Información del sistema
        info_frame = tk.Frame(main_container, bg="#ffffff", relief="solid", bd=1)
        info_frame.pack(pady=20, padx=100, fill="x")
        
        tk.Label(info_frame, text="Bienvenido al Sistema", 
                font=("Arial", 16), bg="#ffffff", fg="#34495e").pack(pady=20)
        tk.Label(info_frame, text="Funcionalidades disponibles:", 
                font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=10)
        
        features = [
            "• Gestión completa de productos",
            "• Punto de venta integrado",
            "• Control de inventario",
            "• Reportes de transacciones",
            "• Sistema de usuarios"
        ]
        
        for feature in features:
            tk.Label(info_frame, text=feature, font=("Arial", 10), 
                    bg="#ffffff", fg="#7f8c8d").pack(anchor="w", padx=40, pady=2)
        
        tk.Label(info_frame, text="", bg="#ffffff").pack(pady=10)

class GestionProductosFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ecf0f1")
        self.controller = controller
        self.dao = DaoProducto()  # Usar DAO para interactuar con la base de datos

        # Título
        tk.Label(self, text="Gestión de Productos", 
                 font=("Arial", 18, "bold"), bg="#ecf0f1").pack(pady=20)

        # Frame para botones
        button_frame = tk.Frame(self, bg="#ecf0f1")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Cargar Productos", command=self.load_productos,
                  bg="#27ae60", fg="white", font=("Arial", 10), padx=20).pack(side="left", padx=5)
        tk.Button(button_frame, text="Añadir Producto", command=self.add_producto,
                  bg="#3498db", fg="white", font=("Arial", 10), padx=20).pack(side="left", padx=5)
        tk.Button(button_frame, text="Actualizar Producto", command=self.update_producto,
                  bg="#f39c12", fg="white", font=("Arial", 10), padx=20).pack(side="left", padx=5)  # Nuevo botón
        tk.Button(button_frame, text="Eliminar Producto", command=self.delete_producto,
                  bg="#e74c3c", fg="white", font=("Arial", 10), padx=20).pack(side="left", padx=5)

        # Tabla de productos
        columns = ("ID", "Nombre", "Categoría", "Precio", "Stock")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def load_productos(self):
        """Cargar productos desde la base de datos"""
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        # Cargar productos desde DAO
        productos = self.dao.get_all(database)
        for producto in productos:
            self.tree.insert("", "end", values=(
                producto.id, producto.nombre, producto.categoria, 
                f"${producto.precio:.2f}", producto.cantidad_stock
            ))

    def add_producto(self):
        """Abrir ventana para añadir un nuevo producto"""
        add_window = tk.Toplevel(self)
        add_window.title("Añadir Producto")
        add_window.geometry("400x300")
        add_window.resizable(False, False)
        
        # Centrar ventana
        add_window.transient(self)
        add_window.grab_set()
        
        tk.Label(add_window, text="Nombre:", font=("Arial", 10)).pack(pady=5)
        nombre_entry = tk.Entry(add_window, font=("Arial", 10), width=30)
        nombre_entry.pack(pady=5)
        
        tk.Label(add_window, text="Categoría:", font=("Arial", 10)).pack(pady=5)
        categoria_entry = tk.Entry(add_window, font=("Arial", 10), width=30)
        categoria_entry.pack(pady=5)
        
        tk.Label(add_window, text="Precio:", font=("Arial", 10)).pack(pady=5)
        precio_entry = tk.Entry(add_window, font=("Arial", 10), width=30)
        precio_entry.pack(pady=5)
        
        tk.Label(add_window, text="Cantidad Stock:", font=("Arial", 10)).pack(pady=5)
        cantidad_entry = tk.Entry(add_window, font=("Arial", 10), width=30)
        cantidad_entry.pack(pady=5)

        def save_producto():
            try:
                nombre = nombre_entry.get().strip()
                categoria = categoria_entry.get().strip()
                precio = float(precio_entry.get())
                cantidad_stock = int(cantidad_entry.get())
                
                if not nombre or not categoria:
                    messagebox.showerror("Error", "Por favor complete todos los campos")
                    return
                
                # Crear producto usando DAO
                producto = Producto(None, nombre, categoria, precio, cantidad_stock)
                self.dao.insert(database, producto)
                
                messagebox.showinfo("Éxito", "Producto añadido correctamente")
                add_window.destroy()
                self.load_productos()
                
            except ValueError:
                messagebox.showerror("Error", "Precio y cantidad deben ser números válidos")

        tk.Button(add_window, text="Guardar", command=save_producto,
                  bg="#27ae60", fg="white", font=("Arial", 10), padx=20).pack(pady=10)

    def update_producto(self):
        """Abrir ventana para actualizar un producto seleccionado"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un producto para actualizar")
            return
        
        producto_id = int(self.tree.item(selected_item)["values"][0])
        producto = self.dao.get_by_id(database, producto_id)
        
        if not producto:
            messagebox.showerror("Error", "No se pudo encontrar el producto seleccionado")
            return

        update_window = tk.Toplevel(self)
        update_window.title("Actualizar Producto")
        update_window.geometry("400x300")
        update_window.resizable(False, False)
        
        # Centrar ventana
        update_window.transient(self)
        update_window.grab_set()
        
        tk.Label(update_window, text="Nombre:", font=("Arial", 10)).pack(pady=5)
        nombre_entry = tk.Entry(update_window, font=("Arial", 10), width=30)
        nombre_entry.insert(0, producto.nombre)
        nombre_entry.pack(pady=5)
        
        tk.Label(update_window, text="Categoría:", font=("Arial", 10)).pack(pady=5)
        categoria_entry = tk.Entry(update_window, font=("Arial", 10), width=30)
        categoria_entry.insert(0, producto.categoria)
        categoria_entry.pack(pady=5)
        
        tk.Label(update_window, text="Precio:", font=("Arial", 10)).pack(pady=5)
        precio_entry = tk.Entry(update_window, font=("Arial", 10), width=30)
        precio_entry.insert(0, f"{producto.precio:.2f}")
        precio_entry.pack(pady=5)
        
        tk.Label(update_window, text="Cantidad Stock:", font=("Arial", 10)).pack(pady=5)
        cantidad_entry = tk.Entry(update_window, font=("Arial", 10), width=30)
        cantidad_entry.insert(0, f"{producto.cantidad_stock}")
        cantidad_entry.pack(pady=5)

        def save_changes():
            try:
                nombre = nombre_entry.get().strip()
                categoria = categoria_entry.get().strip()
                precio = float(precio_entry.get())
                cantidad_stock = int(cantidad_entry.get())
                
                if not nombre or not categoria:
                    messagebox.showerror("Error", "Por favor complete todos los campos")
                    return
                
                # Actualizar producto usando DAO
                producto_actualizado = Producto(producto_id, nombre, categoria, precio, cantidad_stock)
                self.dao.update(database, producto_actualizado)
                
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                update_window.destroy()
                self.load_productos()
                
            except ValueError:
                messagebox.showerror("Error", "Precio y cantidad deben ser números válidos")

        tk.Button(update_window, text="Guardar Cambios", command=save_changes,
                  bg="#f39c12", fg="white", font=("Arial", 10), padx=20).pack(pady=10)

    def delete_producto(self):
        """Eliminar un producto seleccionado"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
            producto_id = int(self.tree.item(selected_item)["values"][0])
            self.dao.delete(database, producto_id)
            self.load_productos()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")



class CobrarFrame(tk.Frame):
    def __init__(self, parent, controller):  # Punto de Venta
        super().__init__(parent, bg="#ecf0f1")
        self.controller = controller
        self.dao = DaoProducto()
        self.dao_ventas = DaoVentas()
        self.dao_ticket = DaoTicket()
        self.cart_items = defaultdict(lambda: {"precio": 0, "cantidad": 0, "subtotal": 0, "producto_id": None})
        
        self.setup_ui()
        self.refresh_products()

    def setup_ui(self): # Configura la interfaz de usuario
        """Configura la interfaz de usuario"""
        # Título
        title_label = tk.Label(self, text="Punto de Venta", 
                              font=("Arial", 18, "bold"), bg="#ecf0f1", fg="#2c3e50")
        title_label.pack(pady=10)

        # Frame principal dividido en dos columnas
        main_frame = tk.Frame(self, bg="#ecf0f1")
        main_frame.pack(fill="both", expand=True, padx=20)
        
        self.setup_products_section(main_frame)
        self.setup_cart_section(main_frame)

    def setup_products_section(self, parent):
        """Configura la sección de productos"""
        # Columna izquierda - Productos
        left_frame = tk.Frame(parent, bg="#ffffff", relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Título de productos
        products_title = tk.Label(left_frame, text="Productos Disponibles", 
                                 font=("Arial", 14, "bold"), bg="#ffffff", fg="#2c3e50")
        products_title.pack(pady=10)
        
        # Frame para filtros
        filter_frame = tk.Frame(left_frame, bg="#ffffff")
        filter_frame.pack(pady=5, padx=10, fill="x")
        
        tk.Label(filter_frame, text="Filtrar por categoría:", bg="#ffffff").pack(side="left")
        self.category_var = tk.StringVar(value="Todas")
        self.category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, 
                                          state="readonly", width=15)
        self.category_combo.pack(side="left", padx=5)
        self.category_combo.bind("<<ComboboxSelected>>", self.filter_products)
        
        # Botón actualizar
        refresh_btn = tk.Button(filter_frame, text="Actualizar", 
                               command=self.refresh_products,
                               bg="#3498db", fg="white", font=("Arial", 9))
        refresh_btn.pack(side="right")
        
        # Scrollable frame para productos
        canvas_frame = tk.Frame(left_frame, bg="#ffffff")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#ffffff")
        scrollbar_products = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.products_frame = tk.Frame(self.canvas, bg="#ffffff")
        
        self.products_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.products_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_products.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar_products.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def setup_cart_section(self, parent):
        """Configura la sección del carrito"""
        # Columna derecha - Carrito
        right_frame = tk.Frame(parent, bg="#ffffff", relief="solid", bd=1, width=450)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Título del carrito
        cart_title = tk.Label(right_frame, text="Carrito de Compras", 
                             font=("Arial", 14, "bold"), bg="#ffffff", fg="#2c3e50")
        cart_title.pack(pady=10)
        
        # Cliente ID
        cliente_frame = tk.Frame(right_frame, bg="#ffffff")
        cliente_frame.pack(pady=5, padx=10, fill="x")
        tk.Label(cliente_frame, text="Cliente ID:", bg="#ffffff", font=("Arial", 10)).pack(side="left")
        self.cliente_id_entry = tk.Entry(cliente_frame, width=15, font=("Arial", 10))
        self.cliente_id_entry.pack(side="right")
        
        # Tabla del carrito con scrollbar
        cart_frame = tk.Frame(right_frame, bg="#ffffff")
        cart_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        cart_columns = ("Producto", "Cant.", "Precio", "Subtotal")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show="headings", height=10)
        
        # Configurar columnas
        column_widths = {"Producto": 140, "Cant.": 50, "Precio": 80, "Subtotal": 80}
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=column_widths.get(col, 80), anchor="center" if col != "Producto" else "w")
        
        # Scrollbar para el carrito
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side="left", fill="both", expand=True)
        cart_scrollbar.pack(side="right", fill="y")
        
        # Total
        self.total_label = tk.Label(right_frame, text="Total: $0.00", 
                                   font=("Arial", 16, "bold"), bg="#ffffff", fg="#e74c3c")
        self.total_label.pack(pady=15)
        
        # Botones del carrito
        self.setup_cart_buttons(right_frame)

    def setup_cart_buttons(self, parent):
        """Configura los botones del carrito"""
        cart_buttons = tk.Frame(parent, bg="#ffffff")
        cart_buttons.pack(pady=10, padx=10, fill="x")
        
        # Botones de cantidad
        quantity_frame = tk.Frame(cart_buttons, bg="#ffffff")
        quantity_frame.pack(fill="x", pady=2)
        
        tk.Button(quantity_frame, text="- Cantidad", command=self.decrease_quantity,
                 bg="#f39c12", fg="white", font=("Arial", 9), width=12).pack(side="left", padx=2)
        tk.Button(quantity_frame, text="+ Cantidad", command=self.increase_quantity,
                 bg="#2980b9", fg="white", font=("Arial", 9), width=12).pack(side="right", padx=2)
        
        # Otros botones
        tk.Button(cart_buttons, text="Quitar Producto", command=self.remove_from_cart,
                 bg="#e67e22", fg="white", font=("Arial", 10), width=20).pack(fill="x", pady=2)
        tk.Button(cart_buttons, text="Vaciar Carrito", command=self.clear_cart,
                 bg="#e74c3c", fg="white", font=("Arial", 10), width=20).pack(fill="x", pady=2)
        
        # Separador
        separator = tk.Frame(cart_buttons, height=2, bg="#bdc3c7")
        separator.pack(fill="x", pady=10)
        
        # Botón principal
        tk.Button(cart_buttons, text="PROCESAR VENTA", command=self.realizar_cobro,
                 bg="#27ae60", fg="white", font=("Arial", 12, "bold"), 
                 height=2, relief="raised", bd=3).pack(fill="x", pady=5)

    def _on_mousewheel(self, event):
        """Maneja el scroll del mouse en el canvas"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def refresh_products(self):
        """Actualiza la lista de productos"""
        try:
            # Limpiar productos existentes
            for widget in self.products_frame.winfo_children():
                widget.destroy()
            
            # Obtener productos de la base de datos
            productos = self.dao.get_all(database)
            
            # Actualizar categorías
            self.update_categories(productos)
            
            # Filtrar productos si es necesario
            categoria_seleccionada = self.category_var.get()
            if categoria_seleccionada != "Todas":
                productos = [p for p in productos if p.categoria == categoria_seleccionada]
            
            # Mostrar productos
            self.display_products(productos)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")

    def update_categories(self, productos):
        """Actualiza el combobox de categorías"""
        categorias = list(set(p.categoria for p in productos))
        categorias.sort()
        categorias.insert(0, "Todas")
        
        self.category_combo['values'] = categorias
        if self.category_var.get() not in categorias:
            self.category_var.set("Todas")

    def display_products(self, productos):
        """Muestra los productos en la interfaz"""
        productos_por_fila = 4
        
        for index, producto in enumerate(productos):
            if index % productos_por_fila == 0:
                row_frame = tk.Frame(self.products_frame, bg="#ffffff")
                row_frame.pack(fill="x", pady=5, padx=5)
            
            # Determinar color y estado según stock
            color, estado, text_color = self.get_product_display_info(producto)
            
            product_button = tk.Button(
                row_frame,
                text=f"{producto.nombre}\n${producto.precio:.2f}\n{estado}",
                command=lambda p=producto: self.add_to_cart(p),
                width=18,
                height=4,
                bg=color,
                fg=text_color,
                font=("Arial", 9, "bold"),
                relief="raised",
                bd=2,
                state="normal" if producto.cantidad_stock > 0 else "disabled",
                cursor="hand2" if producto.cantidad_stock > 0 else "arrow"
            )
            product_button.pack(side="left", padx=5)
            
            # Efecto hover
            if producto.cantidad_stock > 0:
                self.add_hover_effect(product_button, color)

    def get_product_display_info(self, producto):
        """Retorna información de visualización del producto"""
        if producto.cantidad_stock <= 0:
            return "#c0392b", "SIN STOCK", "white"
        elif producto.cantidad_stock <= 5:
            return "#f39c12", f"Stock: {producto.cantidad_stock}", "white"
        else:
            return "#27ae60", f"Stock: {producto.cantidad_stock}", "white"

    def add_hover_effect(self, button, original_color):
        """Agrega efecto hover a los botones"""
        def on_enter(e):
            button.config(bg=self.lighten_color(original_color))
        
        def on_leave(e):
            button.config(bg=original_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def lighten_color(self, color):  # Aclara un color para el efecto hover
        """Aclara un color para el efecto hover"""
        color_map = {
            "#27ae60": "#2ecc71",
            "#f39c12": "#f1c40f",
            "#c0392b": "#e74c3c"
        }
        return color_map.get(color, color)

    def filter_products(self, event=None):  # Filtra productos por categoría
        """Filtra productos por categoría"""
        self.refresh_products()

    def add_to_cart(self, producto):
        """Agrega un producto al carrito"""
        try:
            # Verificar stock disponible
            if producto.cantidad_stock <= 0:
                messagebox.showwarning("Sin Stock", f"El producto '{producto.nombre}' no tiene stock disponible.")
                return
            
            # Verificar si ya se alcanzó el límite de stock en el carrito
            if self.cart_items[producto.nombre]["cantidad"] >= producto.cantidad_stock:
                messagebox.showwarning("Sin Stock", f"No hay más stock disponible para '{producto.nombre}'.")
                return
            
            # Agregar al carrito
            if self.cart_items[producto.nombre]["cantidad"] == 0:
                self.cart_items[producto.nombre]["precio"] = producto.precio
                self.cart_items[producto.nombre]["producto_id"] = producto.id
            
            self.cart_items[producto.nombre]["cantidad"] += 1
            self.cart_items[producto.nombre]["subtotal"] = (
                self.cart_items[producto.nombre]["precio"] * 
                self.cart_items[producto.nombre]["cantidad"]
            )
            
            self.refresh_cart()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")

    def increase_quantity(self):
        """Aumenta la cantidad del producto seleccionado"""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para aumentar cantidad")
            return
        
        item = selected[0]
        values = self.cart_tree.item(item, "values")
        nombre = values[0]
        
        # Buscar el producto para verificar stock
        productos = self.dao.get_all(database)
        producto = next((p for p in productos if p.nombre == nombre), None)
        
        if producto and self.cart_items[nombre]["cantidad"] < producto.cantidad_stock:
            self.cart_items[nombre]["cantidad"] += 1
            self.cart_items[nombre]["subtotal"] = (
                self.cart_items[nombre]["precio"] * 
                self.cart_items[nombre]["cantidad"]
            )
            self.refresh_cart()
        else:
            messagebox.showwarning("Sin Stock", f"No hay más stock disponible para '{nombre}'.")

    def decrease_quantity(self):
        """Disminuye la cantidad del producto seleccionado"""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para disminuir cantidad")
            return
        
        item = selected[0]
        values = self.cart_tree.item(item, "values")
        nombre = values[0]
        
        if self.cart_items[nombre]["cantidad"] > 1:
            self.cart_items[nombre]["cantidad"] -= 1
            self.cart_items[nombre]["subtotal"] = (
                self.cart_items[nombre]["precio"] * 
                self.cart_items[nombre]["cantidad"]
            )
            self.refresh_cart()
        else:
            messagebox.showinfo("Información", "Use 'Quitar Producto' para eliminar completamente el item")

    def refresh_cart(self):
        """Actualiza la vista del carrito"""
        # Limpiar carrito
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        total = 0
        for nombre, info in self.cart_items.items():
            if info["cantidad"] > 0:
                self.cart_tree.insert("", "end", values=(
                    nombre, 
                    info["cantidad"], 
                    f"${info['precio']:.2f}", 
                    f"${info['subtotal']:.2f}"
                ))
                total += info["subtotal"]
        
        self.total_label.config(text=f"Total: ${total:.2f}")

    def remove_from_cart(self): 
        """Remueve completamente un producto del carrito"""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para quitar")
            return
        
        item = selected[0]
        values = self.cart_tree.item(item, "values")
        nombre = values[0]
        
        if messagebox.askyesno("Confirmar", f"¿Quitar '{nombre}' del carrito?"):
            self.cart_items[nombre] = {"precio": 0, "cantidad": 0, "subtotal": 0, "producto_id": None}
            self.refresh_cart()

    def clear_cart(self):
        """Vacía completamente el carrito"""
        if not any(info["cantidad"] > 0 for info in self.cart_items.values()):
            messagebox.showinfo("Información", "El carrito ya está vacío")
            return
            
        if messagebox.askyesno("Confirmar", "¿Vaciar todo el carrito?"):
            self.cart_items.clear()
            self.refresh_cart()

    def realizar_cobro(self): # Procesa la venta
        """Procesa la venta"""
        
        try:
            # Calcular total
            total = sum(float(info["subtotal"]) for info in self.cart_items.values() if info["cantidad"] > 0)

            if total == 0:
                messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito")
                return

            # Validar cliente ID
            cliente_id_text = self.cliente_id_entry.get().strip()
            cliente_id = None
            if cliente_id_text:
                try:
                    cliente_id = int(cliente_id_text)
                except ValueError:
                    messagebox.showerror("Error", "El ID del cliente debe ser un número")
                    return

            # Obtener empleado_id automáticamente
            empleado_id = self.controller.empleado_id
            if not empleado_id:
                messagebox.showerror("Error", "No se pudo obtener el ID del empleado")
                return

            # Abrir ventana de cobro
            self.open_payment_window(total, cliente_id, empleado_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar cobro: {str(e)}")

    def open_payment_window(self, total, cliente_id, empleado_id):  # Abre la ventana de procesamiento de pago
        """Abre la ventana de procesamiento de pago"""
        cobro_window = tk.Toplevel(self)
        cobro_window.title("Procesar Venta")
        cobro_window.geometry("450x400")
        cobro_window.resizable(False, False)
        cobro_window.transient(self)
        cobro_window.grab_set()
        cobro_window.configure(bg="#ecf0f1")

        # Centrar ventana
        cobro_window.update_idletasks()
        x = (cobro_window.winfo_screenwidth() // 2) - (450 // 2)
        y = (cobro_window.winfo_screenheight() // 2) - (400 // 2)
        cobro_window.geometry(f"450x400+{x}+{y}")

        # Título
        tk.Label(cobro_window, text="Procesar Venta", 
                font=("Arial", 18, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=20)

        # Resumen de venta
        summary_frame = tk.Frame(cobro_window, bg="#ffffff", relief="solid", bd=1)
        summary_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(summary_frame, text="Resumen de Venta", 
                font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=5)
        
        items_count = sum(info["cantidad"] for info in self.cart_items.values() if info["cantidad"] > 0)
        tk.Label(summary_frame, text=f"Productos: {items_count}", 
                bg="#ffffff", font=("Arial", 10)).pack()
        tk.Label(summary_frame, text=f"Cliente: {cliente_id or 'N/A'}", 
                bg="#ffffff", font=("Arial", 10)).pack()
        tk.Label(summary_frame, text=f"Total a Pagar: ${total:.2f}", 
                font=("Arial", 16, "bold"), bg="#ffffff", fg="#e74c3c").pack(pady=10)

        # Entrada de pago
        payment_frame = tk.Frame(cobro_window, bg="#ecf0f1")
        payment_frame.pack(pady=20)
        
        tk.Label(payment_frame, text="Monto Recibido:", 
                font=("Arial", 12, "bold"), bg="#ecf0f1").pack(pady=5)
        recibido_entry = tk.Entry(payment_frame, font=("Arial", 14), width=15, 
                                 justify="center", relief="solid", bd=2)
        recibido_entry.pack(pady=5)
        recibido_entry.focus()

        # Label para resultados
        result_label = tk.Label(cobro_window, text="", font=("Arial", 12, "bold"), bg="#ecf0f1")
        result_label.pack(pady=10)

        def procesar_pago():
            try:
                recibido_text = recibido_entry.get().strip()
                if not recibido_text:
                    result_label.config(text="¡Ingrese un monto!", fg="#e74c3c")
                    return
                
                recibido = float(recibido_text)
                if recibido < 0:
                    result_label.config(text="¡El monto no puede ser negativo!", fg="#e74c3c")
                    return
                    
                if recibido < total:
                    faltante = float(total - recibido)	
                    result_label.config(text=f"¡Faltan ${faltante:.2f}!", fg="#e74c3c")
                    return

                cambio = float(recibido - total)
                
                result_label.config(text=f"Cambio: ${cambio:.2f}", fg="#27ae60")

                # Confirmar venta
                if messagebox.askyesno("Confirmar Venta", 
                                     f"¿Procesar venta por ${total:.2f}?\nCambio: ${cambio:.2f}"):
                    self.process_sale(total, recibido, cambio, cliente_id, empleado_id, cobro_window)

            except ValueError:
                result_label.config(text="¡Ingrese un monto válido!", fg="#e74c3c")
            except Exception as e:
                result_label.config(text=f"Error: {str(e)}", fg="#e74c3c")

        # Botones
        buttons_frame = tk.Frame(cobro_window, bg="#ecf0f1")
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="Procesar Pago", command=procesar_pago,
                  bg="#27ae60", fg="white", font=("Arial", 12, "bold"), 
                  padx=30, pady=10, relief="raised", bd=3).pack(side="left", padx=10)
        
        tk.Button(buttons_frame, text="Cancelar", command=cobro_window.destroy,
                  bg="#95a5a6", fg="white", font=("Arial", 12), 
                  padx=30, pady=10).pack(side="left", padx=10)

        # Bind Enter key
        recibido_entry.bind("<Return>", lambda event: procesar_pago())

    def process_sale(self, total, recibido, cambio, cliente_id, empleado_id, window):
        """Procesa la venta en la base de datos"""
        try:
            # Validar empleado_id
            cursor = database.cursor()
            cursor.execute("SELECT id FROM empleado WHERE id = %s", (empleado_id,))
            empleado = cursor.fetchone()
            cursor.close()
            
            if not empleado:
                raise ValueError(f"El empleado con ID {empleado_id} no existe en la base de datos.")
            
            # Validar carrito
            if not any(info["cantidad"] > 0 for info in self.cart_items.values()):
                raise ValueError("El carrito está vacío. No se puede procesar la venta.")
            
            # Registrar venta
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.dao_ventas.insert(database, fecha_hora, cliente_id, float(total), empleado_id)

            # Actualizar stock
            productos = self.dao.get_all(database)
            nombre_a_id = {p.nombre: p.id for p in productos}
            for nombre, info in self.cart_items.items():
                producto_id = nombre_a_id.get(nombre)
                if producto_id:
                    for _ in range(info["cantidad"]):
                        self.dao.restar_stock(database, producto_id)
            # Generar ticket
            ticket = self.generar_ticket(float(total), float(recibido), float(cambio), cliente_id, fecha_hora)

            # Registrar ticket
            self.dao_ticket.insert(database, ticket, cliente_id)
            self.dao_ventas.insert(database, fecha_hora, cliente_id, total, empleado_id)


            # Mostrar confirmación
            messagebox.showinfo("Venta Exitosa", 
                              f"¡Venta procesada correctamente!\n\n"
                              f"Total: ${total:.2f}\n"
                              f"Recibido: ${recibido:.2f}\n"
                              f"Cambio: ${cambio:.2f}\n\n"
                              f"Ticket guardado en: {ticket}")

            # Limpiar y cerrar
            window.destroy()
            self.clear_cart()
            self.refresh_products()

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar venta: {str(e)}")

    def generar_ticket(self, total, recibido, cambio, cliente_id, fecha_hora):
        """Genera el ticket de venta"""
        try:
            # Crear directorio si no existe
            os.makedirs("tickets", exist_ok=True)
            
            # Nombre del archivo
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            ticket_path = f"tickets/ticket_{fecha_str}.txt"
            
            # Obtener nombre del empleado
            empleado_nombre = getattr(self.controller, 'empleado_nombre', 'N/A')
            
            # Generar contenido del ticket
            with open(ticket_path, "w", encoding="utf-8") as f:
                f.write("=" * 55 + "\n")
                f.write("                TICKET DE VENTA\n")
                f.write("=" * 55 + "\n")
                f.write(f"Fecha: {fecha_hora}\n")
                f.write(f"Empleado: {empleado_nombre}\n")
                f.write(f"Cliente ID: {cliente_id or 'N/A'}\n")
                f.write("-" * 55 + "\n")
                f.write("PRODUCTOS:\n")
                f.write("-" * 55 + "\n")
                f.write(f"{'Producto':<25} {'Cant':>4} {'Precio':>10} {'Subtotal':>12}\n")
                f.write("-" * 55 + "\n")
                
                for nombre, info in self.cart_items.items():
                    if info["cantidad"] > 0:
                        f.write(f"{nombre[:24]:<25} {info['cantidad']:>4} "
                               f"${info['precio']:>8.2f} ${info['subtotal']:>10.2f}\n")
                
                f.write("-" * 55 + "\n")
                f.write(f"{'TOTAL:':>43} ${total:>8.2f}\n")
                f.write(f"{'RECIBIDO:':>43} ${recibido:>8.2f}\n")
                f.write(f"{'CAMBIO:':>43} ${cambio:>8.2f}\n")
                f.write("=" * 55 + "\n")
                f.write("             ¡Gracias por su compra!\n")
                f.write("               Vuelva pronto\n")
                f.write("=" * 55 + "\n")
            
            return ticket_path
                
        except Exception as e:
            print(f"Error generando ticket: {e}")
            return "Error al generar ticket"

class FinanciaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ecf0f1")
        self.controller = controller
        self.dao_ventas = DaoVentas()
        
        self.create_widgets()
        self.load_ventas()
    
    def create_widgets(self):
        # Título
        title_label = tk.Label(self, text="Historial de Transacciones y Análisis", 
                             font=("Arial", 18, "bold"), bg="#ecf0f1", fg="#2c3e50")
        title_label.pack(pady=20)
        
        # Frame principal dividido en dos columnas
        main_frame = tk.Frame(self, bg="#ecf0f1")
        main_frame.pack(fill="both", expand=True, padx=20)
        
        # Columna izquierda - Controles y tabla
        left_frame = tk.Frame(main_frame, bg="#ecf0f1")
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Frame de controles de período
        period_frame = tk.LabelFrame(left_frame, text="Consultas por Período", 
                                   font=("Arial", 12, "bold"), bg="#ecf0f1", fg="#2c3e50")
        period_frame.pack(fill="x", pady=10)
        
        # Botones de período predefinido
        quick_buttons_frame = tk.Frame(period_frame, bg="#ecf0f1")
        quick_buttons_frame.pack(pady=10)
        
        periods = [
            ("Hoy", self.consultar_hoy, "#e74c3c"),
            ("Esta Semana", self.consultar_semana, "#f39c12"),
            ("Este Mes", self.consultar_mes, "#27ae60"),
            ("Este Año", self.consultar_año, "#3498db")
        ]
        
        for i, (text, command, color) in enumerate(periods):
            btn = tk.Button(quick_buttons_frame, text=text, command=command,
                           bg=color, fg="white", font=("Arial", 9), padx=15)
            btn.grid(row=0, column=i, padx=5)
        
        # Selector de período personalizado
        custom_frame = tk.Frame(period_frame, bg="#ecf0f1")
        custom_frame.pack(pady=10)
        
        tk.Label(custom_frame, text="Desde:", bg="#ecf0f1", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.fecha_inicio = DateEntry(custom_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_inicio.grid(row=0, column=1, padx=5)
        
        tk.Label(custom_frame, text="Hasta:", bg="#ecf0f1", font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.fecha_fin = DateEntry(custom_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_fin.grid(row=0, column=3, padx=5)
        
        tk.Button(custom_frame, text="Consultar Período", command=self.consultar_periodo,
                 bg="#9b59b6", fg="white", font=("Arial", 10), padx=15).grid(row=0, column=4, padx=10)
        
        # Botones de acción
        button_frame = tk.Frame(left_frame, bg="#ecf0f1")
        button_frame.pack(pady=10)
        
        actions = [
            ("Actualizar Todo", self.load_ventas, "#3498db"),
            ("Exportar", self.export_ventas, "#27ae60"),
            ("Gráfica Mensual", self.mostrar_grafica_mensual, "#e67e22")
        ]
        
        for text, command, color in actions:
            tk.Button(button_frame, text=text, command=command,
                     bg=color, fg="white", font=("Arial", 10), padx=20).pack(side="left", padx=5)
        
        # Tabla de ventas
        self.create_table(left_frame)
        
        # Total
        self.total_label = tk.Label(left_frame, text="Total Ventas: $0.00", 
                                   font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#e74c3c")
        self.total_label.pack(pady=10)
        
        # Frame de estadísticas
        stats_frame = tk.LabelFrame(left_frame, text="Estadísticas del Período", 
                                   font=("Arial", 12, "bold"), bg="#ecf0f1", fg="#2c3e50")
        stats_frame.pack(fill="x", pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=6, width=50, font=("Arial", 9))
        self.stats_text.pack(padx=10, pady=10)
        
        # Columna derecha - Gráficas
        self.right_frame = tk.Frame(main_frame, bg="#ecf0f1", width=400)
        self.right_frame.pack(side="right", fill="both", padx=(20, 0))
        self.right_frame.pack_propagate(False)
        
        # Placeholder para gráficas
        graph_label = tk.Label(self.right_frame, text="Gráficas aparecerán aquí", 
                              font=("Arial", 12), bg="#ecf0f1", fg="#7f8c8d")
        graph_label.pack(expand=True)
    
    def create_table(self, parent):
        # Tabla de ventas
        columns = ("ID", "Fecha/Hora", "Cliente ID", "Total", "Empleado")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Fecha/Hora":
                self.tree.column(col, width=150)
            else:
                self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame contenedor para tabla y scrollbar
        table_frame = tk.Frame(parent, bg="#ecf0f1")
        table_frame.pack(fill="both", expand=True, pady=10)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def consultar_hoy(self):
        hoy = datetime.now().date()
        self.consultar_por_fechas(hoy, hoy, "Ventas de Hoy")
    
    def consultar_semana(self):
        hoy = datetime.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        self.consultar_por_fechas(inicio_semana, fin_semana, "Ventas de Esta Semana")
    
    def consultar_mes(self):
        hoy = datetime.now().date()
        inicio_mes = hoy.replace(day=1)
        if hoy.month == 12:
            fin_mes = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fin_mes = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)
        self.consultar_por_fechas(inicio_mes, fin_mes, "Ventas de Este Mes")
    
    def consultar_año(self):
        hoy = datetime.now().date()
        inicio_año = hoy.replace(month=1, day=1)
        fin_año = hoy.replace(month=12, day=31)
        self.consultar_por_fechas(inicio_año, fin_año, "Ventas de Este Año")
    
    def consultar_periodo(self):
        inicio = self.fecha_inicio.get_date()
        fin = self.fecha_fin.get_date()
        
        if inicio > fin:
            messagebox.showerror("Error", "La fecha de inicio no puede ser mayor que la fecha final")
            return
        
        periodo_texto = f"Período del {inicio.strftime('%d/%m/%Y')} al {fin.strftime('%d/%m/%Y')}"
        self.consultar_por_fechas(inicio, fin, periodo_texto)
    
    def consultar_por_fechas(self, fecha_inicio, fecha_fin, titulo):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Obtener ventas del período usando el DAO
            ventas = self.dao_ventas.get_by_period(database, fecha_inicio, fecha_fin)
            total_sum = 0
            
            for venta in reversed(ventas):
                self.tree.insert("", "end", values=(
                    venta.id,
                    venta.fecha_venta,
                    venta.cliente_id or 'N/A',
                    f"${venta.total:.2f}",
                    venta.empleado_id
                ))
                total_sum += venta.total
            
            self.total_label.config(text=f"Total {titulo}: ${total_sum:.2f}")
            self.actualizar_estadisticas(ventas, titulo)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar ventas: {str(e)}")
    
    def actualizar_estadisticas(self, ventas, titulo):
        if not ventas:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"{titulo}\n\nNo hay ventas en este período.")
            return
        
        total_ventas = len(ventas)
        total_monto = sum(venta.total for venta in ventas)
        promedio_venta = total_monto / total_ventas
        venta_maxima = max(venta.total for venta in ventas)
        venta_minima = min(venta.total for venta in ventas)
        
        # Ventas por empleado
        ventas_por_empleado = defaultdict(int)
        for venta in ventas:
            ventas_por_empleado[venta.empleado_id] += 1
        
        mejor_empleado = max(ventas_por_empleado.items(), key=lambda x: x[1]) if ventas_por_empleado else ("N/A", 0)
        
        stats_text = f"""{titulo}
{'='*40}
Total de transacciones: {total_ventas}
Monto total: ${total_monto:.2f}
Promedio por venta: ${promedio_venta:.2f}
Venta máxima: ${venta_maxima:.2f}
Venta mínima: ${venta_minima:.2f}
Mejor empleado: {mejor_empleado[0]} ({mejor_empleado[1]} ventas)
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
    
    def load_ventas(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Obtener todas las ventas usando el DAO
            ventas = self.dao_ventas.get_all(database)
            total_sum = 0
            
            for venta in reversed(ventas):
                self.tree.insert("", "end", values=(
                    venta.id,
                    venta.fecha_venta,
                    venta.cliente_id or 'N/A',
                    f"${venta.total:.2f}",
                    venta.empleado_id
                ))
                total_sum += venta.total
            
            self.total_label.config(text=f"Total Ventas: ${total_sum:.2f}")
            self.actualizar_estadisticas(ventas, "Todas las Ventas")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar ventas: {str(e)}")
    
    def mostrar_grafica_mensual(self):
        try:
            # Limpiar frame derecho
            for widget in self.right_frame.winfo_children():
                widget.destroy()
            
            # Obtener datos para gráfica mensual
            ventas = self.dao_ventas.get_all(database)
            
            if not ventas:
                tk.Label(self.right_frame, text="No hay datos para mostrar", 
                         font=("Arial", 12), bg="#ecf0f1").pack(expand=True)
                return
            
            # Agrupar ventas por mes
            ventas_por_mes = defaultdict(float)
            
            for venta in ventas:
                try:
                    # `fecha_venta` ya es un objeto datetime
                    fecha = venta.fecha_venta
                    mes_año = fecha.strftime('%Y-%m')
                    ventas_por_mes[mes_año] += float(venta.total)  # 转换为 float
                except Exception as e:
                    print(f"Error procesando venta: {venta}, Error: {e}")
                    continue
        
            if not ventas_por_mes:
                tk.Label(self.right_frame, text="Error al procesar fechas", 
                         font=("Arial", 12), bg="#ecf0f1").pack(expand=True)
                return
            
            # Crear gráfica
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#ecf0f1')
            
            meses = sorted(ventas_por_mes.keys())
            valores = [ventas_por_mes[mes] for mes in meses]
            
            # Convertir meses a formato más legible
            meses_legibles = []
            for mes in meses:
                fecha = datetime.strptime(mes, '%Y-%m')
                meses_legibles.append(fecha.strftime('%b %Y'))
            
            bars = ax.bar(meses_legibles, valores, color='#3498db', alpha=0.7)
            
            # Personalizar gráfica
            ax.set_title('Ventas Mensuales', fontsize=14, fontweight='bold')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Ventas ($)')
            ax.grid(axis='y', alpha=0.3)
            
            # Rotar etiquetas del eje x
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Agregar valores en las barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:.0f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            # Integrar gráfica en tkinter
            canvas = FigureCanvasTkAgg(fig, self.right_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráfica: {str(e)}")
    
    def export_ventas(self):
        try:
            os.makedirs("reportes", exist_ok=True)
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            reporte_path = f"reportes/ventas_{fecha_str}.txt"
            
            # Obtener datos actuales de la tabla
            items = self.tree.get_children()
            if not items:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            with open(reporte_path, "w", encoding="utf-8") as f:
                f.write("REPORTE DE VENTAS\n")
                f.write("=" * 80 + "\n")
                f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de transacciones: {len(items)}\n")
                
                # Calcular total de las ventas mostradas
                total_mostrado = 0
                for item in items:
                    valores = self.tree.item(item)['values']
                    total_str = valores[3].replace('$', '')
                    total_mostrado += float(total_str)
                
                f.write(f"Total de ventas mostradas: ${total_mostrado:.2f}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"{'ID':<5} {'Fecha/Hora':<20} {'Cliente':<10} {'Total':<12} {'Empleado':<10}\n")
                f.write("-" * 80 + "\n")
                
                for item in items:
                    valores = self.tree.item(item)['values']
                    f.write(f"{valores[0]:<5} {valores[1]:<20} "
                           f"{valores[2]:<10} {valores[3]:<12} {valores[4]:<10}\n")
            
            messagebox.showinfo("Exportación Exitosa", f"Reporte guardado en: {reporte_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
class OrdenFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ecf0f1")
        self.controller = controller
        self.dao_orden = DaoOrden(database)  # Asegúrate de que DaoOrden tenga métodos para interactuar con la tabla 'orden'

        # Título
        tk.Label(self, text="Detalles de Órdenes", 
                 font=("Arial", 18, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=20)

        # Botón para recargar datos
        tk.Button(self, text="Cargar Órdenes", command=self.load_ordenes,
                  bg="#3498db", fg="white", font=("Arial", 12), padx=20).pack(pady=10)

        # Tabla de órdenes
        columns = ("ID", "Cliente ID", "Detalle", "Fecha")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col == "Detalle" else 100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Botón para ver detalles
        tk.Button(self, text="Ver Detalles", command=self.ver_detalle,
                  bg="#27ae60", fg="white", font=("Arial", 12), padx=20).pack(pady=10)

    def load_ordenes(self):
        """Cargar órdenes desde la base de datos"""
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        try:
            # Obtener órdenes desde la base de datos
            ordenes = self.dao_orden.get_all_ordenes()  # Método que debes implementar en DaoOrden
            for orden in ordenes:
                self.tree.insert("", "end", values=(orden.id, orden.fecha, orden.detalles, orden.cliente_id))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar órdenes: {str(e)}")

    def ver_detalle(self):
        """Abrir ventana con detalles de la orden seleccionada"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una orden para ver los detalles")
            return
        
        item = selected_item[0]
        values = self.tree.item(item, "values")
        detalle = values[2]  # Columna de detalles

        # Crear ventana de detalles
        detalle_window = tk.Toplevel(self)
        detalle_window.title("Detalles de la Orden")
        detalle_window.geometry("500x400")
        detalle_window.resizable(False, False)
        detalle_window.configure(bg="#ecf0f1")

        # Mostrar detalles
        tk.Label(detalle_window, text="Detalles de la Orden", 
                 font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=20)
        
        detalle_text = tk.Text(detalle_window, wrap="word", font=("Arial", 12), bg="#ffffff", fg="#2c3e50")
        detalle_text.insert("1.0", detalle)
        detalle_text.config(state="disabled")  # Hacer que el texto sea de solo lectura
        detalle_text.pack(padx=20, pady=10, fill="both", expand=True)

        # Botón para cerrar la ventana
        tk.Button(detalle_window, text="Cerrar", command=detalle_window.destroy,
                  bg="#e74c3c", fg="white", font=("Arial", 12), padx=20).pack(pady=10)
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.dao = DaoEmpleado()
        self.root.title("Inicio de Sesión - Sistema de Gestión")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
        
        self.root.configure(bg="#2c3e50")
        
        # Título
        tk.Label(self.root, text="Sistema de Gestión", 
                font=("Arial", 24, "bold"), bg="#2c3e50", fg="white").pack(pady=30)
        
        # Formulario de login
        form_frame = tk.Frame(self.root, bg="#34495e", relief="raised", bd=2)
        form_frame.pack(pady=30, padx=50, fill="x")
        
        tk.Label(form_frame, text="Iniciar Sesión", 
                font=("Arial", 16, "bold"), bg="#34495e", fg="white").pack(pady=20)
        
        tk.Label(form_frame, text="Nombre de Usuario:", 
                font=("Arial", 12), bg="#34495e", fg="white").pack(pady=5)
        
        self.nombre_entry = tk.Entry(form_frame, font=("Arial", 12), width=25, justify="center")
        self.nombre_entry.pack(pady=10)
        self.nombre_entry.focus()
        
        # Mensaje de estado
        self.msg_label = tk.Label(form_frame, text="", 
                                 font=("Arial", 10), bg="#34495e", fg="#e74c3c")
        self.msg_label.pack(pady=5)
        
        # Botones
        button_frame = tk.Frame(form_frame, bg="#34495e")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Ingresar", command=self.login,
                 bg="#27ae60", fg="white", font=("Arial", 12, "bold"), 
                 padx=20, pady=5).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Crear Usuario", command=self.crear_empleado,
                 bg="#3498db", fg="white", font=("Arial", 12, "bold"), 
                 padx=20, pady=5).pack(side="left", padx=5)
        tk.Button(button_frame, text="Salir", command=self.root.quit,
                 bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), 
                 padx=20, pady=5).pack(side="left", padx=5)
        
        # Bind Enter key
        self.nombre_entry.bind("<Return>", lambda event: self.login())
        
        # Información adicional
        tk.Label(self.root, text="Usuario por defecto: admin", 
                font=("Arial", 10, "italic"), bg="#2c3e50", fg="#bdc3c7").pack(pady=10)

    def login(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            self.msg_label.config(text="Por favor ingrese un nombre de usuario")
            return
        
        empleado = self.dao.get_by_nombre(database, nombre)
        if empleado:
            self.root.destroy()
            main_root = tk.Tk()
            MainApp(main_root, empleado_id=empleado[0], empleado_nombre=empleado[1])  # Cambia empleado[0] a ID y empleado[1] a nombre
            main_root.mainloop()
        else:
            self.msg_label.config(text="Usuario no encontrado")

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

# Función principal
def main():
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()