from datetime import date, datetime
from pathlib import Path
import json

import customtkinter as ctk
import yaml
from PIL import Image
from tkinter import ttk

ctk.set_appearance_mode("light")

# ============================================================
# Rutas y constantes
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
RUTA_CUENTAS = BASE_DIR / "Cuentas.json"
RUTA_DATOS = BASE_DIR / "Hoja_datos.json"
RUTA_FACTURA = BASE_DIR / "nuevo.txt"
RUTA_IMAGEN = BASE_DIR / "IMAGEN DE APLICACION.jpg"

COLOR_FONDO = "#bce2f4"
COLOR_PANEL = "#eaf6fb"
COLOR_PANEL_FILTROS = "#dff0f8"
COLOR_BOTON = "lightblue"
COLOR_BOTON_ACTIVO = "#5aa9c9"
COLOR_TEXTO = "black"

SEXOS = ["Hembra", "Macho"]
RAZAS = [
    "Holstein",
    "Jersey",
    "Brahman",
    "Angus",
    "Hereford",
    "Nelore",
    "Gyr",
    "Simmental",
    "Normando",
    "Cebú",
    "Mestizo",
    "Otra",
]
PROPOSITOS = ["Leche", "Carne", "Doble propósito"]
ORIGENES = ["Criado en la granja", "Comprado", "Donado", "Otro"]
ESTADOS = ["Activo", "Vendido", "Muerto"]

# Categorías que se pueden filtrar en el catálogo.
# La clave coincide con el nombre del campo guardado en Hoja_datos.json.
CAMPOS_FILTRO = [
    ("sexo", "Sexo"),
    ("raza", "Raza"),
    ("origen", "Origen"),
    ("proposito", "Propósito"),
    ("estado", "Estado"),
    ("color", "Color"),
]

_imagen_fondo = None


# ============================================================
# Utilidades generales
# ============================================================
def crear_fondo(ventana):
    """Coloca la imagen de fondo. Si no existe, la ventana sigue funcionando."""
    global _imagen_fondo
    try:
        if _imagen_fondo is None:
            imagen = Image.open(RUTA_IMAGEN)
            _imagen_fondo = ctk.CTkImage(
                light_image=imagen,
                dark_image=imagen,
                size=(1280, 720),
            )
    except Exception:
        return None

    etiqueta = ctk.CTkLabel(ventana, image=_imagen_fondo, text="")
    etiqueta.place(x=0, y=0, relwidth=1, relheight=1)
    etiqueta.lower()
    return etiqueta


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


# ============================================================
# Cuentas
# ============================================================
def cargar_usuarios():
    datos = cargar_json(RUTA_CUENTAS, {})
    return datos if isinstance(datos, dict) else {}


def guardar_usuarios(usuarios):
    guardar_json(RUTA_CUENTAS, usuarios)


# ============================================================
# Animales (bovinos)
# ============================================================
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
            if str(animal.get(clave, "")).strip().lower() != str(valor).strip().lower():
                coincide = False
                break

        if coincide:
            resultado.append(animal)

    return resultado


def valores_categoria(animales, categoria):
    valores = {
        str(animal.get(categoria, "")).strip()
        for animal in animales
        if str(animal.get(categoria, "")).strip()
    }
    return sorted(valores, key=str.lower)


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


# ============================================================
# Ventana de inicio de sesión
# ============================================================
def crear_ventana_login():
    root = ctk.CTk()
    root.title("Metodos campesinos")
    root.geometry("1280x720")
    root.minsize(1000, 650)
    crear_fondo(root)

    titulo = ctk.CTkLabel(
        root,
        text="Inicio de sesión",
        font=("Arial", 56),
        fg_color="transparent",
        bg_color=COLOR_FONDO,
        text_color=COLOR_TEXTO,
    )
    titulo.place(relx=0.5, rely=0.15, anchor="center")

    etiqueta_usuario = ctk.CTkLabel(
        root,
        text="Digite su usuario",
        font=("Arial", 30),
        fg_color="transparent",
        bg_color=COLOR_FONDO,
        text_color=COLOR_TEXTO,
    )
    etiqueta_usuario.place(relx=0.5, rely=0.28, anchor="center")

    entry_usuario = ctk.CTkEntry(
        root,
        font=("Arial", 26),
        fg_color="transparent",
        text_color=COLOR_TEXTO,
        width=420,
    )
    entry_usuario.place(relx=0.5, rely=0.38, anchor="center")

    etiqueta_contrasena = ctk.CTkLabel(
        root,
        text="Digite su contraseña",
        font=("Arial", 30),
        fg_color="transparent",
        bg_color=COLOR_FONDO,
        text_color=COLOR_TEXTO,
    )
    etiqueta_contrasena.place(relx=0.5, rely=0.50, anchor="center")

    entry_contrasena = ctk.CTkEntry(
        root,
        font=("Arial", 26),
        fg_color="transparent",
        text_color=COLOR_TEXTO,
        show="*",
        width=420,
    )
    entry_contrasena.place(relx=0.5, rely=0.60, anchor="center")

    boton_ingresar = ctk.CTkButton(
        root,
        text="Iniciar sesión",
        font=("Arial", 26),
        fg_color=COLOR_BOTON,
        text_color=COLOR_TEXTO,
        width=420,
        height=50,
        command=lambda: iniciar_sesion(root),
    )
    boton_ingresar.place(relx=0.5, rely=0.72, anchor="center")

    boton_crear = ctk.CTkButton(
        root,
        text="Crear usuario",
        font=("Arial", 26),
        width=420,
        height=50,
        command=lambda: abrir_registro_cuenta(root),
    )
    boton_crear.place(relx=0.5, rely=0.82, anchor="center")

    root.entry_usuario = entry_usuario
    root.entry_contrasena = entry_contrasena
    root.error_usuario = None
    root.error_contrasena = None
    root.ventana_principal = None
    root.ventana_registro_cuenta = None

    entry_usuario.bind("<Return>", lambda event: iniciar_sesion(root))
    entry_contrasena.bind("<Return>", lambda event: iniciar_sesion(root))

    entry_usuario.focus_set()
    return root


