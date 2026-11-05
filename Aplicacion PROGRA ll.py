from datetime import date, datetime
from pathlib import Path
import json
import os
import tkinter as tk

import customtkinter as ctk
import yaml
from PIL import Image, ImageOps, ImageTk
from tkinter import ttk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --- Rutas y constantes ---
BASE_DIR = Path(__file__).resolve().parent
RUTA_CUENTAS = BASE_DIR / "Cuentas.json"
RUTA_DATOS = BASE_DIR / "Hoja_datos.json"
RUTA_FACTURA = BASE_DIR / "nuevo.txt"
RUTA_IMAGEN = BASE_DIR / "IMAGEN DE APLICACION.jpg"

# Paleta reducida: escala clara de fondos y un solo color de acción.
COLOR_FONDO = "#eef7fa"
COLOR_TARJETA = "#eef7fa"
COLOR_SUAVE = "#dcebf2"
COLOR_BORDE = "#b9d5e1"
COLOR_PRIMARIO = "#2d7d9a"
COLOR_PRIMARIO_HOVER = "#26687f"
COLOR_TEXTO = "#20313a"
COLOR_SECUNDARIO = "#5f737d"
COLOR_PELIGRO = "#b04a45"
COLOR_EXITO = "#2f7d5c"

FUENTE = "Arial"

SEXOS = ["Hembra", "Macho"]
RAZAS = ["Holstein", "Jersey", "Brahman", "Angus", "Hereford", "Nelore", "Gyr", "Simmental", "Normando", "Cebú", "Mestizo", "Otra"]
PROPOSITOS = ["Leche", "Carne", "Doble propósito"]
ORIGENES = ["Criado en la granja", "Comprado", "Donado", "Otro"]
ESTADOS = ["Activo", "Vendido", "Muerto"]
CAMPOS_FILTRO = [("sexo", "Sexo"), ("raza", "Raza"), ("origen", "Origen"), ("proposito", "Propósito"), ("estado", "Estado"), ("color", "Color")]

_imagen_base = None

# --- Ayudas de interfaz ---
def etiqueta(padre, texto, tam=14, color=COLOR_TEXTO, negrita=False, **kw):
    fuente = (FUENTE, tam, "bold") if negrita else (FUENTE, tam)
    return ctk.CTkLabel(padre, text=texto, font=fuente, text_color=color, **kw)

def entrada(padre, marcador="", alto=44, **kw):
    return ctk.CTkEntry(padre, height=alto, font=(FUENTE, 14), placeholder_text=marcador, corner_radius=10, fg_color="white", border_color=COLOR_BORDE, border_width=1, **kw)

def boton(padre, texto, comando, tipo="primario", ancho=170, alto=44, tam=14, **kw):
    estilos = {
        "primario": {"fg_color": COLOR_PRIMARIO, "hover_color": COLOR_PRIMARIO_HOVER, "text_color": "white", "border_width": 0},
        "suave": {"fg_color": COLOR_SUAVE, "hover_color": COLOR_BORDE, "text_color": COLOR_TEXTO, "border_width": 1, "border_color": COLOR_BORDE},
        "peligro": {"fg_color": COLOR_PELIGRO, "hover_color": "#933c38", "text_color": "white", "border_width": 0},
        "texto": {"fg_color": "transparent", "hover_color": COLOR_SUAVE, "text_color": COLOR_SECUNDARIO, "border_width": 0},
    }
    return ctk.CTkButton(padre, text=texto, command=comando, width=ancho, height=alto, font=(FUENTE, tam), corner_radius=10, **estilos[tipo], **kw)

def tarjeta(padre, **kw):
    return ctk.CTkFrame(padre, fg_color=COLOR_TARJETA, corner_radius=22, border_width=1, border_color=COLOR_BORDE, **kw)

def fijar_ancho(tarjeta, ancho):
    """Evita que la tarjeta se encoja al ancho de su contenido (altura sigue automatica)."""
    ctk.CTkFrame(tarjeta, width=ancho, height=1, fg_color="transparent").pack()

