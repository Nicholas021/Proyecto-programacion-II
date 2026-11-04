from PIL import Image
import customtkinter as ctk
import json
import yaml

ctk.set_appearance_mode("light")

root = ctk.CTk()
root.title("Metodos campesinos")
root.geometry("1280x720")

imagen = Image.open("IMAGEN DE APLICACION.jpg")
foto = ctk.CTkImage(light_image=imagen, dark_image=imagen, size=(1920, 1080))

label_foto = ctk.CTkLabel(root, image=foto, text="")
label_foto.place(x=0, y=0, relwidth=1, relheight=1)
label_foto.lower()

ms = ctk.CTkLabel(root, text="Inicio de sesion", font=("Arial", 60), fg_color="transparent", bg_color="#bce2f4", text_color="black")
ms.place(relx=0.5, rely=0.15, anchor="center")

textusu = ctk.CTkLabel(root, text="Digite su Usuario", font=("Arial", 40), fg_color="transparent", bg_color="#bce2f4", text_color="black")
textusu.place(relx=0.5, rely=0.28, anchor="center")

usuario = ctk.CTkEntry(root, font=("Arial", 40), fg_color="transparent", border_color="", text_color="black", width=400)
usuario.place(relx=0.5, rely=0.38, anchor="center")

textc = ctk.CTkLabel(root, text="Digite su contraseña", font=("Arial", 40), fg_color="transparent", bg_color="#bce2f4", text_color="black")
textc.place(relx=0.5, rely=0.50, anchor="center")

contraseña = ctk.CTkEntry(root, font=("Arial", 40), fg_color="transparent", border_color="", text_color="black", show="*", width=400)
contraseña.place(relx=0.5, rely=0.60, anchor="center")

#========================================================================================

