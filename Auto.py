import subprocess
import time
import os
import shutil

# --- CONFIGURACIÓN ---
ARCHIVO_SISTEMA = "run.py"
REINTENTO_SEGUNDOS = 30  # Tiempo de seguridad solicitado
CARPETA_BD = "instance"
ARCHIVO_BD = "olimpiadas_nanotecnologia.db"

def actualizar_y_vigilar():
    print("--- 🔬 SISTEMA DE REGISTRO OVN 2026 ---")
    
    # 1. Intentar bajar cambios de GitHub
    print("📥 Buscando actualizaciones en GitHub...")
    try:
        subprocess.run(["git", "pull", "origin", "main"], timeout=30)
    except Exception as e:
        print(f"⚠️ No se pudo conectar a GitHub (revisar internet): {e}")

    intentos = 0
    while True:
        intentos += 1
        print(f"\n🚀 [GUARDIÁN] Intento #{intentos} - Iniciando sistema...")
        
        # 2. Crear respaldo de seguridad antes de cada inicio
        ruta_bd = os.path.join(CARPETA_BD, ARCHIVO_BD)
        if os.path.exists(ruta_bd):
            respaldo = os.path.join(CARPETA_BD, "respaldo_automatico.db")
            shutil.copy(ruta_bd, respaldo)
            print("✅ Respaldo de base de datos creado.")

        try:
            # 3. Ejecutar el sistema de registro
            # Asegúrate de que run.py tenga app.run(host='0.0.0.0')
            proceso = subprocess.Popen(["python", ARCHIVO_SISTEMA])
            proceso.wait() 
            
            print(f"⚠️ [SISTEMA CERRADO] El proceso terminó. Reiniciando en {REINTENTO_SEGUNDOS} segundos...")
        except Exception as e:
            print(f"❌ [ERROR CRÍTICO] Falló el inicio: {e}")
        
        # Espera de seguridad
        time.sleep(REINTENTO_SEGUNDOS)

if __name__ == "__main__":
    actualizar_y_vigilar()