def iniciar_sesion(root):
    for atributo in ("error_usuario", "error_contrasena"):
        etiqueta = getattr(root, atributo, None)
        if etiqueta is not None:
            try:
                etiqueta.destroy()
            except Exception:
                pass
            setattr(root, atributo, None)

    usuario = root.entry_usuario.get().strip()
    contrasena = root.entry_contrasena.get()

    if not usuario or not contrasena:
        root.error_usuario = ctk.CTkLabel(
            root,
            text="Digite usuario y contraseña",
            font=("Arial", 20),
            text_color="red",
            fg_color="transparent",
        )
        root.error_usuario.place(relx=0.5, rely=0.92, anchor="center")
        return

    usuarios = cargar_usuarios()

    if usuario in usuarios and usuarios[usuario] == contrasena:
        abrir_menu_principal(root, usuario)
    elif usuario in usuarios:
        root.error_contrasena = ctk.CTkLabel(
            root,
            text="Contraseña incorrecta",
            font=("Arial", 20),
            text_color="red",
            fg_color="transparent",
        )
        root.error_contrasena.place(relx=0.5, rely=0.92, anchor="center")
    else:
        root.error_usuario = ctk.CTkLabel(
            root,
            text="Usuario incorrecto",
            font=("Arial", 20),
            text_color="red",
            fg_color="transparent",
        )
        root.error_usuario.place(relx=0.5, rely=0.92, anchor="center")


def abrir_registro_cuenta(root):
    if ventana_abierta(root, "ventana_registro_cuenta"):
        return

    ventana = ctk.CTkToplevel(root, fg_color="lightblue")
    ventana.title("Crear usuario")
    ventana.geometry("800x600")
    ventana.transient(root)

    etiqueta_usuario = ctk.CTkLabel(
        ventana,
        text="Ingrese su nuevo usuario",
        font=("Arial", 30),
        text_color=COLOR_TEXTO,
    )
    etiqueta_usuario.place(relx=0.5, rely=0.20, anchor="center")

    entry_usuario = ctk.CTkEntry(ventana, font=("Arial", 20), width=420)
    entry_usuario.place(relx=0.5, rely=0.32, anchor="center")

    etiqueta_contrasena = ctk.CTkLabel(
        ventana,
        text="Ingrese su contraseña",
        font=("Arial", 30),
        text_color=COLOR_TEXTO,
    )
    etiqueta_contrasena.place(relx=0.5, rely=0.47, anchor="center")

    entry_contrasena = ctk.CTkEntry(ventana, font=("Arial", 20), width=420, show="*")
    entry_contrasena.place(relx=0.5, rely=0.59, anchor="center")

    mensaje = ctk.CTkLabel(ventana, text="", font=("Arial", 16), text_color="red")
    mensaje.place(relx=0.5, rely=0.69, anchor="center")

    def cerrar():
        try:
            ventana.destroy()
        except Exception:
            pass
        root.ventana_registro_cuenta = None
        root.deiconify()
        root.lift()
        root.focus_force()

    def guardar_y_cerrar():
        nombre_usuario = entry_usuario.get().strip()
        clave_usuario = entry_contrasena.get()

        if not nombre_usuario or not clave_usuario:
            mensaje.configure(text="Por favor, llena ambos campos.")
            return

        cuentas = cargar_usuarios()
        if nombre_usuario in cuentas:
            mensaje.configure(text="Ese usuario ya existe. Elige otro.")
            return

        cuentas[nombre_usuario] = clave_usuario
        try:
            guardar_usuarios(cuentas)
        except OSError as error:
            mensaje.configure(text=f"No se pudo guardar: {error}")
            return

        cerrar()

    boton_terminar = ctk.CTkButton(
        ventana,
        text="Terminar usuario",
        font=("Arial", 24),
        fg_color="green",
        width=420,
        height=50,
        command=guardar_y_cerrar,
    )
    boton_terminar.place(relx=0.5, rely=0.80, anchor="center")

    ventana.protocol("WM_DELETE_WINDOW", cerrar)
    root.ventana_registro_cuenta = ventana
    entry_usuario.focus_set()
    ventana.focus_force()


