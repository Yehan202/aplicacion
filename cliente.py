import tkinter as tk
from tkinter import ttk, messagebox
from data.dao.dao_productos import DaoProducto, DaoCliente, DaoVentas, DaoTicket
from collections import defaultdict
from data.database import database
from datetime import datetime


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Cliente")
        self.root.geometry("700x500")
        self.dao_cliente = DaoCliente(database)

        self._setup_background()
        self._setup_datetime()
        self._setup_logo()
        self._setup_form()
        self._setup_buttons()

    def _setup_background(self):
        """Configurar imagen de fondo"""
        bg_photo = None  # Puedes agregar una imagen de fondo si lo deseas
        if bg_photo:
            tk.Label(self.root, image=bg_photo).place(relwidth=1, relheight=1)
            self.bg_photo = bg_photo

    def _setup_datetime(self):
        """Configurar reloj"""
        self.date_time_label = tk.Label(
            self.root, text="", font=("Arial", 20, "bold"),
            bg="#ffffff", fg="#000000"
        )
        self.date_time_label.pack(anchor="nw", padx=10, pady=5)
        self.update_time_id = None
        self._update_datetime()

    def _update_datetime(self):
        """Actualizar fecha y hora"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_time_label.config(text=now)
        self.update_time_id = self.root.after(1000, self._update_datetime)

    def _setup_logo(self):
        """Configurar logo"""
        logo_photo = None  # Puedes agregar un logo si lo deseas
        if logo_photo:
            tk.Label(self.root, image=logo_photo).pack(pady=20)
            self.logo_photo = logo_photo
        else:
            tk.Label(self.root, text="(Logo no disponible)",
                     font=("Arial", 12, "italic")).pack(pady=20)

    def _setup_form(self):
        """Configurar formulario"""
        form_frame = tk.Frame(self.root, bg="#ffffff")
        form_frame.pack(pady=20)

        self.nombre_entry = self._create_label_entry(
            form_frame, "Nombre del Cliente:", 0
        )
        self.nombre_entry.focus()

        self.msg_label = tk.Label(
            self.root, text="", fg="black", font=("Calibri", 10, "italic"),
            anchor="center", bg="#ffffff"
        )
        self.msg_label.pack(pady=10, anchor="center")

    def _setup_buttons(self):
        """Configurar botones"""
        button_frame = tk.Frame(self.root, bg="#ffffff")
        button_frame.pack(pady=10)

        buttons = [
            ("Entrar", self.login),
            ("Crear Nuevo Cliente", self.crear_cliente)
        ]

        for text, command in buttons:
            tk.Button(
                button_frame, text=text, command=command,
                font=("Arial", 15, "bold"), relief="groove", bd=3
            ).pack(side="left", padx=5, pady=5)

        self.nombre_entry.bind("<Return>", lambda e: self.login())

    def _create_label_entry(self, parent, label_text, row):
        """Crear par label-entry"""
        tk.Label(parent, text=label_text, font=("Arial", 12, "bold")).grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        entry = tk.Entry(parent, font=("Arial", 12))
        entry.grid(row=row, column=1, padx=10, pady=5)
        return entry

    def login(self):
        """Proceso de login"""
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            self.msg_label.config(text="Ingrese un nombre.")
            return

        cliente = self.dao_cliente.get_by_nombre(nombre)
        if cliente:
            self._cancel_datetime_update()
            self._abrir_app_principal(cliente)
        else:
            self.msg_label.config(text="Cliente no encontrado.")

    def crear_cliente(self):
        """Crear un nuevo cliente"""
        popup = tk.Toplevel(self.root)
        popup.title("Crear Nuevo Cliente")
        popup.geometry("400x250")
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="Nombre del Cliente:", font=("Arial", 12)).pack(pady=10)
        nombre_entry = tk.Entry(popup, font=("Arial", 12))
        nombre_entry.pack(pady=5)

        tk.Label(popup, text="Contacto del Cliente:", font=("Arial", 12)).pack(pady=10)
        contacto_entry = tk.Entry(popup, font=("Arial", 12))
        contacto_entry.pack(pady=5)

        def confirmar():
            nombre = nombre_entry.get().strip()
            contacto = contacto_entry.get().strip()

            if not nombre or not contacto:
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            try:
                fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cliente_id = self.dao_cliente.insert(nombre, contacto, fecha_registro)
                messagebox.showinfo("Éxito", f"Cliente creado con éxito. ID: {cliente_id}")
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el cliente: {str(e)}")

        tk.Button(popup, text="Confirmar", command=confirmar, bg="#4a90e2", fg="white", font=("Arial", 12)).pack(pady=20)

    def _abrir_app_principal(self, cliente):
        """Abrir aplicación principal"""
        self.root.destroy()
        main_root = tk.Tk()
        MainApp(main_root, cliente_id=cliente[0], cliente_nombre=cliente[1])
        main_root.mainloop()

    def _cancel_datetime_update(self):
        """Cancelar actualización de hora"""
        if self.update_time_id:
            self.root.after_cancel(self.update_time_id)


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
        tk.Button(nav_frame, text="Compra", command=self.show_cobrar, bg="#4a90e2", fg="white").pack(side="left", padx=5, pady=5)

        # 主内容区
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True)

        # 初始化各个页面Frame
        self.frames = {}
        for F in (InicioFrame, CobrarFrame):
            page_name = F.__name__
            frame = F(parent=self.content_frame, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_inicio()

    


    def __init__(self, root, cliente_id=None, cliente_nombre=None):
        self.root = root
        self.root.title("Sistema de Ventas")
        self.root.geometry("1200x800")
        self.cliente_id = cliente_id
        self.cliente_nombre = cliente_nombre

        self._setup_navigation()
        self._setup_content()
        self.show_inicio()

    def _setup_navigation(self):
        """Configurar barra de navegación"""
        nav_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        nav_frame.pack(side="top", fill="x")
        nav_frame.grid_propagate(False)

        tk.Label(
            nav_frame,
            text=f"Cliente: {self.cliente_nombre} | ID: {self.cliente_id}",
            bg="#4a90e2", fg="white", font=("Arial", 10, "italic")
        ).pack(side="right", padx=10)

    def _setup_content(self):
        """Configurar área de contenido"""
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True)

        self.frames = {}
        for frame_class in [InicioFrame]:
            name = frame_class.__name__
            frame = frame_class(self.content_frame, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_inicio(self):
        self.frames["InicioFrame"].tkraise()


class InicioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Bienvenido al Sistema de Ventas", font=("Arial", 18)).pack(pady=20)
class CobrarFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ecf0f1")
        self.controller = controller
        self.dao = DaoProducto()
        self.dao_ventas = DaoVentas()
        self.dao_ticket = DaoTicket()
        self.cart_items = defaultdict(lambda: {"precio": 0, "cantidad": 0, "subtotal": 0, "producto_id": None})
        
        self.setup_ui()
        self.refresh_products()

    def setup_ui(self):
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

    def lighten_color(self, color):
        """Aclara un color para el efecto hover"""
        color_map = {
            "#27ae60": "#2ecc71",
            "#f39c12": "#f1c40f",
            "#c0392b": "#e74c3c"
        }
        return color_map.get(color, color)

    def filter_products(self, event=None):
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

    def realizar_cobro(self):
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

    def open_payment_window(self, total, cliente_id, empleado_id):
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


# Punto de entrada
if __name__ == "__main__":
    login_root = tk.Tk()
    LoginWindow(login_root)
    login_root.mainloop()