def ajustar_ventana(ventana, ancho=1360, alto=840):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    ancho = min(ancho, int(pantalla_ancho * 0.94))
    alto = min(alto, int(pantalla_alto * 0.92))
    x = max((pantalla_ancho - ancho) // 2, 0)
    y = max((pantalla_alto - alto) // 2, 0)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    ventana.minsize(min(1040, ancho), min(660, alto))
    ventana.resizable(True, True)
    ventana.configure(fg_color=COLOR_FONDO)

def cargar_imagen():
    global _imagen_base
    if _imagen_base is None:
        try:
            with Image.open(RUTA_IMAGEN) as archivo:
                _imagen_base = archivo.convert("RGB")
        except Exception:
            _imagen_base = False
    return _imagen_base or None

def poner_fondo(ventana):
    """Pone la imagen de fondo y la ajusta cuando la ventana cambia de tamaño."""
    imagen = cargar_imagen()
    if imagen is None:
        return None

    fondo = ctk.CTkLabel(ventana, text="", fg_color="transparent")
    fondo.place(x=0, y=0, relwidth=1, relheight=1)
    fondo.lower()
    estado = {"tam": (0, 0), "job": None}

    def ajustar():
        estado["job"] = None
        try:
            if not ventana.winfo_exists():
                return
            ancho = max(ventana.winfo_width(), 480)
            alto = max(ventana.winfo_height(), 360)
        except Exception:
            return
        if abs(ancho - estado["tam"][0]) < 40 and abs(alto - estado["tam"][1]) < 40:
            return
        estado["tam"] = (ancho, alto)
        escala = ctk.ScalingTracker.get_widget_scaling(fondo) or 1.0
        recorte = ImageOps.fit(imagen, (ancho, alto), Image.Resampling.LANCZOS)
        foto = ctk.CTkImage(light_image=recorte, dark_image=recorte, size=(max(round(ancho / escala), 1), max(round(alto / escala), 1)))
        fondo.configure(image=foto)
        fondo.image = foto

    def redimensionar(evento=None):
        if evento is not None and evento.widget is not ventana:
            return
        if estado["job"] is not None:
            try:
                ventana.after_cancel(estado["job"])
            except Exception:
                pass
        estado["job"] = ventana.after(140, ajustar)

    ventana.bind("<Configure>", redimensionar)
    ventana.after(20, ajustar)
    return fondo

def nueva_ventana(padre, titulo, ancho=1360, alto=840, fondo=True):
    ventana = ctk.CTkToplevel(padre)
    ventana.title(titulo)
    ajustar_ventana(ventana, ancho, alto)
    ventana.resizable(True, True)
    if fondo:
        poner_fondo(ventana)
    return ventana

def ventana_abierta(padre, atributo):
    """Evita abrir dos veces la misma ventana y trae al frente la existente."""
    ventana = getattr(padre, atributo, None)
    if ventana is not None:
        try:
            if ventana.winfo_exists():
                ventana.deiconify()
                ventana.lift()
                ventana.focus_force()
                return True
        except Exception:
            pass
        setattr(padre, atributo, None)
    return False

# --- Archivos y datos ---
def cargar_json(ruta, predeterminado):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            contenido = archivo.read().strip()
            if not contenido:
                return predeterminado
            return json.loads(contenido)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return predeterminado

def guardar_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

def cargar_usuarios():
    datos = cargar_json(RUTA_CUENTAS, {})
    return datos if isinstance(datos, dict) else {}

def guardar_usuarios(usuarios):
    guardar_json(RUTA_CUENTAS, usuarios)

def cargar_animales():
    datos = cargar_json(RUTA_DATOS, {"animales": []})
    if isinstance(datos, dict):
        animales = datos.get("animales", [])
        return animales if isinstance(animales, list) else []
    if isinstance(datos, list):
        return datos
    return []

def guardar_animales(animales):
    guardar_json(RUTA_DATOS, {"animales": animales})

def validar_fecha(texto):
    try:
        return datetime.strptime(str(texto).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def calcular_edad(fecha_nacimiento):
    nacimiento = validar_fecha(fecha_nacimiento)
    if nacimiento is None:
        return "Sin fecha"
    hoy = date.today()
    if nacimiento > hoy:
        return "Fecha futura"

    meses = (hoy.year - nacimiento.year) * 12 + (hoy.month - nacimiento.month)
    if hoy.day < nacimiento.day:
        meses -= 1
    meses = max(meses, 0)

    if meses == 0:
        return "Menos de 1 mes"

    anos, meses_restantes = divmod(meses, 12)
    texto_anos = "1 año" if anos == 1 else f"{anos} años"
    texto_meses = "1 mes" if meses_restantes == 1 else f"{meses_restantes} meses"

    if anos == 0:
        return texto_meses
    if meses_restantes == 0:
        return texto_anos
    return f"{texto_anos} y {texto_meses}"

def formatear_peso(peso):
    try:
        return f"{float(peso):.1f}"
    except (TypeError, ValueError):
        return "—"

def filtrar_animales(animales, filtros, texto=""):
    texto = str(texto).strip().lower()
    resultado = []

    for animal in animales:
        if texto:
            nombre = str(animal.get("nombre", "")).lower()
            identificacion = str(animal.get("identificacion", "")).lower()
            if texto not in nombre and texto not in identificacion:
                continue

        coincide = True
        for clave, valor in filtros.items():
            if valor is None:
                continue
            if str(animal.get(clave) or "").strip().lower() != str(valor).strip().lower():
                coincide = False
                break

        if coincide:
            resultado.append(animal)

    return resultado

def valores_categoria(animales, categoria):
    valores = {str(animal.get(categoria) or "").strip() for animal in animales}
    return sorted((valor for valor in valores if valor), key=str.lower)

def formatear_hoja(animal):
    def dato(clave, defecto="—"):
        valor = animal.get(clave, "")
        if valor is None:
            return defecto
        valor = str(valor).strip()
        return valor if valor else defecto

    lineas = [
        "HOJA TÉCNICA DEL BOVINO",
        "=" * 46,
        f"Identificación: {dato('identificacion')}",
        f"Nombre: {dato('nombre')}",
        f"Raza: {dato('raza')}",
        f"Sexo: {dato('sexo')}",
        f"Fecha de nacimiento: {dato('fecha_nacimiento')}  ({calcular_edad(animal.get('fecha_nacimiento'))})",
        f"Peso: {formatear_peso(animal.get('peso'))} kg",
        f"Color: {dato('color')}",
        f"Propósito: {dato('proposito')}",
        f"Origen: {dato('origen')}",
        f"Procedencia: {dato('procedencia')}",
        f"Fecha de ingreso: {dato('fecha_ingreso')}",
        f"Estado: {dato('estado')}",
        "",
        "Observaciones:",
        dato("observaciones"),
    ]
    return "\n".join(lineas)

# --- Inicio de sesión ---
def crear_ventana_login():
    root = ctk.CTk()
    root.title("Métodos Campesinos")
    ajustar_ventana(root, 1180, 760)
    poner_fondo(root)

    panel = tarjeta(root)
    panel.place(relx=0.5, rely=0.5, anchor="center")
    fijar_ancho(panel, 540)

    etiqueta(panel, "Métodos Campesinos", 28, COLOR_TEXTO, negrita=True).pack(pady=(52, 4))
    etiqueta(panel, "Control de ganado", 14, COLOR_SECUNDARIO).pack(pady=(0, 38))

    etiqueta(panel, "Usuario", 13, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=60)
    entry_usuario = entrada(panel, "Escribe tu usuario")
    entry_usuario.pack(fill="x", padx=60, pady=(6, 18))

    etiqueta(panel, "Contraseña", 13, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=60)
    entry_contrasena = entrada(panel, "Escribe tu contraseña", show="*")
    entry_contrasena.pack(fill="x", padx=60, pady=(6, 34))

    boton(panel, "Iniciar sesión", lambda: iniciar_sesion(root), "primario").pack(fill="x", padx=60)
    boton(panel, "Crear usuario", lambda: abrir_registro_cuenta(root), "suave").pack(fill="x", padx=60, pady=(12, 0))

    mensaje = etiqueta(panel, "", 13, COLOR_PELIGRO, wraplength=380)
    mensaje.pack(pady=(18, 28))

    root.entry_usuario = entry_usuario
    root.entry_contrasena = entry_contrasena
    root.mensaje_login = mensaje
    root.ventana_principal = None
    root.ventana_registro_cuenta = None

    entry_usuario.bind("<Return>", lambda event: iniciar_sesion(root))
    entry_contrasena.bind("<Return>", lambda event: iniciar_sesion(root))
    entry_usuario.focus_set()
    return root

def iniciar_sesion(root):
    usuario = root.entry_usuario.get().strip()
    contrasena = root.entry_contrasena.get()
    mensaje = root.mensaje_login

    if not usuario or not contrasena:
        mensaje.configure(text="Completa usuario y contraseña.", text_color=COLOR_PELIGRO)
        return

    usuarios = cargar_usuarios()

    if usuario in usuarios and usuarios[usuario] == contrasena:
        mensaje.configure(text="")
        abrir_menu_principal(root, usuario)
    elif usuario in usuarios:
        mensaje.configure(text="Contraseña incorrecta.", text_color=COLOR_PELIGRO)
    else:
        mensaje.configure(text="Usuario no encontrado.", text_color=COLOR_PELIGRO)

def abrir_registro_cuenta(root):
    if ventana_abierta(root, "ventana_registro_cuenta"):
        return

    ventana = nueva_ventana(root, "Crear usuario", 1040, 700)

    panel = tarjeta(ventana)
    panel.place(relx=0.5, rely=0.5, anchor="center")
    fijar_ancho(panel, 500)

    etiqueta(panel, "Crear usuario", 28, COLOR_TEXTO, negrita=True).pack(pady=(46, 4))
    etiqueta(panel, "Elige un nombre y una contraseña.", 13, COLOR_SECUNDARIO).pack(pady=(0, 34))

    etiqueta(panel, "Nuevo usuario", 13, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=60)
    entry_usuario = entrada(panel, "Nombre de usuario")
    entry_usuario.pack(fill="x", padx=60, pady=(6, 18))

    etiqueta(panel, "Contraseña", 13, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=60)
    entry_contrasena = entrada(panel, "Contraseña", show="*")
    entry_contrasena.pack(fill="x", padx=60, pady=(6, 26))

    mensaje = etiqueta(panel, "", 12, COLOR_PELIGRO, wraplength=380)
    mensaje.pack(pady=(0, 12))

    def cerrar():
        try:
            ventana.destroy()
        except Exception:
            pass
        root.ventana_registro_cuenta = None
        root.lift()
        root.focus_force()

    def guardar_y_cerrar():
        nombre_usuario = entry_usuario.get().strip()
        clave_usuario = entry_contrasena.get()

        if not nombre_usuario or not clave_usuario:
            mensaje.configure(text="Completa ambos campos.")
            return

        cuentas = cargar_usuarios()
        if nombre_usuario.lower() in (usuario.lower() for usuario in cuentas):
            mensaje.configure(text="Ese usuario ya existe. Elige otro.")
            return

        cuentas[nombre_usuario] = clave_usuario
        try:
            guardar_usuarios(cuentas)
        except OSError as error:
            mensaje.configure(text=f"No se pudo guardar: {error}")
            return

        cerrar()

    boton(panel, "Crear cuenta", guardar_y_cerrar, "primario").pack(fill="x", padx=60)
    boton(panel, "Cancelar", cerrar, "texto", alto=34).pack(fill="x", padx=60, pady=(8, 12))

    ventana.protocol("WM_DELETE_WINDOW", cerrar)
    root.ventana_registro_cuenta = ventana
    entry_usuario.focus_set()
    ventana.focus_force()

# --- Menú principal ---
def abrir_menu_principal(root, usuario):
    if ventana_abierta(root, "ventana_principal"):
        return

    principal = nueva_ventana(root, "Menú principal", 1360, 820, fondo=False)
    root.withdraw()

    lienzo = tk.Canvas(principal, highlightthickness=0, bd=0, bg=COLOR_FONDO)
    lienzo.place(x=0, y=0, relwidth=1, relheight=1)

    imagen = cargar_imagen()
    estado = {"job": None, "tam": (0, 0), "foto": None}

    def cerrar():
        cerrar_sesion(root, principal)

    boton_cerrar = boton(principal, "Cerrar sesión", cerrar, "suave", ancho=140, alto=36)

    botones = [
        boton(principal, "Registrar animal", lambda: abrir_formulario_animal(principal), "primario", ancho=220, alto=108, tam=15),
        boton(principal, "Consultar animales", lambda: abrir_catalogo(principal), "suave", ancho=220, alto=108, tam=15),
        boton(principal, "Generar factura", lambda: abrir_facturacion(principal), "suave", ancho=220, alto=108, tam=15),
        boton(principal, "Acerca de", lambda: abrir_acerca(principal), "suave", ancho=220, alto=108, tam=15),
    ]

    def ubicar_botones():
        boton_cerrar.place(relx=1.0, x=-48, y=30, anchor="ne")
        centro = (len(botones) - 1) / 2
        for indice, widget in enumerate(botones):
            widget.place(relx=0.5, rely=0.50, x=round((indice - centro) * 234), anchor="n")

    def dibujar():
        estado["job"] = None
        try:
            if not lienzo.winfo_exists():
                return
            ancho = max(lienzo.winfo_width(), 480)
            alto = max(lienzo.winfo_height(), 360)
        except Exception:
            return
        if abs(ancho - estado["tam"][0]) < 40 and abs(alto - estado["tam"][1]) < 40:
            return
        estado["tam"] = (ancho, alto)
        lienzo.delete("all")

        if imagen is not None:
            recorte = ImageOps.fit(imagen, (ancho, alto), Image.Resampling.LANCZOS)
            foto = ImageTk.PhotoImage(recorte)
            lienzo.create_image(0, 0, anchor="nw", image=foto)
            estado["foto"] = foto

        escala = ctk.ScalingTracker.get_widget_scaling(lienzo) or 1.0
        margen = round(48 * escala)
        lienzo.create_text(margen, round(30 * escala), anchor="nw", text="Métodos Campesinos", font=(FUENTE, 16, "bold"), fill=COLOR_TEXTO)
        lienzo.create_text(ancho - margen - round(162 * escala), round(38 * escala), anchor="ne", text=f"Usuario: {usuario}", font=(FUENTE, 10), fill=COLOR_SECUNDARIO)
        lienzo.create_text(ancho / 2, alto * 0.40, anchor="center", text="¿Qué deseas hacer?", font=(FUENTE, 20, "bold"), fill=COLOR_TEXTO)
        lienzo.create_text(ancho / 2, alto * 0.40 + round(44 * escala), anchor="center", text="Selecciona una opción para continuar.", font=(FUENTE, 11), fill=COLOR_SECUNDARIO)
        ubicar_botones()

    def redimensionar(evento=None):
        if evento is not None and evento.widget is not lienzo:
            return
        if estado["job"] is not None:
            try:
                lienzo.after_cancel(estado["job"])
            except Exception:
                pass
        estado["job"] = lienzo.after(140, dibujar)

    lienzo.bind("<Configure>", redimensionar)
    principal.protocol("WM_DELETE_WINDOW", lambda: cerrar_sesion(root, principal))
    root.ventana_principal = principal
    principal.focus_force()
    lienzo.after(30, dibujar)

def cerrar_sesion(root, principal):
    for atributo in ("ventana_catalogo", "ventana_registro_animal", "ventana_factura", "ventana_factura_vista", "ventana_acerca"):
        ventana = getattr(principal, atributo, None)
        if ventana is not None:
            try:
                ventana.destroy()
            except Exception:
                pass
            setattr(principal, atributo, None)

    try:
        principal.destroy()
    except Exception:
        pass
    root.ventana_principal = None

    try:
        root.deiconify()
        root.entry_contrasena.delete(0, "end")
        root.entry_usuario.focus_set()
        root.mensaje_login.configure(text="")
        root.lift()
        root.focus_force()
    except Exception:
        pass

# --- Formulario de registro de bovinos ---
def abrir_formulario_animal(principal):
    if ventana_abierta(principal, "ventana_registro_animal"):
        return

    formulario = nueva_ventana(principal, "Registrar animal", 1280, 820)

    panel = tarjeta(formulario)
    panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.93, relheight=0.9)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_rowconfigure(1, weight=1)

    cabecera = ctk.CTkFrame(panel, fg_color="transparent")
    cabecera.grid(row=0, column=0, sticky="ew", padx=36, pady=(28, 12))
    etiqueta(cabecera, "Registrar animal", 28, COLOR_TEXTO, negrita=True).pack(anchor="w")
    etiqueta(cabecera, "Hoja técnica básica del bovino.", 13, COLOR_SECUNDARIO).pack(anchor="w", pady=(4, 0))

    marco = ctk.CTkScrollableFrame(panel, fg_color=COLOR_TARJETA, bg_color=COLOR_TARJETA, corner_radius=0, scrollbar_button_color=COLOR_BORDE, scrollbar_button_hover_color=COLOR_PRIMARIO)
    marco.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 10))
    marco.grid_columnconfigure(0, weight=1)
    marco.grid_columnconfigure(1, weight=1)

    def agregar_campo(fila, columna, texto, tipo="entry", valores=None, marcador="", columnas=1):
        contenedor = ctk.CTkFrame(marco, fg_color="transparent")
        contenedor.grid(row=fila, column=columna, columnspan=columnas, sticky="ew", padx=12, pady=8)
        etiqueta(contenedor, texto, 12, COLOR_SECUNDARIO, anchor="w").pack(fill="x")

        if tipo.startswith("combo"):
            widget = ctk.CTkComboBox(contenedor, values=valores or [], state="readonly" if tipo == "combo" else "normal", height=42, font=(FUENTE, 14), corner_radius=10, border_width=1, border_color=COLOR_BORDE)
            if valores:
                widget.set(valores[0])
        elif tipo == "texto":
            widget = ctk.CTkTextbox(contenedor, height=96, font=(FUENTE, 14), corner_radius=10, border_width=1, border_color=COLOR_BORDE, fg_color="white")
        else:
            widget = entrada(contenedor, marcador)

        widget.pack(fill="x", pady=(6, 0))
        return widget

    entry_identificacion = agregar_campo(0, 0, "Identificación / arete *", marcador="Ej: AR-001")
    entry_nombre = agregar_campo(0, 1, "Nombre *", marcador="Ej: Luna")
    combo_raza = agregar_campo(1, 0, "Raza *", tipo="combo_editable", valores=RAZAS)
    combo_sexo = agregar_campo(1, 1, "Sexo *", tipo="combo", valores=SEXOS)
    entry_fecha_nacimiento = agregar_campo(2, 0, "Fecha de nacimiento * (AAAA-MM-DD)", marcador="Ej: 2022-03-15")
    entry_peso = agregar_campo(2, 1, "Peso (kg) *", marcador="Ej: 450")
    entry_color = agregar_campo(3, 0, "Color", marcador="Ej: Blanco y negro")
    combo_proposito = agregar_campo(3, 1, "Propósito *", tipo="combo", valores=PROPOSITOS)
    combo_origen = agregar_campo(4, 0, "Origen *", tipo="combo", valores=ORIGENES)
    entry_procedencia = agregar_campo(4, 1, "Procedencia", marcador="Granja o lugar de donde vino")
    entry_fecha_ingreso = agregar_campo(5, 0, "Fecha de ingreso (AAAA-MM-DD)", marcador="Hoy")
    combo_estado = agregar_campo(5, 1, "Estado *", tipo="combo", valores=ESTADOS)
    texto_observaciones = agregar_campo(6, 0, "Observaciones", tipo="texto", columnas=2)

    combo_proposito.set("Doble propósito")
    combo_raza.set("Mestizo")
    entry_fecha_ingreso.insert(0, date.today().isoformat())

    pie = ctk.CTkFrame(panel, fg_color="transparent")
    pie.grid(row=2, column=0, sticky="ew", padx=36, pady=(0, 24))

    mensaje = etiqueta(pie, "", 12, COLOR_PELIGRO, anchor="w", wraplength=620, justify="left")
    mensaje.pack(side="left", fill="x", expand=True)

    boton(pie, "Guardar animal", lambda: guardar(), "primario", ancho=180, alto=42).pack(side="right")
    boton(pie, "Limpiar", lambda: limpiar(), "suave", ancho=120, alto=42).pack(side="right", padx=(10, 0))
    boton(pie, "Volver", lambda: volver(), "suave", ancho=120, alto=42).pack(side="right", padx=(10, 0))

    def mostrar_error(texto):
        mensaje.configure(text=texto, text_color=COLOR_PELIGRO)

    def limpiar():
        for campo in (entry_identificacion, entry_nombre, entry_fecha_nacimiento, entry_peso, entry_color, entry_fecha_ingreso):
            campo.delete(0, "end")
        for combo, valor in ((combo_raza, "Mestizo"), (combo_sexo, "Hembra"), (combo_proposito, "Doble propósito"), (combo_origen, "Criado en la granja"), (combo_estado, "Activo")):
            combo.set(valor)
        entry_fecha_ingreso.insert(0, date.today().isoformat())
        texto_observaciones.delete("1.0", "end")
        mensaje.configure(text="")
        entry_identificacion.focus_set()

    def guardar():
        datos = {
            "identificacion": entry_identificacion.get().strip(),
            "nombre": entry_nombre.get().strip(),
            "raza": combo_raza.get().strip(),
            "sexo": combo_sexo.get().strip(),
            "fecha_nacimiento": entry_fecha_nacimiento.get().strip(),
            "peso": entry_peso.get().strip().replace(",", "."),
            "color": entry_color.get().strip(),
            "proposito": combo_proposito.get().strip(),
            "origen": combo_origen.get().strip(),
            "procedencia": entry_procedencia.get().strip(),
            "fecha_ingreso": entry_fecha_ingreso.get().strip(),
            "estado": combo_estado.get().strip(),
            "observaciones": texto_observaciones.get("1.0", "end-1c").strip(),
        }

        if not datos["identificacion"]:
            return mostrar_error("La identificación o arete es obligatoria.")
        if not datos["nombre"]:
            return mostrar_error("El nombre del animal es obligatorio.")
        if not datos["raza"]:
            return mostrar_error("La raza es obligatoria.")
        if datos["sexo"] not in SEXOS:
            return mostrar_error("Selecciona un sexo válido.")
        if datos["proposito"] not in PROPOSITOS:
            return mostrar_error("Selecciona un propósito válido.")
        if datos["origen"] not in ORIGENES:
            return mostrar_error("Selecciona un origen válido.")
        if datos["estado"] not in ESTADOS:
            return mostrar_error("Selecciona un estado válido.")

        nacimiento = validar_fecha(datos["fecha_nacimiento"])
        if nacimiento is None:
            return mostrar_error("La fecha de nacimiento debe tener el formato AAAA-MM-DD.")
        if nacimiento > date.today():
            return mostrar_error("La fecha de nacimiento no puede ser futura.")

        ingreso = validar_fecha(datos["fecha_ingreso"] or date.today().isoformat())
        if ingreso is None:
            return mostrar_error("La fecha de ingreso debe tener el formato AAAA-MM-DD.")
        if ingreso < nacimiento:
            return mostrar_error("La fecha de ingreso no puede ser anterior a la de nacimiento.")

        try:
            peso = float(datos["peso"])
        except ValueError:
            return mostrar_error("El peso debe ser un número. Ejemplo: 450 o 450,5.")
        if peso <= 0:
            return mostrar_error("El peso debe ser mayor que cero.")

        if datos["origen"] != "Criado en la granja" and not datos["procedencia"]:
            return mostrar_error("Indica la procedencia del animal (granja o lugar de origen).")
        if datos["origen"] == "Criado en la granja" and not datos["procedencia"]:
            datos["procedencia"] = "Granja propia"

        animales = cargar_animales()
        if any(str(animal.get("identificacion", "")).strip().lower() == datos["identificacion"].lower() for animal in animales):
            return mostrar_error("Ya existe un animal con esa identificación o arete.")

        ids = [animal.get("id") for animal in animales if isinstance(animal.get("id"), int)]
        datos["id"] = max(ids, default=0) + 1
        datos["fecha_nacimiento"] = nacimiento.isoformat()
        datos["fecha_ingreso"] = ingreso.isoformat()
        datos["peso"] = peso

        animales.append(datos)
        try:
            guardar_animales(animales)
        except OSError as error:
            return mostrar_error(f"No se pudo guardar el animal: {error}")

        catalogo = getattr(principal, "ventana_catalogo", None)
        if catalogo is not None:
            try:
                if catalogo.winfo_exists():
                    catalogo.recargar()
            except Exception:
                pass

        limpiar()
        mensaje.configure(text=f"Animal '{datos['nombre']}' registrado correctamente.", text_color=COLOR_EXITO)

    def volver():
        try:
            formulario.destroy()
        except Exception:
            pass
        principal.ventana_registro_animal = None

    formulario.protocol("WM_DELETE_WINDOW", volver)
    principal.ventana_registro_animal = formulario

    # Referencias útiles para pruebas y para refrescar el formulario.
    formulario.entry_identificacion = entry_identificacion
    formulario.entry_nombre = entry_nombre
    formulario.combo_raza = combo_raza
    formulario.combo_sexo = combo_sexo
    formulario.entry_fecha_nacimiento = entry_fecha_nacimiento
    formulario.entry_peso = entry_peso
    formulario.entry_color = entry_color
    formulario.combo_proposito = combo_proposito
    formulario.combo_origen = combo_origen
    formulario.entry_procedencia = entry_procedencia
    formulario.entry_fecha_ingreso = entry_fecha_ingreso
    formulario.combo_estado = combo_estado
    formulario.texto_observaciones = texto_observaciones
    formulario.mensaje = mensaje
    formulario.guardar = guardar
    formulario.limpiar = limpiar

    entry_identificacion.focus_set()
    formulario.focus_force()