# ============================================================
# Menú principal
# ============================================================
def abrir_menu_principal(root, usuario):
    if ventana_abierta(root, "ventana_principal"):
        return

    root.withdraw()

    principal = ctk.CTkToplevel(root)
    principal.title("Menu principal")
    principal.geometry("1280x720")
    principal.minsize(1000, 650)
    crear_fondo(principal)

    ctk.CTkLabel(
        principal,
        text="Menú principal",
        font=("Arial", 44),
        bg_color=COLOR_FONDO,
        text_color=COLOR_TEXTO,
    ).place(relx=0.5, rely=0.12, anchor="center")

    ctk.CTkLabel(
        principal,
        text=f"Usuario: {usuario}",
        font=("Arial", 18),
        bg_color=COLOR_FONDO,
        text_color=COLOR_TEXTO,
    ).place(relx=0.88, rely=0.06, anchor="center")

    boton_consulta = ctk.CTkButton(
        principal,
        text="Consulta animales",
        font=("Arial", 24),
        bg_color=COLOR_FONDO,
        width=420,
        height=50,
        command=lambda: abrir_catalogo(principal),
    )
    boton_consulta.place(relx=0.22, rely=0.30, anchor="center")

    boton_factura = ctk.CTkButton(
        principal,
        text="Generar factura",
        font=("Arial", 24),
        bg_color=COLOR_FONDO,
        width=420,
        height=50,
        command=lambda: abrir_facturacion(principal),
    )
    boton_factura.place(relx=0.22, rely=0.44, anchor="center")

    boton_registrar = ctk.CTkButton(
        principal,
        text="Registrar animal",
        font=("Arial", 24),
        bg_color=COLOR_FONDO,
        width=420,
        height=50,
        command=lambda: abrir_formulario_animal(principal),
    )
    boton_registrar.place(relx=0.22, rely=0.58, anchor="center")

    boton_salir = ctk.CTkButton(
        principal,
        text="Cerrar sesión",
        font=("Arial", 18),
        fg_color="#c94f4f",
        hover_color="#a83f3f",
        width=200,
        height=40,
        command=lambda: cerrar_sesion(root, principal),
    )
    boton_salir.place(relx=0.88, rely=0.90, anchor="center")

    principal.protocol("WM_DELETE_WINDOW", lambda: cerrar_sesion(root, principal))
    root.ventana_principal = principal
    principal.focus_force()


def cerrar_sesion(root, principal):
    try:
        principal.destroy()
    except Exception:
        pass
    root.ventana_principal = None

    try:
        root.deiconify()
        root.entry_contrasena.delete(0, "end")
        root.entry_usuario.focus_set()
        root.lift()
        root.focus_force()
    except Exception:
        pass


