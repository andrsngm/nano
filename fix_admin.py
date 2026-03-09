import sqlite3
from werkzeug.security import generate_password_hash
import os

DB_NAME = "instance/olimpiadas_nanotecnologia.db"

def restaurar_acceso():
    if not os.path.exists(DB_NAME):
        print(f"❌ Error: No se encuentra el archivo {DB_NAME}")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Generamos un hash limpio para la clave 12345
        nueva_clave_hash = generate_password_hash("Usuario-Administrador1")
        
        # 1. Intentamos actualizar cualquier usuario que sea administrador
        # 2. Si no sabemos el nombre exacto, lo forzamos por ID o buscamos el registro
        cursor.execute("UPDATE usuario SET username='admin', password=? WHERE id=1", (nueva_clave_hash,))
        
        if conn.total_changes == 0:
            # Si el paso anterior no cambió nada, intentamos por el nombre 'admin_nano_2026' que pusimos antes
            cursor.execute("UPDATE usuario SET username='admin', password=? WHERE username='admin'", (nueva_clave_hash,))

        conn.commit()
        print("✅ ACCESO RESTAURADO")
        print("---------------------------")
        print("Usuario: admin")
        print("Contraseña: Usuario-Administrador1")
        print("---------------------------")
        print("Intenta entrar ahora al panel.")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    restaurar_acceso()