def cargar_usuarios():
    try:
        with open('Cuentas.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def registro():
    root.withdraw()

    sesiones = ctk.CTk()
    sesiones.title("Crear usuario")
    sesiones.geometry("800x600")
    sesiones.config(background="lightblue")

    usuarionuevo = ctk.CTkLabel(sesiones,text="Ingrese su nuevo usuario",font=("Arial", 40),text_color="black")
    usuarionuevo.place(relx=0.5, rely=0.20, anchor="center")

    nuevousuario = ctk.CTkEntry(sesiones, font=("Arial", 20), width=400)
    nuevousuario.place(relx=0.5, rely=0.30, anchor="center")

    contraseñanueva = ctk.CTkLabel(sesiones,text="Ingrese su contraseña",font=("Arial", 40),text_color="black")
    contraseñanueva.place(relx=0.5, rely=0.45, anchor="center")

    nuevacontraseña = ctk.CTkEntry(sesiones, font=("Arial", 20), width=400, show="*")
    nuevacontraseña.place(relx=0.5, rely=0.55, anchor="center")

    def guardar_y_cerrar():
        nombre_usuario = nuevousuario.get()
        clave_usuario = nuevacontraseña.get()

        if nombre_usuario != "" and clave_usuario != "":
            cuentas = cargar_usuarios()
            cuentas[nombre_usuario] = clave_usuario

            with open('Cuentas.json', 'w', encoding='utf-8') as file:
                json.dump(cuentas, file, indent=4, ensure_ascii=False)

            sesiones.destroy()
            root.deiconify()
        else:
            print("Por favor, llena ambos campos.")


    terminarinicio = ctk.CTkButton(sesiones,text="Terminar usuario",font=("Arial", 30),fg_color="green",width=400,height=50,command=guardar_y_cerrar)
    terminarinicio.place(relx=0.5, rely=0.75, anchor="center")

    sesiones.mainloop()

boton_ingresar = ctk.CTkButton(root, text="Iniciar sesión", font=("Arial", 30), fg_color="lightblue", text_color="black", width=400, height=50, command=lambda: usua())
boton_ingresar.place(relx=0.5, rely=0.72, anchor="center")

crear = ctk.CTkButton(root, text="Crear usuario", font=("Arial", 30), width=400, height=50, command=registro)
crear.place(relx=0.5, rely=0.82, anchor="center")


#========================================================================================================

def ventana():
    root.destroy()
    principal = ctk.CTk()
    principal.title("Menu Principal")
    principal.geometry("1280x720")

    imagen = Image.open("IMAGEN DE APLICACION.jpg")
    foto = ctk.CTkImage(light_image=imagen, dark_image=imagen, size=(1920, 1080))

    label_foto = ctk.CTkLabel(principal, image=foto, text="")
    label_foto.place(x=0, y=0, relwidth=1, relheight=1)
    label_foto.lower()

    ctk.CTkLabel(principal, text="Menu principal", font=("Arial", 40)).pack(pady=50)

# sesion = ctk.CTkLabel(principal, text=(),font=("Arial",15),bg_color="#bce2f4", text_color="black",width=400,height=50)
#sesion.place(relx=0.9, rely=0.1, anchor="center")

    insertar_animal = ctk.CTkButton(principal,text="Registrar animal",font=("Arial",30),bg_color="#bce2f4",width=400,height=50,command=lambda:insertar())
    insertar_animal.place(relx=0.2, rely=0.45, anchor="center")

    consulta = ctk.CTkButton(principal,text="Consulta animales",font=("Arial",30),bg_color="#bce2f4",width=400,height=50,command=lambda: catalogo())
    consulta.place(relx=0.2, rely=0.2, anchor="center")

    datos = ctk.CTkButton(principal,text="Generar factura",font=("Arial",30),bg_color="#bce2f4",width=400,height=50,command=lambda: facturacion())
    datos.place(relx=0.2, rely=0.35, anchor="center")


    def volver():
        for w in principal.winfo_children():
            if isinstance(w, ctk.CTkToplevel):
                w.destroy()
        principal.deiconify()

    def catalogo():
        principal.withdraw()
        especies = ctk.CTkToplevel(principal)
        especies.title("Consulta")
        especies.geometry("1280x720")

        imagen = Image.open("IMAGEN DE APLICACION.jpg")
        foto = ctk.CTkImage(light_image=imagen, dark_image=imagen, size=(1920, 1080))

        label_foto = ctk.CTkLabel(especies, image=foto, text="")
        label_foto.place(x=0, y=0, relwidth=1, relheight=1)
        label_foto.lower()

        buscar = ctk.CTkLabel(especies,text="Digita el animal que deseas buscar: ",font=("Arial",30),bg_color="#bce2f4", text_color="black",width=400,height=50)
        buscar.place(relx=0.2, rely=0.2, anchor="center")


        caja_datos = ctk.CTkTextbox(especies, width=500, height=300, font=("Arial", 20), wrap="none")
        caja_datos.place(relx=0.5, rely=0.55, anchor="center")
        caja_datos.insert("1.0", "Selecciona un género para ver la información.")
        caja_datos.configure(state="disabled")

        def click(genero):

            try:
                with open("Hoja_datos.json", "r", encoding="utf-8") as file:
                    datos_json = json.load(file)
                    texto_ordenado = json.dumps(datos_json, indent=4, ensure_ascii=False)

            except FileNotFoundError:
                texto_ordenado = "Error: No se encontró el archivo 'Hoja_datos.json'"

            except json.JSONDecodeError:
                texto_ordenado = "Error: El archivo JSON está mal estructurado o vacío."

            caja_datos.configure(state="normal")
            caja_datos.delete("1.0", "end")
            caja_datos.insert("1.0", texto_ordenado)
            caja_datos.configure(state="disabled")


        opciones = ["Masculino", "Femenino"]
        combo = ctk.CTkComboBox(especies,values=opciones,state="readonly",width=400,height=50,bg_color="#bce2f4",command=click)
        combo.set("GENERO")
        combo.place(relx=0.8,rely=0.2,anchor="center")
        combo.configure(width=200, height=40)


        regresar = ctk.CTkButton(especies,text=("Volver"),font=("Arial",30),bg_color="#bce2f4", text_color="black",width=400,height=50,command=volver)
        regresar.place(relx=0.9, rely=0.8, anchor="center")
        regresar.configure(width=30, height=40)

        especies.mainloop()


    def facturacion():

        principal.withdraw()
        factura = ctk.CTkToplevel(principal)
        factura.title("Factura")
        factura.geometry("1280x720")
        factura.protocol("WM_DELETE_WINDOW", volver)

        label_foto = ctk.CTkLabel(factura, image=foto, text="")
        label_foto.place(x=0, y=0, relwidth=1, relheight=1)
        label_foto.lower()

        entry_granja = ctk.CTkEntry(factura, font=("Arial",20), width=400, height=50, placeholder_text="Granja")
        entry_granja.place(relx=0.2, rely=0.25, anchor="center")

        entry_vacas = ctk.CTkEntry(factura, font=("Arial",20), width=400, height=50, placeholder_text="Número de vacas")
        entry_vacas.place(relx=0.2, rely=0.37, anchor="center")

        entry_precio = ctk.CTkEntry(factura, font=("Arial",20), width=400, height=50, placeholder_text="Precio por libra")
        entry_precio.place(relx=0.2, rely=0.49, anchor="center")

        caja_factura = ctk.CTkTextbox(factura, width=600, height=450, font=("Arial", 20), wrap="none")
        caja_factura.place(relx=0.65, rely=0.5, anchor="center")
        caja_factura.insert("1.0", "Aquí aparecerá la factura cuando pulses Generar.")
        caja_factura.configure(state="disabled")

        def mostrar(texto):
            caja_factura.configure(state="normal")
            caja_factura.delete("1.0", "end")
            caja_factura.insert("1.0", texto)
            caja_factura.configure(state="disabled")

        def archivos():

            granja = entry_granja.get().strip()
            vacas = entry_vacas.get().strip()
            precio = entry_precio.get().strip().replace(",", ".")

            if granja == "" or vacas == "" or precio == "":
                mostrar("Llena los tres campos: granja, vacas y precio por libra.")
                return

            try:
                vacas = int(vacas)
                precio = float(precio)
            except ValueError:
                mostrar("Las vacas deben ser un número entero y el precio un número (ej: 8500).")
                return

            try:
                with open('nuevo.txt', 'r', encoding="utf-8") as f:
                    datos = yaml.safe_load(f) or {}
            except FileNotFoundError:
                datos = {}

            datos["Granja"] = granja
            datos["VACAS"] = vacas
            datos["Precio_por_libra"] = precio

            inicio = ("# ==========================================\n"
                      "#   Facturacion Electronica De Venta\n"
                      "#   Generado por MiniGan.INC\n"
                      "#   Correo: MiniGan.Outlook.com\n"
                      "#   PQR: 3**********\n"
                      "# ==========================================\n")

            with open('nuevo.txt', "w", encoding="utf-8") as f:
                f.write(inicio)
                yaml.dump(datos, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            with open('nuevo.txt', 'r', encoding="utf-8") as f:
                mostrar(f.read())

        generacion = ctk.CTkButton(factura,text=("Generar"),font=("Arial",20),bg_color="#bce2f4", text_color="black",width=150,height=40,command=lambda:archivos())
        generacion.place(relx=0.2, rely=0.70, anchor="center")

        regresar = ctk.CTkButton(factura,text=("Volver"),font=("Arial",30),bg_color="#bce2f4", text_color="black",width=140,height=40,command=volver)
        regresar.place(relx=0.9, rely=0.9, anchor="center")

    def insertar():

        with open("Hoja_datos.json", "w", encoding="utf-8") as archivo:

            json.load(archivo, indent=4)





    principal.mainloop()


#=====================================================================================


errorusuario = None
errorcontraseña = None

def usua(event=None):
    global errorusuario, errorcontraseña

    if errorusuario is not None:
        errorusuario.destroy()
        errorusuario = None
    if errorcontraseña is not None:
        errorcontraseña.destroy()
        errorcontraseña = None

    textoin = usuario.get()
    textoini = contraseña.get()
    usuarios = cargar_usuarios()

    if textoin in usuarios:
        if usuarios[textoin] == textoini:
            ventana()
        else:
            usuario.configure(border_color="", text_color="black")
            contraseña.configure(border_color="red", text_color="red")
            errorcontraseña = ctk.CTkLabel(root, text="Contraseña incorrecta", font=("Arial", 40), text_color="red", fg_color="transparent")
            errorcontraseña.place(relx=0.5, rely=0.92, anchor="center")
    else:
        usuario.configure(border_color="red", text_color="red")
        contraseña.configure(border_color="red", text_color="red")
        errorusuario = ctk.CTkLabel(root, text="Usuario incorrecto", font=("Arial", 40), text_color="red", fg_color="transparent")
        errorusuario.place(relx=0.5, rely=0.92, anchor="center")

usuario.bind("<Return>", usua)
contraseña.bind("<Return>", usua)

root.mainloop()