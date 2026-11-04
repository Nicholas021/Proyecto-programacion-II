# Proyecto programacion II
Aplicacion ganadera en Python (CustomTkinter) para inicio de sesion, registro de animales, consulta y generacion de facturas.

## Requisitos

```
pip install customtkinter Pillow PyYAML
```

## Ejecucion

```
python "Aplicacion PROGRA ll.py"
```

## Cuentas y contraseñas

- **Archivo real:** `Cuentas.json`, en la raiz de la carpeta del proyecto.
- **No se versiona en Git:** esta incluido en `.gitignore` para no exponer contraseñas en el repositorio (ni en su historial).
- **Respaldo:** el archivo real queda respaldado por OneDrive (historial de versiones) y por cualquier copia local que hagas.
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
guardar **hashes** de las contraseñas (no texto plano) y mantener la sal en el
codigo o en una variable de entorno.

## Datos

- `Hoja_datos.json`: datos de animales (actualmente vacio; pendiente de corregir).
- `nuevo.txt`: ultima factura generada en formato YAML.
