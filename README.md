# nano
# Sistema de Registro - Olimpiada Venezolana de Nanotecnología 2026

Este sistema gestiona el registro de los 2500 jóvenes participantes, organizados por el Programa Nacional Semillero Científico.

## 🚀 Instalación
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar la aplicación: `python run.py`


## Configurar el "Encendido Automático" (El Guardián):
Para que el sistema se inicie solo al prender el servidor y se recupere de fallos, configuraremos el script auto.py en el sistema:
1. En la terminal, escribe: crontab -e
2. Baja hasta el final del archivo y pega esta línea (cambia "usuario" por el nombre real en el servidor): @reboot python3 /home/usuario/nano/auto.py &
3. Guarda y sal (Ctrl+O, Enter, Ctrl+X).
4. python auto.py

## 🛠️ Tecnologías
- **Backend:** Python / Flask
- **Base de Datos:** SQLite (olimpiadas_nanotecnologia.db)
- **Frontend:** HTML5, CSS3 y JavaScript (venezuela.js)
