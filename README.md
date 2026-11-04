# Proyecto programacion II

Aplicacion ganadera de escritorio en Python + CustomTkinter para el manejo basico
de bovinos: inicio de sesion, registro de animales, consulta con filtros y
generacion de facturas.

## Funcionalidades

- Inicio de sesion y creacion de usuarios.
- **Registro de bovinos** mediante formulario con hoja tecnica basica.
- **Consulta de animales** con busqueda por nombre/identificacion y filtros por
  categorias: sexo, raza, origen, proposito, estado y color.
- **Hoja tecnica** del animal seleccionado (incluye edad calculada).
- **Generacion de factura** en formato YAML.
- Los datos se guardan en `Hoja_datos.json`; las cuentas en `Cuentas.json`.

## Requisitos

```
pip install customtkinter Pillow PyYAML
```

Probado con Python 3.14, CustomTkinter 6.0.0, Pillow 12.3.0 y PyYAML 6.0.3.

## Ejecucion

```
python "Aplicacion PROGRA ll.py"
```

Las rutas se resuelven con `Path(__file__).resolve().parent`, asi que la
aplicacion funciona aunque se ejecute desde otra carpeta.

## Registro de animales

El formulario pide:

| Campo | Obligatorio | Detalle |
|---|---|---|
| Identificacion / arete | Si | Debe ser unico |
| Nombre | Si | |
| Raza | Si | Lista editable (Holstein, Brahman, Mestizo, etc.) |
| Sexo | Si | Hembra / Macho |
| Fecha de nacimiento | Si | Formato `AAAA-MM-DD` |
| Peso | Si | Kilogramos, mayor que cero |
| Color | No | |
| Proposito | Si | Leche / Carne / Doble proposito |
| Origen | Si | Criado en la granja / Comprado / Donado / Otro |
| Procedencia | Segun origen | Obligatoria si no fue criado en la granja |
| Fecha de ingreso | No | Por defecto, la fecha actual |
| Estado | Si | Activo / Vendido / Muerto |
| Observaciones | No | |

La edad se calcula automaticamente a partir de la fecha de nacimiento.

## Consulta y filtros

- La busqueda por texto acepta parte del nombre o de la identificacion.
- Los botones de categoria muestran una lista con los valores existentes.
- Al elegir un valor se aplica el filtro; los filtros se combinan.
- **Todos** limpia la categoria actual y **Limpiar filtros** limpia todo.
- Al seleccionar una fila se muestra la hoja tecnica completa del bovino.

## Estructura de `Hoja_datos.json`

```json
{
    "animales": [
        {
            "id": 1,
            "identificacion": "AR-001",
            "nombre": "Luna",
            "raza": "Holstein",
            "sexo": "Hembra",
            "fecha_nacimiento": "2022-03-15",
            "peso": 450.0,
            "color": "Blanco y negro",
            "proposito": "Leche",
            "origen": "Criado en la granja",
            "procedencia": "Granja propia",
            "fecha_ingreso": "2022-03-15",
            "estado": "Activo",
            "observaciones": ""
        }
    ]
}
```

## Cuentas y contraseñas

- **Archivo real:** `Cuentas.json`, en la raiz de la carpeta del proyecto.
- **No se versiona en Git:** esta incluido en `.gitignore` para no exponer
  contraseñas en el repositorio (ni en su historial).
- **Plantilla versionada:** `Cuentas.ejemplo.json` muestra el formato esperado:

```json
{
    "usuario": "contrasena"
}
```

### Como acceder a las credenciales

**Desde la carpeta (recomendado):**

1. Abre `C:\Users\nicol\OneDrive\Desktop\Proyecto de progra\Proyecto programacion II\Cuentas.json`.
2. Puedes verlo con el Bloc de notas o VS Code.
3. Tambien puedes abrirlo con:

```
notepad "Cuentas.json"
```

**Desde Git:**

El archivo real no esta en Git por seguridad, asi que `git show` no lo mostrara.
En el repositorio solo esta la plantilla:

```
git show HEAD:Cuentas.ejemplo.json
```

Si en el futuro se quieren guardar las cuentas en Git, la forma correcta es
guardar **hashes** de las contraseñas (no texto plano).

## Notas de seguridad

- Las contraseñas se guardan actualmente en texto plano en `Cuentas.json`.
  Se recomienda migrar a hashes (por ejemplo, `hashlib.pbkdf2_hmac`) en una
  siguiente iteracion.
- El archivo `Cuentas.json` no debe subirse a GitHub.
