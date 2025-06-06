import tkinter as tk
from tkinter import ttk, messagebox
from data.dao.dao_productos import DaoProducto, DaoCliente
from collections import defaultdict
from data.database import database
from datetime import datetime


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Cliente")
        self.root.geometry("400x300")
        self.dao_cliente = DaoCliente(database)
        
        self._setup_form()

    def _setup_form(self):
        """Configurar formulario de login"""
        # Título
        tk.Label(self.root, text="Sistema de Ventas", 
                font=("Arial", 18, "bold")).pack(pady=30)
        
        # Formulario
        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=20)

        tk.Label(form_frame, text="Nombre del Cliente:", 
                font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.nombre_entry = tk.Entry(form_frame, font=("Arial", 12), width=20)
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=10)
        self.nombre_entry.focus()

        # Mensaje de estado
        self.msg_label = tk.Label(self.root, text="", fg="red", font=("Arial", 10))
        self.msg_label.pack(pady=5)

        # Botones
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Entrar", command=self.login,
                 font=("Arial", 12), bg="#4CAF50", fg="white", padx=20).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Crear Cliente", command=self.crear_cliente,
                 font=("Arial", 12), bg="#2196F3", fg="white", padx=20).pack(side="left", padx=5)

        # Bind Enter key
        self.nombre_entry.bind("<Return>", lambda e: self.login())

    def login(self):
        """Proceso de login"""
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            self.msg_label.config(text="Ingrese un nombre.")
            return

        cliente = self.dao_cliente.get_by_nombre(nombre)
        if cliente:
            self._abrir_app_principal(cliente)
        else:
            self.msg_label.config(text="Cliente no encontrado.")

    def crear_cliente(self):
        """Crear un nuevo cliente"""
        popup = tk.Toplevel(self.root)
        popup.title("Crear Nuevo Cliente")
        popup.geometry("350x200")
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="Nombre:", font=("Arial", 12)).pack(pady=10)
        nombre_entry = tk.Entry(popup, font=("Arial", 12), width=25)
        nombre_entry.pack(pady=5)

        tk.Label(popup, text="Contacto:", font=("Arial", 12)).pack(pady=5)
        contacto_entry = tk.Entry(popup, font=("Arial", 12), width=25)
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
                messagebox.showinfo("Éxito", f"Cliente creado con ID: {cliente_id}")
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el cliente: {str(e)}")

        tk.Button(popup, text="Confirmar", command=confirmar, 
                 bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)

    def _abrir_app_principal(self, cliente):
        """Abrir aplicación principal"""
        self.root.destroy()
        main_root = tk.Tk()
        MainApp(main_root, cliente_id=cliente[0], cliente_nombre=cliente[1])
        main_root.mainloop()


