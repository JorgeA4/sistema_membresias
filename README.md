# Nexum

## Ejecución

Las credenciales de MariaDB deben estar definidas en
`~/.config/nexum/nexum.env`. Cárgalas en la misma terminal desde la que se
ejecutará la aplicación:

```bash
source ~/.config/nexum/nexum.env
source .venv/bin/activate
python main.py
```

MariaDB debe estar iniciado y el valor de `NEXUM_DB_SOCKET` debe apuntar al
socket activo. Las credenciales no deben almacenarse en este repositorio.