# --- Catálogo de animales con filtros ---
def abrir_catalogo(principal):
    if ventana_abierta(principal, "ventana_catalogo"):
        return

    catalogo = nueva_ventana(principal, "Consulta de animales", 1360, 840)

    panel = tarjeta(catalogo)
    panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.94, relheight=0.9)
    panel.grid_columnconfigure(0, weight=0, minsize=330)
    panel.grid_columnconfigure(1, weight=1)
    panel.grid_rowconfigure(1, weight=1)

    cabecera = ctk.CTkFrame(panel, fg_color="transparent")
    cabecera.grid(row=0, column=0, columnspan=2, sticky="ew", padx=32, pady=(24, 12))
    etiqueta(cabecera, "Animales", 28, COLOR_TEXTO, negrita=True).pack(side="left")
    contador = etiqueta(cabecera, "", 13, COLOR_SECUNDARIO)
    contador.pack(side="right")

    izquierdo = ctk.CTkFrame(panel, fg_color=COLOR_SUAVE, corner_radius=16)
    izquierdo.grid(row=1, column=0, sticky="nsew", padx=(32, 14), pady=(0, 26))

    etiqueta(izquierdo, "Buscar", 12, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=16, pady=(18, 6))
    fila_busqueda = ctk.CTkFrame(izquierdo, fg_color="transparent")
    fila_busqueda.pack(fill="x", padx=16)

    entry_busqueda = entrada(fila_busqueda, "Nombre o arete", alto=38)
    entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 8))
    boton(fila_busqueda, "Buscar", lambda: actualizar_lista(), "primario", ancho=84, alto=38, tam=12).pack(side="left")
    entry_busqueda.bind("<Return>", lambda event: actualizar_lista())

    etiqueta(izquierdo, "Filtrar por", 12, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=16, pady=(18, 6))
    marco_categorias = ctk.CTkFrame(izquierdo, fg_color="transparent")
    marco_categorias.pack(fill="x", padx=11)
    marco_categorias.grid_columnconfigure(0, weight=1)
    marco_categorias.grid_columnconfigure(1, weight=1)

    botones_categoria = {}
    for indice, (clave, titulo) in enumerate(CAMPOS_FILTRO):
        boton_cat = boton(marco_categorias, titulo, lambda c=clave: seleccionar_categoria(c), "suave", alto=34, tam=12)
        boton_cat.grid(row=indice // 2, column=indice % 2, padx=5, pady=5, sticky="ew")
        botones_categoria[clave] = boton_cat

    boton(izquierdo, "Volver", lambda: cerrar_catalogo(), "texto", alto=34, tam=12).pack(side="bottom", fill="x", padx=16, pady=(0, 18))
    boton(izquierdo, "Limpiar filtros", lambda: limpiar_filtros(), "suave", alto=34, tam=12).pack(side="bottom", fill="x", padx=16, pady=(0, 6))
    boton(izquierdo, "Ver hoja técnica", lambda: mostrar_hoja(), "primario", alto=36, tam=12).pack(side="bottom", fill="x", padx=16, pady=(8, 0))

    etiqueta(izquierdo, "Valores", 12, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=16, pady=(18, 6))
    panel_valores = ctk.CTkScrollableFrame(izquierdo, height=180, fg_color=COLOR_TARJETA, bg_color=COLOR_TARJETA, corner_radius=12, scrollbar_button_color=COLOR_BORDE, scrollbar_button_hover_color=COLOR_PRIMARIO)
    panel_valores.pack(fill="both", expand=True, padx=16, pady=(0, 8))

    derecho = ctk.CTkFrame(panel, fg_color="transparent")
    derecho.grid(row=1, column=1, sticky="nsew", padx=(14, 32), pady=(0, 26))
    derecho.grid_rowconfigure(0, weight=1)
    derecho.grid_columnconfigure(0, weight=1)

    marco_tabla = ctk.CTkFrame(derecho, fg_color=COLOR_TARJETA, corner_radius=14, border_width=1, border_color=COLOR_BORDE)
    marco_tabla.grid(row=0, column=0, sticky="nsew")
    marco_tabla.grid_rowconfigure(0, weight=1)
    marco_tabla.grid_columnconfigure(0, weight=1)

    estilo = ttk.Style()
    try:
        estilo.theme_use("clam")
    except Exception:
        pass
    estilo.configure("Animales.Treeview", background=COLOR_TARJETA, foreground=COLOR_TEXTO, fieldbackground=COLOR_TARJETA, rowheight=34, font=(FUENTE, 11), borderwidth=0)
    estilo.configure("Animales.Treeview.Heading", font=(FUENTE, 11, "bold"), background=COLOR_SUAVE, foreground=COLOR_TEXTO, borderwidth=0, padding=(8, 6))

    columnas = [("identificacion", "Arete", 110), ("nombre", "Nombre", 130), ("raza", "Raza", 110), ("sexo", "Sexo", 80), ("peso", "Peso (kg)", 90), ("origen", "Origen", 160)]

    tabla = ttk.Treeview(marco_tabla, columns=[columna[0] for columna in columnas], show="headings", style="Animales.Treeview")
    for clave, titulo, ancho in columnas:
        tabla.heading(clave, text=titulo)
        tabla.column(clave, width=ancho, anchor="w", stretch=True)

    barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.grid(row=0, column=0, sticky="nsew")
    barra.grid(row=0, column=1, sticky="ns")

    filtros = {clave: None for clave, _ in CAMPOS_FILTRO}
    categoria_actual = None
    animales_filtrados = []

    def actualizar_lista():
        nonlocal animales_filtrados
        todos = cargar_animales()
        animales_filtrados = filtrar_animales(todos, filtros, entry_busqueda.get())

        filas = tabla.get_children()
        if filas:
            tabla.delete(*filas)
        for indice, animal in enumerate(animales_filtrados):
            tabla.insert("", "end", iid=str(indice), values=(
                animal.get("identificacion", ""),
                animal.get("nombre", ""),
                animal.get("raza", ""),
                animal.get("sexo", ""),
                formatear_peso(animal.get("peso")),
                animal.get("origen", ""),
            ))

        contador.configure(text=f"{len(animales_filtrados)} de {len(todos)} animales")

    def indice_seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            return None
        try:
            indice = int(seleccion[0])
        except ValueError:
            return None
        if 0 <= indice < len(animales_filtrados):
            return indice
        return None

    def mostrar_hoja(evento=None):
        indice = indice_seleccionado()
        if indice is None:
            return
        animal = animales_filtrados[indice]
        titulo = f"Hoja técnica - {animal.get('nombre', '')}"
        contenido = formatear_hoja(animal)

        if ventana_abierta(catalogo, "ventana_hoja"):
            catalogo.ventana_hoja.mostrar_hoja(titulo, contenido)
            return

        vista = nueva_ventana(catalogo, titulo, 900, 720)

        panel_hoja = tarjeta(vista)
        panel_hoja.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.92)

        cabecera = ctk.CTkFrame(panel_hoja, fg_color="transparent")
        cabecera.pack(fill="x", padx=28, pady=(22, 12))
        etiqueta(cabecera, "Hoja técnica del bovino", 24, COLOR_TEXTO, negrita=True).pack(side="left")
        etiqueta(cabecera, animal.get("identificacion", ""), 13, COLOR_SECUNDARIO).pack(side="right")

        caja = ctk.CTkTextbox(panel_hoja, font=("Consolas", 12), wrap="none", corner_radius=14, border_width=1, border_color=COLOR_BORDE, fg_color="white")
        caja.pack(fill="both", expand=True, padx=28, pady=(0, 14))

        pie = ctk.CTkFrame(panel_hoja, fg_color="transparent")
        pie.pack(fill="x", padx=28, pady=(0, 20))

        def cerrar_hoja():
            try:
                vista.destroy()
            except Exception:
                pass
            catalogo.ventana_hoja = None

        def mostrar_hoja_texto(titulo, contenido):
            vista.title(titulo)
            caja.configure(state="normal")
            caja.delete("1.0", "end")
            caja.insert("1.0", contenido)
            caja.configure(state="disabled")

        boton(pie, "Cerrar", lambda: cerrar_hoja(), "primario", ancho=120, alto=38, tam=13).pack(side="right")

        vista.protocol("WM_DELETE_WINDOW", cerrar_hoja)
        vista.mostrar_hoja = mostrar_hoja_texto
        vista.caja = caja
        catalogo.ventana_hoja = vista

        mostrar_hoja_texto(titulo, contenido)
        vista.focus_force()

    def aplicar_valor(valor):
        if categoria_actual is None:
            return
        filtros[categoria_actual] = valor
        actualizar_lista()
        seleccionar_categoria(categoria_actual)

    def seleccionar_categoria(categoria):
        nonlocal categoria_actual
        categoria_actual = categoria

        for clave, boton_cat in botones_categoria.items():
            activo = clave == categoria
            boton_cat.configure(fg_color=COLOR_PRIMARIO if activo else COLOR_SUAVE, hover_color=COLOR_PRIMARIO_HOVER if activo else COLOR_BORDE, text_color="white" if activo else COLOR_TEXTO)

        for hijo in panel_valores.winfo_children():
            hijo.destroy()

        valores = valores_categoria(cargar_animales(), categoria)
        elegido = filtros[categoria]

        boton(panel_valores, "Todos", lambda: aplicar_valor(None), "primario" if elegido is None else "suave", alto=30, tam=12).pack(fill="x", padx=4, pady=2)
        for valor in valores:
            boton(panel_valores, valor, lambda v=valor: aplicar_valor(v), "primario" if elegido == valor else "suave", alto=30, tam=12).pack(fill="x", padx=4, pady=2)
        if not valores:
            etiqueta(panel_valores, "Sin valores registrados", 12, COLOR_SECUNDARIO).pack(pady=12)

    def limpiar_filtros():
        nonlocal categoria_actual
        for clave in filtros:
            filtros[clave] = None
        entry_busqueda.delete(0, "end")
        categoria_actual = None

        for boton_cat in botones_categoria.values():
            boton_cat.configure(fg_color=COLOR_SUAVE, hover_color=COLOR_BORDE, text_color=COLOR_TEXTO)
        for hijo in panel_valores.winfo_children():
            hijo.destroy()

        actualizar_lista()

    def recargar():
        actualizar_lista()
        if categoria_actual is not None:
            seleccionar_categoria(categoria_actual)

    def cerrar_catalogo():
        try:
            catalogo.destroy()
        except Exception:
            pass
        principal.ventana_catalogo = None

    tabla.bind("<Double-1>", mostrar_hoja)
    tabla.bind("<Return>", mostrar_hoja)
    catalogo.protocol("WM_DELETE_WINDOW", cerrar_catalogo)
    principal.ventana_catalogo = catalogo

    # Referencias y funciones útiles para pruebas y para refrescar la vista.
    catalogo.tabla = tabla
    catalogo.entry_busqueda = entry_busqueda
    catalogo.panel_valores = panel_valores
    catalogo.contador = contador
    catalogo.filtros = filtros
    catalogo.botones_categoria = botones_categoria
    catalogo.actualizar_lista = actualizar_lista
    catalogo.seleccionar_categoria = seleccionar_categoria
    catalogo.aplicar_valor = aplicar_valor
    catalogo.limpiar_filtros = limpiar_filtros
    catalogo.mostrar_hoja = mostrar_hoja
    catalogo.recargar = recargar

    actualizar_lista()
    catalogo.focus_force()