class MainApp:
    def __init__(self, root, cliente_id=None, cliente_nombre=None):
        self.root = root
        self.root.title("Sistema de Ventas")
        self.root.geometry("1000x900")
        self.cliente_id = cliente_id
        self.cliente_nombre = cliente_nombre

        self._setup_navigation()
        self._setup_content()
        self.show_inicio()

    def _setup_navigation(self):
        """Configurar barra de navegación"""
        nav_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        nav_frame.pack(side="top", fill="x")
        nav_frame.pack_propagate(False)

        tk.Button(nav_frame, text="Inicio", command=self.show_inicio, 
                 bg="#3498db", fg="white", font=("Arial", 12), 
                 padx=20).pack(side="left", padx=10, pady=15)
        
        tk.Button(nav_frame, text="Realizar Pedido", command=self.show_cobrar, 
                 bg="#e74c3c", fg="white", font=("Arial", 12), 
                 padx=20).pack(side="left", padx=10, pady=15)
        
        tk.Label(nav_frame, text=f"Cliente: {self.cliente_nombre} (ID: {self.cliente_id})", 
                bg="#2c3e50", fg="white", font=("Arial", 11)).pack(side="right", padx=20, pady=15)

    def _setup_content(self):
        """Configurar área de contenido"""
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True)

        self.frames = {}
        for frame_class in [InicioFrame, CobrarFrame]:
            name = frame_class.__name__
            frame = frame_class(self.content_frame, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def show_inicio(self):
        """Mostrar la página de inicio"""
        self.frames["InicioFrame"].tkraise()

    def show_cobrar(self):
        """Mostrar la página de pedidos"""
        self.frames["CobrarFrame"].tkraise()


class InicioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ecf0f1")
        self.controller = controller
        
        # Título de bienvenida
        tk.Label(self, text="Bienvenido al Sistema de Ventas", 
                font=("Arial", 24, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=50)
        
        # Información del cliente
        info_frame = tk.Frame(self, bg="#ffffff", relief="solid", bd=2)
        info_frame.pack(pady=30, padx=50, fill="x")
        
        tk.Label(info_frame, text="Información del Cliente", 
                font=("Arial", 16, "bold"), bg="#ffffff", fg="#2c3e50").pack(pady=15)
        
        tk.Label(info_frame, text=f"Nombre: {controller.cliente_nombre}", 
                font=("Arial", 14), bg="#ffffff").pack(pady=5)
        
        tk.Label(info_frame, text=f"ID: {controller.cliente_id}", 
                font=("Arial", 14), bg="#ffffff").pack(pady=5)
        
        # Instrucciones
        tk.Label(self, text="Haga clic en 'Realizar Pedido' para comenzar", 
                font=("Arial", 12, "italic"), bg="#ecf0f1", fg="#7f8c8d").pack(pady=30)


class CobrarFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ecf0f1")
        self.controller = controller
        self.dao = DaoProducto()
        self.cart_items = defaultdict(lambda: {"precio": 0, "cantidad": 0, "subtotal": 0, "producto_id": None})
        
        self.setup_ui()
        self.refresh_products()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Título
        tk.Label(self, text="Realizar Pedido", 
                font=("Arial", 18, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=10)

        # Frame principal
        main_frame = tk.Frame(self, bg="#ecf0f1")
        main_frame.pack(fill="both", expand=True, padx=20)
        
        self.setup_products_section(main_frame)
        self.setup_cart_section(main_frame)

    def setup_products_section(self, parent):
        """Configura la sección de productos"""
        # Productos disponibles
        left_frame = tk.Frame(parent, bg="#ffffff", relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Productos Disponibles", 
                font=("Arial", 14, "bold"), bg="#ffffff", fg="#2c3e50").pack(pady=10)
        
        # Scrollable frame para productos
        canvas_frame = tk.Frame(left_frame, bg="#ffffff")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#ffffff")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.products_frame = tk.Frame(self.canvas, bg="#ffffff")
        
        self.products_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.products_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_cart_section(self, parent):
        """Configura la sección del carrito"""
        right_frame = tk.Frame(parent, bg="#ffffff", relief="solid", bd=1, width=400)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)
        
        tk.Label(right_frame, text="Carrito de Pedido", 
                font=("Arial", 14, "bold"), bg="#ffffff", fg="#2c3e50").pack(pady=10)
        
        # Tabla del carrito
        cart_frame = tk.Frame(right_frame, bg="#ffffff")
        cart_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        columns = ("Producto", "Cantidad", "Precio", "Subtotal")
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show="headings", height=12)
        
        # Configurar columnas
        widths = {"Producto": 120, "Cantidad": 60, "Precio": 70, "Subtotal": 80}
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=widths.get(col, 80), anchor="center")
        
        scrollbar_cart = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scrollbar_cart.set)
        
        self.cart_tree.pack(side="left", fill="both", expand=True)
        scrollbar_cart.pack(side="right", fill="y")
        
        # Total
        self.total_label = tk.Label(right_frame, text="Total: $0.00", 
                                   font=("Arial", 16, "bold"), bg="#ffffff", fg="#e74c3c")
        self.total_label.pack(pady=15)
        
        # Botones
        self.setup_cart_buttons(right_frame)

    def setup_cart_buttons(self, parent):
        """Configura los botones del carrito"""
        buttons_frame = tk.Frame(parent, bg="#ffffff")
        buttons_frame.pack(pady=10, padx=10, fill="x")
        
        # Botones de control
        tk.Button(buttons_frame, text="+ Cantidad", command=self.increase_quantity,
                 bg="#2ecc71", fg="white", font=("Arial", 10)).pack(fill="x", pady=2)
        
        tk.Button(buttons_frame, text="- Cantidad", command=self.decrease_quantity,
                 bg="#f39c12", fg="white", font=("Arial", 10)).pack(fill="x", pady=2)
        
        tk.Button(buttons_frame, text="Quitar Producto", command=self.remove_from_cart,
                 bg="#e74c3c", fg="white", font=("Arial", 10)).pack(fill="x", pady=2)
        
        tk.Button(buttons_frame, text="Vaciar Carrito", command=self.clear_cart,
                 bg="#95a5a6", fg="white", font=("Arial", 10)).pack(fill="x", pady=10)
        
        # Botón principal
        tk.Button(buttons_frame, text="FINALIZAR PEDIDO", command=self.finalizar_pedido,
                 bg="#8e44ad", fg="white", font=("Arial", 12, "bold"), 
                 height=2).pack(fill="x", pady=10)

    def refresh_products(self):
        """Actualiza la lista de productos"""
        try:
            # Limpiar productos existentes
            for widget in self.products_frame.winfo_children():
                widget.destroy()
            
            # Obtener productos
            productos = self.dao.get_all(database)
            self.display_products(productos)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")

    def display_products(self, productos):
        """Muestra los productos en la interfaz"""
        productos_por_fila = 3
        
        for index, producto in enumerate(productos):
            if index % productos_por_fila == 0:
                row_frame = tk.Frame(self.products_frame, bg="#ffffff")
                row_frame.pack(fill="x", pady=5, padx=5)
            
            # Color según stock
            if producto.cantidad_stock <= 0:
                color, estado = "#e74c3c", "SIN STOCK"
            elif producto.cantidad_stock <= 5:
                color, estado = "#f39c12", f"Stock: {producto.cantidad_stock}"
            else:
                color, estado = "#27ae60", f"Stock: {producto.cantidad_stock}"
            
            btn = tk.Button(
                row_frame,
                text=f"{producto.nombre}\n${producto.precio:.2f}\n{estado}",
                command=lambda p=producto: self.add_to_cart(p),
                width=20, height=4, bg=color, fg="white",
                font=("Arial", 9, "bold"), relief="raised", bd=2,
                state="normal" if producto.cantidad_stock > 0 else "disabled"
            )
            btn.pack(side="left", padx=5)

    def add_to_cart(self, producto):
        """Agrega un producto al carrito"""
        try:
            if producto.cantidad_stock <= 0:
                messagebox.showwarning("Sin Stock", f"El producto '{producto.nombre}' no tiene stock.")
                return
            
            if self.cart_items[producto.nombre]["cantidad"] >= producto.cantidad_stock:
                messagebox.showwarning("Sin Stock", f"No hay más stock para '{producto.nombre}'.")
                return
            
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
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = selected[0]
        values = self.cart_tree.item(item, "values")
        nombre = values[0]
        
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
            messagebox.showwarning("Sin Stock", f"No hay más stock para '{nombre}'.")

    def decrease_quantity(self):
        """Disminuye la cantidad del producto seleccionado"""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
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

    def refresh_cart(self):
        """Actualiza la vista del carrito"""
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
        """Remueve un producto del carrito"""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = selected[0]
        values = self.cart_tree.item(item, "values")
        nombre = values[0]
        
        if messagebox.askyesno("Confirmar", f"¿Quitar '{nombre}' del carrito?"):
            self.cart_items[nombre] = {"precio": 0, "cantidad": 0, "subtotal": 0, "producto_id": None}
            self.refresh_cart()

    def clear_cart(self):
        """Vacía el carrito"""
        if not any(info["cantidad"] > 0 for info in self.cart_items.values()):
            messagebox.showinfo("Información", "El carrito ya está vacío")
            return
            
        if messagebox.askyesno("Confirmar", "¿Vaciar todo el carrito?"):
            self.cart_items.clear()
            self.refresh_cart()

    def finalizar_pedido(self):
        """Finaliza el pedido, guarda en la base de datos y exporta el detalle como texto"""
        try:
            # Validar que hay productos en el carrito
            if not any(info["cantidad"] > 0 for info in self.cart_items.values()):
                messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito")
                return

            # Calcular total
            total = sum(info["subtotal"] for info in self.cart_items.values() if info["cantidad"] > 0)
            
            # Crear el detalle del pedido
            productos_texto = []
            for nombre, info in self.cart_items.items():
                if info["cantidad"] > 0:
                    productos_texto.append(f"{nombre}: {info['cantidad']} x ${info['precio']:.2f} = ${info['subtotal']:.2f}")
            
            detalle_pedido = "\n".join(productos_texto)
            detalle_completo = (
                f"Cliente: {self.controller.cliente_nombre} (ID: {self.controller.cliente_id})\n"
                f"Productos:\n{detalle_pedido}\n"
                f"Total: ${total:.2f}\n"
                f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # Confirmar pedido
            if not messagebox.askyesno("Confirmar Pedido", f"¿Confirmar pedido?\n\n{detalle_completo}"):
                return

            # Insertar en la tabla 'orden'
            cursor = database.cursor()
            query = """
                INSERT INTO orden (cliente_id, detalles,fecha)
                VALUES (%s, %s, NOW())
            """
            cursor.execute(query, (self.controller.cliente_id, detalle_completo))
            database.commit()
            cursor.close()

            # Mostrar confirmación
            messagebox.showinfo("Pedido Exitoso", 
                            f"¡Pedido registrado correctamente!\n\nTotal: ${total:.2f}\n"
                            f"El detalle se ha exportado como archivo de texto.")

            # Limpiar carrito
            self.clear_cart()
            self.refresh_products()

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar pedido: {str(e)}")


# Punto de entrada
if __name__ == "__main__":
    login_root = tk.Tk()
    LoginWindow(login_root)
    login_root.mainloop()