# ============================================================
# Formulario de registro de bovinos
# ============================================================
def abrir_formulario_animal(principal):
    if ventana_abierta(principal, "ventana_registro_animal"):
        return

    formulario = ctk.CTkToplevel(principal)
    formulario.title("Registrar animal")
    formulario.geometry("980x720")
    formulario.minsize(900, 650)
    formulario.transient(principal)
    crear_fondo(formulario)

    panel = ctk.CTkFrame(formulario, fg_color=COLOR_PANEL, corner_radius=18)
    panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.96, relheight=0.95)

    ctk.CTkLabel(
        panel,
        text="Registrar animal",
        font=("Arial", 34),
        text_color=COLOR_TEXTO,
    ).pack(pady=(16, 2))

    ctk.CTkLabel(
        panel,
        text="Completa la hoja técnica básica del bovino.",
        font=("Arial", 16),
        text_color="#444444",
    ).pack(pady=(0, 8))

    marco_formulario = ctk.CTkScrollableFrame(
        panel,
        fg_color=COLOR_PANEL,
        corner_radius=0,
    )
    marco_formulario.pack(fill="both", expand=True, padx=18, pady=(0, 8))
    marco_formulario.grid_columnconfigure(0, weight=1)
    marco_formulario.grid_columnconfigure(1, weight=1)

    def agregar_campo(
        fila,
        columna,
        etiqueta,
        tipo="entry",
        valores=None,
        placeholder="",
        columnspan=1,
    ):
        marco = ctk.CTkFrame(marco_formulario, fg_color="transparent")
        marco.grid(
            row=fila,
            column=columna,
            columnspan=columnspan,
            padx=10,
            pady=6,
            sticky="ew",
        )
        ctk.CTkLabel(
            marco,
            text=etiqueta,
            font=("Arial", 15),
            text_color=COLOR_TEXTO,
            anchor="w",
        ).pack(fill="x")

        if tipo in ("combo", "combo_editable"):
            widget = ctk.CTkComboBox(
                marco,
                values=valores or [],
                font=("Arial", 15),
                height=36,
                state="readonly" if tipo == "combo" else "normal",
            )
            if valores:
                widget.set(valores[0])
        elif tipo == "texto":
            widget = ctk.CTkTextbox(
                marco,
                height=90,
                font=("Arial", 15),
                wrap="word",
            )
        else:
            widget = ctk.CTkEntry(
                marco,
                font=("Arial", 15),
                height=36,
                placeholder_text=placeholder,
            )

        widget.pack(fill="x")
        return widget

    entry_identificacion = agregar_campo(
        0, 0, "Identificación / arete *", placeholder="Ej: AR-001"
    )
    entry_nombre = agregar_campo(
        0, 1, "Nombre *", placeholder="Ej: Luna"
    )
    combo_raza = agregar_campo(
        1, 0, "Raza *", tipo="combo_editable", valores=RAZAS
    )
    combo_sexo = agregar_campo(
        1, 1, "Sexo *", tipo="combo", valores=SEXOS
    )
    entry_fecha_nacimiento = agregar_campo(
        2,
        0,
        "Fecha de nacimiento * (AAAA-MM-DD)",
        placeholder="Ej: 2022-03-15",
    )
    entry_peso = agregar_campo(
        2, 1, "Peso (kg) *", placeholder="Ej: 450"
    )
    entry_color = agregar_campo(
        3, 0, "Color", placeholder="Ej: Blanco y negro"
    )
    combo_proposito = agregar_campo(
        3, 1, "Propósito *", tipo="combo", valores=PROPOSITOS
    )
    combo_origen = agregar_campo(
        4, 0, "Origen *", tipo="combo", valores=ORIGENES
    )
    entry_procedencia = agregar_campo(
        4,
        1,
        "Procedencia",
        placeholder="Granja o lugar de donde vino",
    )
    entry_fecha_ingreso = agregar_campo(
        5,
        0,
        "Fecha de ingreso (AAAA-MM-DD)",
        placeholder="Hoy",
    )
    combo_estado = agregar_campo(
        5, 1, "Estado *", tipo="combo", valores=ESTADOS
    )
    texto_observaciones = agregar_campo(
        6, 0, "Observaciones", tipo="texto", columnspan=2
    )

    combo_proposito.set("Doble propósito")
    combo_raza.set("Mestizo")
    entry_fecha_ingreso.insert(0, date.today().isoformat())

    mensaje = ctk.CTkLabel(
        panel,
        text="",
        font=("Arial", 15),
        text_color="red",
        wraplength=860,
    )
    mensaje.pack(pady=(2, 0))

    marco_botones = ctk.CTkFrame(panel, fg_color="transparent")
    marco_botones.pack(pady=(6, 14))

    def actualizar_procedencia(valor):
        if valor == "Criado en la granja":
            entry_procedencia.configure(state="normal")
            entry_procedencia.delete(0, "end")
            entry_procedencia.configure(state="disabled")
        else:
            entry_procedencia.configure(state="normal")

    combo_origen.configure(command=actualizar_procedencia)

    def limpiar():
        entry_identificacion.delete(0, "end")
        entry_nombre.delete(0, "end")
        combo_raza.set("Mestizo")
        combo_sexo.set("Hembra")
        entry_fecha_nacimiento.delete(0, "end")
        entry_peso.delete(0, "end")
        entry_color.delete(0, "end")
        combo_proposito.set("Doble propósito")
        combo_origen.set("Criado en la granja")
        actualizar_procedencia("Criado en la granja")
        entry_fecha_ingreso.delete(0, "end")
        entry_fecha_ingreso.insert(0, date.today().isoformat())
        combo_estado.set("Activo")
        texto_observaciones.delete("1.0", "end")
        mensaje.configure(text="")
        entry_identificacion.focus_set()

    def guardar():
        identificacion = entry_identificacion.get().strip()
        nombre = entry_nombre.get().strip()
        raza = combo_raza.get().strip()
        sexo = combo_sexo.get().strip()
        fecha_nacimiento_texto = entry_fecha_nacimiento.get().strip()
        peso_texto = entry_peso.get().strip().replace(",", ".")
        color = entry_color.get().strip()
        proposito = combo_proposito.get().strip()
        origen = combo_origen.get().strip()
        procedencia = entry_procedencia.get().strip()
        fecha_ingreso_texto = entry_fecha_ingreso.get().strip()
        estado = combo_estado.get().strip()
        observaciones = texto_observaciones.get("1.0", "end-1c").strip()

        def mostrar_error(texto):
            mensaje.configure(text=texto, text_color="red")

        if not identificacion:
            return mostrar_error("La identificación o arete es obligatoria.")
        if not nombre:
            return mostrar_error("El nombre del animal es obligatorio.")
        if not raza:
            return mostrar_error("La raza es obligatoria.")
        if sexo not in SEXOS:
            return mostrar_error("Selecciona un sexo válido.")
        if proposito not in PROPOSITOS:
            return mostrar_error("Selecciona un propósito válido.")
        if origen not in ORIGENES:
            return mostrar_error("Selecciona un origen válido.")
        if estado not in ESTADOS:
            return mostrar_error("Selecciona un estado válido.")

        nacimiento = validar_fecha(fecha_nacimiento_texto)
        if nacimiento is None:
            return mostrar_error(
                "La fecha de nacimiento debe tener el formato AAAA-MM-DD."
            )
        if nacimiento > date.today():
            return mostrar_error("La fecha de nacimiento no puede ser futura.")

        fecha_ingreso_texto = fecha_ingreso_texto or date.today().isoformat()
        ingreso = validar_fecha(fecha_ingreso_texto)
        if ingreso is None:
            return mostrar_error(
                "La fecha de ingreso debe tener el formato AAAA-MM-DD."
            )
        if ingreso < nacimiento:
            return mostrar_error(
                "La fecha de ingreso no puede ser anterior a la de nacimiento."
            )

        try:
            peso = float(peso_texto)
        except ValueError:
            return mostrar_error("El peso debe ser un número. Ejemplo: 450 o 450,5.")
        if peso <= 0:
            return mostrar_error("El peso debe ser mayor que cero.")

        if origen != "Criado en la granja" and not procedencia:
            return mostrar_error(
                "Indica la procedencia del animal (granja o lugar de origen)."
            )
        if origen == "Criado en la granja" and not procedencia:
            procedencia = "Granja propia"

        animales = cargar_animales()
        for animal in animales:
            if (
                str(animal.get("identificacion", "")).strip().lower()
                == identificacion.lower()
            ):
                return mostrar_error(
                    "Ya existe un animal con esa identificación o arete."
                )

        ids = [
            animal.get("id")
            for animal in animales
            if isinstance(animal.get("id"), int)
        ]
        nuevo_id = max(ids, default=0) + 1

        nuevo_animal = {
            "id": nuevo_id,
            "identificacion": identificacion,
            "nombre": nombre,
            "raza": raza,
            "sexo": sexo,
            "fecha_nacimiento": nacimiento.isoformat(),
            "peso": peso,
            "color": color,
            "proposito": proposito,
            "origen": origen,
            "procedencia": procedencia,
            "fecha_ingreso": ingreso.isoformat(),
            "estado": estado,
            "observaciones": observaciones,
        }

        animales.append(nuevo_animal)
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
        mensaje.configure(
            text=f"Animal '{nombre}' registrado correctamente.",
            text_color="green",
        )

    def volver():
        try:
            formulario.destroy()
        except Exception:
            pass
        principal.ventana_registro_animal = None

    ctk.CTkButton(
        marco_botones,
        text="Guardar animal",
        font=("Arial", 18),
        fg_color="green",
        width=200,
        height=44,
        command=guardar,
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        marco_botones,
        text="Limpiar",
        font=("Arial", 18),
        fg_color=COLOR_BOTON,
        text_color=COLOR_TEXTO,
        width=150,
        height=44,
        command=limpiar,
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        marco_botones,
        text="Volver",
        font=("Arial", 18),
        fg_color=COLOR_BOTON,
        text_color=COLOR_TEXTO,
        width=150,
        height=44,
        command=volver,
    ).pack(side="left", padx=8)

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

    actualizar_procedencia(combo_origen.get())
    entry_identificacion.focus_set()
    formulario.focus_force()