# --- Facturación ---
def abrir_facturacion(principal):
    if ventana_abierta(principal, "ventana_factura"):
        return

    factura = nueva_ventana(principal, "Generar factura", 1080, 740)

    panel = tarjeta(factura)
    panel.place(relx=0.5, rely=0.5, anchor="center")
    fijar_ancho(panel, 500)

    etiqueta(panel, "Generar factura", 28, COLOR_TEXTO, negrita=True).pack(pady=(30, 2))
    etiqueta(panel, "Datos de la venta de bovinos.", 13, COLOR_SECUNDARIO).pack(pady=(0, 18))

    etiqueta(panel, "Granja", 12, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=54)
    entry_granja = entrada(panel, "Nombre de la granja")
    entry_granja.pack(fill="x", padx=54, pady=(3, 12))

    etiqueta(panel, "Comprador", 12, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=54)
    entry_comprador = entrada(panel, "Nombre del comprador")
    entry_comprador.pack(fill="x", padx=54, pady=(3, 12))

    etiqueta(panel, "Fecha", 12, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=54)
    entry_fecha = entrada(panel, "AAAA-MM-DD")
    entry_fecha.pack(fill="x", padx=54, pady=(3, 12))
    entry_fecha.insert(0, date.today().isoformat())

    etiqueta(panel, "Número de vacas", 12, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=54)
    entry_vacas = entrada(panel, "Ej: 5")
    entry_vacas.pack(fill="x", padx=54, pady=(3, 12))

    etiqueta(panel, "Precio por libra", 12, COLOR_SECUNDARIO, anchor="w").pack(fill="x", padx=54)
    entry_precio = entrada(panel, "Ej: 12000")
    entry_precio.pack(fill="x", padx=54, pady=(3, 14))

    mensaje = etiqueta(panel, "", 12, COLOR_PELIGRO, wraplength=386, justify="left")
    mensaje.pack(fill="x", padx=54, pady=(0, 8))

    def abrir_vista_factura(texto):
        if ventana_abierta(principal, "ventana_factura_vista"):
            principal.ventana_factura_vista.mostrar_factura(texto)
            return

        vista = nueva_ventana(principal, "Factura", 980, 760)

        panel_vista = tarjeta(vista)
        panel_vista.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.9)

        cabecera = ctk.CTkFrame(panel_vista, fg_color="transparent")
        cabecera.pack(fill="x", padx=28, pady=(22, 12))
        etiqueta(cabecera, "Factura", 24, COLOR_TEXTO, negrita=True).pack(side="left")
        etiqueta(cabecera, f"Archivo: {RUTA_FACTURA.name}", 12, COLOR_SECUNDARIO).pack(side="right")

        caja = ctk.CTkTextbox(panel_vista, font=("Consolas", 12), wrap="none", corner_radius=14, border_width=1, border_color=COLOR_BORDE, fg_color="white")
        caja.pack(fill="both", expand=True, padx=28, pady=(0, 14))

        pie = ctk.CTkFrame(panel_vista, fg_color="transparent")
        pie.pack(fill="x", padx=28, pady=(0, 20))

        def mostrar_factura(texto_vista):
            caja.configure(state="normal")
            caja.delete("1.0", "end")
            caja.insert("1.0", texto_vista)
            caja.configure(state="disabled")

        def cerrar_vista():
            try:
                vista.destroy()
            except Exception:
                pass
            principal.ventana_factura_vista = None

        def abrir_archivo():
            try:
                os.startfile(RUTA_FACTURA)
            except Exception:
                pass

        boton(pie, "Cerrar", lambda: cerrar_vista(), "primario", ancho=120, alto=38, tam=13).pack(side="right")
        boton(pie, "Abrir archivo", lambda: abrir_archivo(), "suave", ancho=140, alto=38, tam=13).pack(side="right", padx=(0, 8))

        vista.protocol("WM_DELETE_WINDOW", cerrar_vista)
        vista.mostrar_factura = mostrar_factura
        vista.caja = caja
        principal.ventana_factura_vista = vista

        mostrar_factura(texto)
        vista.focus_force()

    def generar():
        granja = entry_granja.get().strip()
        comprador = entry_comprador.get().strip()
        fecha_texto = entry_fecha.get().strip()
        vacas_texto = entry_vacas.get().strip()
        precio_texto = entry_precio.get().strip().replace(",", ".")

        if not granja or not comprador or not vacas_texto or not precio_texto:
            mensaje.configure(text="Llena todos los campos.")
            return

        fecha = validar_fecha(fecha_texto)
        if fecha is None:
            mensaje.configure(text="La fecha debe tener el formato AAAA-MM-DD.")
            return

        try:
            vacas = int(vacas_texto)
            precio = float(precio_texto)
        except ValueError:
            mensaje.configure(text="Las vacas deben ser un entero y el precio un número.")
            return

        if vacas <= 0 or precio <= 0:
            mensaje.configure(text="Las vacas y el precio deben ser mayores que cero.")
            return

        datos = {
            "Granja": granja,
            "Comprador": comprador,
            "Fecha": fecha.isoformat(),
            "VACAS": vacas,
            "Precio_por_libra": precio,
        }

        inicio = "# ==========================================\n#   Facturacion Electronica De Venta\n#   Generado por MiniGan.INC\n#   Correo: MiniGan@outlook.com\n#   PQR: 3**********\n# ==========================================\n"

        try:
            RUTA_FACTURA.write_text(inicio + yaml.dump(datos, allow_unicode=True, default_flow_style=False, sort_keys=False), encoding="utf-8")
        except OSError as error:
            mensaje.configure(text=f"No se pudo guardar la factura: {error}")
            return

        abrir_vista_factura(RUTA_FACTURA.read_text(encoding="utf-8"))
        mensaje.configure(text="Factura generada correctamente.", text_color=COLOR_EXITO)

    def cerrar():
        try:
            factura.destroy()
        except Exception:
            pass
        principal.ventana_factura = None

    boton(panel, "Generar factura", lambda: generar(), "primario").pack(fill="x", padx=54)
    boton(panel, "Volver", lambda: cerrar(), "texto", alto=34).pack(fill="x", padx=54, pady=(6, 18))

    factura.protocol("WM_DELETE_WINDOW", cerrar)
    principal.ventana_factura = factura

    # Referencias útiles para pruebas.
    factura.entry_granja = entry_granja
    factura.entry_comprador = entry_comprador
    factura.entry_fecha = entry_fecha
    factura.entry_vacas = entry_vacas
    factura.entry_precio = entry_precio
    factura.mensaje = mensaje
    factura.generar = generar

    factura.focus_force()

