# Nexum

## Ejecución en Linux con LAMPP

Abre una terminal en la carpeta del proyecto y ejecuta los comandos en este
orden:

```bash
sudo /opt/lampp/lampp startmysql
source ~/.config/nexum/nexum.env
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

El archivo de credenciales debe definir las variables de entorno de MariaDB,
incluido `NEXUM_DB_SOCKET` con la ruta del socket activo. Las credenciales no
deben almacenarse en este repositorio.

Para detener MariaDB cuando termines:

```bash
sudo /opt/lampp/lampp stopmysql
```

## Ejecución en Windows con XAMPP

Abre `Símbolo del sistema` o PowerShell en la carpeta del proyecto. Inicia
XAMPP y ejecuta el sistema con los siguientes comandos:

```powershell
C:\xampp\xampp_start.exe
.venv\Scripts\activate
pip install -r requirements.txt
py main.py
```

También puedes iniciar Apache y MySQL desde el panel de control de XAMPP.

Para detener XAMPP desde la terminal:

```powershell
C:\xampp\xampp_stop.exe
```
