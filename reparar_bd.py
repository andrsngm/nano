import sqlite3
import os

DB_PATH = r'C:\Users\Mile\source\repos\Nano\instance\olimpiadas_nanotecnologia.db'

def reparar():
    if not os.path.exists(DB_PATH):
        print(f"Archivo no encontrado en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lista de columnas que SQLAlchemy está buscando y no encuentra
    columnas = [
        "rep_nombre1", "rep_nombre2", "rep_apellido1", "rep_apellido2",
        "rep_cedula", "rep_parentesco", "rep_profesion", "rep_telefono",
        "rep_estado", "rep_municipio", "rep_parroquia"
    ]
    
    print("Iniciando reparación de la tabla 'jovenes'...")
    
    for col in columnas:
        try:
            # Intentamos agregar la columna a la tabla 'jovenes'
            cursor.execute(f"ALTER TABLE jovenes ADD COLUMN {col} TEXT")
            print(f"✅ Columna '{col}' agregada exitosamente.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"ℹ️ La columna '{col}' ya existía.")
            else:
                print(f"❌ Error en '{col}': {e}")
    
    conn.commit()
    conn.close()
    print("\nSincronización terminada. Reinicia tu app Flask ahora.")

if __name__ == "__main__":
    reparar()