# ============================================================
# Catálogo de animales con filtros por categorías
# ============================================================
def abrir_catalogo(principal):
    if ventana_abierta(principal, "ventana_catalogo"):
        return

    catalogo = ctk.CTkToplevel(principal)
    catalogo.title("Consulta de animales")
    catalogo.geometry("1280x720")
    catalogo.minsize(1100, 650)
    catalogo.transient(principal)
    crear_fondo(catalogo)

    panel = ctk.CTkFrame(catalogo, fg_color=COLOR_PANEL, corner_radius=18)
    panel.pack(fill="both", expand=True, padx=16, pady=16)
    panel.grid_columnconfigure(0, weight=0, minsize=330)
    panel.grid_columnconfigure(1, weight=1)
    panel.grid_rowconfigure(1, weight=1)

    encabezado = ctk.CTkFrame(panel, fg_color="transparent")
    encabezado.grid(
        row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(12, 6)
    )

    ctk.CTkLabel(
        encabezado,
        text="Consulta de animales",
        font=("Arial", 32),
        text_color=COLOR_TEXTO,
    ).pack(side="left")

    contador = ctk.CTkLabel(
        encabezado,
        text="",
        font=("Arial", 16),
        text_color="#333333",
    )
    contador.pack(side="right")

    # ---------------- Panel de filtros ----------------
    izquierdo = ctk.CTkFrame(
        panel, fg_color=COLOR_PANEL_FILTROS, corner_radius=12
    )
    izquierdo.grid(
        row=1, column=0, sticky="nsew", padx=(18, 8), pady=(0, 18)
    )

    ctk.CTkLabel(
        izquierdo,
        text="Buscar por nombre o identificación",
        font=("Arial", 15),
        text_color=COLOR_TEXTO,
        anchor="w",
    ).pack(fill="x", padx=12, pady=(12, 4))

    marco_busqueda = ctk.CTkFrame(izquierdo, fg_color="transparent")
    marco_busqueda.pack(fill="x", padx=10)

    entry_busqueda = ctk.CTkEntry(
        marco_busqueda,
        font=("Arial", 14),
        placeholder_text="Ej: Luna o AR-001",
    )
    entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 6))

    ctk.CTkButton(
        marco_busqueda,
        text="Buscar",
        font=("Arial", 14),
        width=80,
        height=32,
        command=lambda: actualizar_lista(),
    ).pack(side="left")

    entry_busqueda.bind("<Return>", lambda event: actualizar_lista())

    ctk.CTkLabel(
        izquierdo,
        text="Filtrar por categoría",
        font=("Arial", 15),
        text_color=COLOR_TEXTO,
        anchor="w",
    ).pack(fill="x", padx=12, pady=(14, 4))

    marco_categorias = ctk.CTkFrame(izquierdo, fg_color="transparent")
    marco_categorias.pack(fill="x", padx=8)
    marco_categorias.grid_columnconfigure(0, weight=1)
    marco_categorias.grid_columnconfigure(1, weight=1)

    botones_categoria = {}
    for indice, (clave, titulo) in enumerate(CAMPOS_FILTRO):
        boton = ctk.CTkButton(
            marco_categorias,
            text=titulo,
            font=("Arial", 14),
            height=32,
            fg_color=COLOR_BOTON,
            text_color=COLOR_TEXTO,
            command=lambda c=clave: seleccionar_categoria(c),
        )
        boton.grid(
            row=indice // 2,
            column=indice % 2,
            padx=3,
            pady=3,
            sticky="ew",
        )
        botones_categoria[clave] = boton

    ctk.CTkLabel(
        izquierdo,
        text="Valores de la categoría",
        font=("Arial", 15),
        text_color=COLOR_TEXTO,
        anchor="w",
    ).pack(fill="x", padx=12, pady=(14, 4))

    panel_valores = ctk.CTkScrollableFrame(
        izquierdo,
        height=230,
        fg_color="#cfe8f3",
    )
    panel_valores.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    filtro_activo = ctk.CTkLabel(
        izquierdo,
        text="Sin filtros activos",
        font=("Arial", 13),
        text_color="#333333",
        wraplength=290,
        justify="left",
    )
    filtro_activo.pack(fill="x", padx=12, pady=(0, 6))

    marco_acciones = ctk.CTkFrame(izquierdo, fg_color="transparent")
    marco_acciones.pack(fill="x", padx=8, pady=(0, 12))

    ctk.CTkButton(
        marco_acciones,
        text="Limpiar filtros",
        font=("Arial", 14),
        fg_color=COLOR_BOTON,
        text_color=COLOR_TEXTO,
        height=32,
        command=lambda: limpiar_filtros(),
    ).pack(fill="x", pady=2)

    ctk.CTkButton(
        marco_acciones,
        text="Actualizar",
        font=("Arial", 14),
        fg_color=COLOR_BOTON,
        text_color=COLOR_TEXTO,
        height=32,
        command=lambda: recargar(),
    ).pack(fill="x", pady=2)

    ctk.CTkButton(
        marco_acciones,
        text="Volver",
        font=("Arial", 14),
        fg_color=COLOR_BOTON,
        text_color=COLOR_TEXTO,
        height=32,
        command=lambda: cerrar_catalogo(),
    ).pack(fill="x", pady=2)

    # ---------------- Panel de resultados ----------------
    derecho = ctk.CTkFrame(panel, fg_color="transparent")
    derecho.grid(
        row=1, column=1, sticky="nsew", padx=(8, 18), pady=(0, 18)
    )
    derecho.grid_rowconfigure(0, weight=1)
    derecho.grid_columnconfigure(0, weight=1)

    marco_tabla = ctk.CTkFrame(derecho, fg_color="white", corner_radius=10)
    marco_tabla.grid(row=0, column=0, sticky="nsew")
    marco_tabla.grid_rowconfigure(0, weight=1)
    marco_tabla.grid_columnconfigure(0, weight=1)

    estilo = ttk.Style()
    try:
        estilo.theme_use("clam")
    except Exception:
        pass
    estilo.configure(
        "Animales.Treeview",
        background="white",
        foreground="black",
        fieldbackground="white",
        rowheight=28,
        font=("Arial", 12),
    )
    estilo.configure(
        "Animales.Treeview.Heading",
        font=("Arial", 12, "bold"),
        background=COLOR_FONDO,
        foreground="black",
    )

    columnas = [
        ("id", "ID", 45),
        ("identificacion", "Identificación", 120),
        ("nombre", "Nombre", 120),
        ("raza", "Raza", 105),
        ("sexo", "Sexo", 70),
        ("edad", "Edad", 110),
        ("peso", "Peso (kg)", 80),
        ("origen", "Origen", 140),
        ("estado", "Estado", 80),
    ]

    tabla = ttk.Treeview(
        marco_tabla,
        columns=[columna[0] for columna in columnas],
        show="headings",
        style="Animales.Treeview",
    )
    for clave, titulo, ancho in columnas:
        tabla.heading(clave, text=titulo)
        tabla.column(clave, width=ancho, anchor="w", stretch=True)

    barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.grid(row=0, column=0, sticky="nsew")
    barra.grid(row=0, column=1, sticky="ns")

    detalle = ctk.CTkTextbox(
        derecho,
        height=190,
        font=("Arial", 14),
        wrap="word",
    )
    detalle.grid(row=1, column=0, sticky="ew", pady=(8, 0))
    detalle.configure(state="disabled")

    # ---------------- Estado y lógica de filtros ----------------
    filtros = {clave: None for clave, _ in CAMPOS_FILTRO}
    categoria_actual = None
    animales_filtrados = []

    def poner_detalle(texto):
        detalle.configure(state="normal")
        detalle.delete("1.0", "end")
        detalle.insert("1.0", texto)
        detalle.configure(state="disabled")

    def actualizar_filtro_activo():
        partes = []
        if entry_busqueda.get().strip():
            partes.append(f"Texto: {entry_busqueda.get().strip()}")
        for clave, titulo in CAMPOS_FILTRO:
            if filtros[clave]:
                partes.append(f"{titulo}: {filtros[clave]}")
        filtro_activo.configure(
            text="\n".join(partes) if partes else "Sin filtros activos"
        )

    def actualizar_lista():
        nonlocal animales_filtrados
        todos = cargar_animales()
        animales_filtrados = filtrar_animales(
            todos, filtros, entry_busqueda.get()
        )

        filas = tabla.get_children()
        if filas:
            tabla.delete(*filas)
        for indice, animal in enumerate(animales_filtrados):
            tabla.insert(
                "",
                "end",
                iid=str(indice),
                values=(
                    animal.get("id", ""),
                    animal.get("identificacion", ""),
                    animal.get("nombre", ""),
                    animal.get("raza", ""),
                    animal.get("sexo", ""),
                    calcular_edad(animal.get("fecha_nacimiento")),
                    formatear_peso(animal.get("peso")),
                    animal.get("origen", ""),
                    animal.get("estado", ""),
                ),
            )

        contador.configure(
            text=f"{len(animales_filtrados)} de {len(todos)} animales"
        )
        actualizar_filtro_activo()

        if animales_filtrados:
            poner_detalle(
                "Selecciona un animal de la lista para ver su hoja técnica."
            )
        else:
            poner_detalle("No hay animales que coincidan con los filtros.")

    def mostrar_seleccion(event=None):
        seleccion = tabla.selection()
        if not seleccion:
            return
        try:
            indice = int(seleccion[0])
        except ValueError:
            return
        if 0 <= indice < len(animales_filtrados):
            poner_detalle(formatear_hoja(animales_filtrados[indice]))

    def aplicar_valor(valor):
        if categoria_actual is None:
            return
        filtros[categoria_actual] = valor
        actualizar_lista()

    def seleccionar_categoria(categoria):
        nonlocal categoria_actual
        categoria_actual = categoria

        for clave, boton in botones_categoria.items():
            boton.configure(
                fg_color=COLOR_BOTON_ACTIVO if clave == categoria else COLOR_BOTON
            )

        for hijo in panel_valores.winfo_children():
            hijo.destroy()

        valores = valores_categoria(cargar_animales(), categoria)

        ctk.CTkButton(
            panel_valores,
            text="Todos",
            font=("Arial", 14),
            height=30,
            fg_color="#9ecfe3",
            text_color=COLOR_TEXTO,
            command=lambda: aplicar_valor(None),
        ).pack(fill="x", padx=4, pady=2)

        if valores:
            for valor in valores:
                ctk.CTkButton(
                    panel_valores,
                    text=valor,
                    font=("Arial", 14),
                    height=30,
                    fg_color=COLOR_BOTON,
                    text_color=COLOR_TEXTO,
                    command=lambda v=valor: aplicar_valor(v),
                ).pack(fill="x", padx=4, pady=2)
        else:
            ctk.CTkLabel(
                panel_valores,
                text="Sin valores registrados",
                font=("Arial", 13),
                text_color="#555555",
            ).pack(pady=10)

    def limpiar_filtros():
        nonlocal categoria_actual
        for clave in filtros:
            filtros[clave] = None
        entry_busqueda.delete(0, "end")
        categoria_actual = None

        for boton in botones_categoria.values():
            boton.configure(fg_color=COLOR_BOTON)

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

    tabla.bind("<<TreeviewSelect>>", mostrar_seleccion)
    catalogo.protocol("WM_DELETE_WINDOW", cerrar_catalogo)
    principal.ventana_catalogo = catalogo

    # Referencias y funciones útiles para pruebas y para refrescar la vista.
    catalogo.tabla = tabla
    catalogo.entry_busqueda = entry_busqueda
    catalogo.panel_valores = panel_valores
    catalogo.detalle = detalle
    catalogo.contador = contador
    catalogo.filtros = filtros
    catalogo.botones_categoria = botones_categoria
    catalogo.actualizar_lista = actualizar_lista
    catalogo.seleccionar_categoria = seleccionar_categoria
    catalogo.aplicar_valor = aplicar_valor
    catalogo.limpiar_filtros = limpiar_filtros
    catalogo.mostrar_seleccion = mostrar_seleccion
    catalogo.recargar = recargar

    actualizar_lista()
    catalogo.focus_force()