# --- Acerca de ---
def abrir_acerca(principal):
    if ventana_abierta(principal, "ventana_acerca"):
        return

    acerca = nueva_ventana(principal, "Acerca de", 920, 700)

    panel = tarjeta(acerca)
    panel.place(relx=0.5, rely=0.5, anchor="center")
    fijar_ancho(panel, 580)

    etiqueta(panel, "Métodos Campesinos", 28, COLOR_TEXTO, negrita=True).pack(pady=(42, 2))
    etiqueta(panel, "Control de ganado", 14, COLOR_SECUNDARIO).pack(pady=(0, 24))

    linea = ctk.CTkFrame(panel, height=1, fg_color=COLOR_BORDE)
    linea.pack(fill="x", padx=64)

    informacion = [
        ("Versión", "1.0"),
        ("Descripción", "Registro, consulta y facturación de bovinos."),
        ("Datos", "Se guardan en tu equipo, en Hoja_datos.json."),
        ("Tecnologías", "Python, CustomTkinter, Pillow y PyYAML."),
        ("Proyecto", "Programación II"),
    ]

    cuerpo = ctk.CTkFrame(panel, fg_color="transparent")
    cuerpo.pack(fill="x", padx=64, pady=(22, 6))

    for titulo, valor in informacion:
        fila = ctk.CTkFrame(cuerpo, fg_color="transparent")
        fila.pack(fill="x", pady=7)
        etiqueta(fila, titulo, 12, COLOR_SECUNDARIO, anchor="nw", width=110).pack(side="left", anchor="n")
        etiqueta(fila, valor, 13, COLOR_TEXTO, anchor="nw", wraplength=340, justify="left").pack(side="left", fill="x", expand=True)

    def cerrar():
        try:
            acerca.destroy()
        except Exception:
            pass
        principal.ventana_acerca = None

    boton(panel, "Cerrar", cerrar, "primario").pack(fill="x", padx=64, pady=(22, 32))

    acerca.protocol("WM_DELETE_WINDOW", cerrar)
    principal.ventana_acerca = acerca
    acerca.cerrar = cerrar
    acerca.focus_force()

# --- Punto de entrada ---
def main():
    root = crear_ventana_login()
    root.mainloop()

if __name__ == "__main__":
    main()