# ============================================================
# Facturación
# ============================================================
def abrir_facturacion(principal):
    if ventana_abierta(principal, "ventana_factura"):
        return

    factura = ctk.CTkToplevel(principal)
    factura.title("Factura")
    factura.geometry("1280x720")
    factura.minsize(1000, 650)
    factura.transient(principal)
    crear_fondo(factura)

    entry_granja = ctk.CTkEntry(
        factura,
        font=("Arial", 20),
        width=420,
        height=50,
        placeholder_text="Granja",
    )
    entry_granja.place(relx=0.2, rely=0.25, anchor="center")

    entry_vacas = ctk.CTkEntry(
        factura,
        font=("Arial", 20),
        width=420,
        height=50,
        placeholder_text="Número de vacas",
    )
    entry_vacas.place(relx=0.2, rely=0.37, anchor="center")

    entry_precio = ctk.CTkEntry(
        factura,
        font=("Arial", 20),
        width=420,
        height=50,
        placeholder_text="Precio por libra",
    )
    entry_precio.place(relx=0.2, rely=0.49, anchor="center")

    caja_factura = ctk.CTkTextbox(
        factura,
        width=620,
        height=450,
        font=("Arial", 18),
        wrap="none",
    )
    caja_factura.place(relx=0.67, rely=0.5, anchor="center")
    caja_factura.insert(
        "1.0", "Aquí aparecerá la factura cuando pulses Generar."
    )
    caja_factura.configure(state="disabled")

    mensaje = ctk.CTkLabel(
        factura, text="", font=("Arial", 15), text_color="red"
    )
    mensaje.place(relx=0.2, rely=0.61, anchor="center")

    def mostrar(texto):
        caja_factura.configure(state="normal")
        caja_factura.delete("1.0", "end")
        caja_factura.insert("1.0", texto)
        caja_factura.configure(state="disabled")

    def archivos():
        granja = entry_granja.get().strip()
        vacas = entry_vacas.get().strip()
        precio = entry_precio.get().strip().replace(",", ".")

        if not granja or not vacas or not precio:
            mensaje.configure(
                text="Llena los tres campos: granja, vacas y precio por libra."
            )
            return

        try:
            vacas = int(vacas)
            precio = float(precio)
        except ValueError:
            mensaje.configure(
                text="Las vacas deben ser un entero y el precio un número."
            )
            return

        if vacas <= 0 or precio <= 0:
            mensaje.configure(
                text="Las vacas y el precio deben ser mayores que cero."
            )
            return

        try:
            with open(RUTA_FACTURA, "r", encoding="utf-8") as archivo:
                datos = yaml.safe_load(archivo) or {}
            if not isinstance(datos, dict):
                datos = {}
        except (FileNotFoundError, yaml.YAMLError):
            datos = {}

        datos["Granja"] = granja
        datos["VACAS"] = vacas
        datos["Precio_por_libra"] = precio

        inicio = (
            "# ==========================================\n"
            "#   Facturacion Electronica De Venta\n"
            "#   Generado por MiniGan.INC\n"
            "#   Correo: MiniGan@outlook.com\n"
            "#   PQR: 3**********\n"
            "# ==========================================\n"
        )

        try:
            with open(RUTA_FACTURA, "w", encoding="utf-8") as archivo:
                archivo.write(inicio)
                yaml.dump(
                    datos,
                    archivo,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )
        except OSError as error:
            mensaje.configure(text=f"No se pudo guardar la factura: {error}")
            return

        with open(RUTA_FACTURA, "r", encoding="utf-8") as archivo:
            mostrar(archivo.read())

        mensaje.configure(text="Factura generada correctamente.", text_color="green")

    def cerrar():
        try:
            factura.destroy()
        except Exception:
            pass
        principal.ventana_factura = None

    ctk.CTkButton(
        factura,
        text="Generar",
        font=("Arial", 20),
        fg_color=COLOR_BOTON,
        text_color=COLOR_TEXTO,
        width=180,
        height=44,
        command=archivos,
    ).place(relx=0.2, rely=0.72, anchor="center")

    ctk.CTkButton(
        factura,
        text="Volver",
        font=("Arial", 18),
        fg_color=COLOR_BOTON,
        text_color=COLOR_TEXTO,
        width=140,
        height=40,
        command=cerrar,
    ).place(relx=0.88, rely=0.90, anchor="center")

    factura.protocol("WM_DELETE_WINDOW", cerrar)
    principal.ventana_factura = factura
    factura.focus_force()


# ============================================================
# Punto de entrada
# ============================================================
def main():
    root = crear_ventana_login()
    root.mainloop()


if __name__ == "__main__":
    main()
