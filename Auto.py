import subprocess
import time
import os

def actualizar_y_correr():
    print("--- 🔬 SISTEMA DE REGISTRO OVN 2026 ---")
    
    # 1. Intentar bajar cambios de GitHub automáticamente
    print("📥 Buscando actualizaciones en GitHub...")
    subprocess.run(["git", "pull", "origin", "main"])
    
    # 2. El Guardián inicia el sistema
    while True:
        print("\n🚀 [GUARDIÁN] Iniciando sistema en http://0.0.0.0:5000")
        try:
            # Ejecuta el sistema
            proceso = subprocess.Popen(["python", "run.py"])
            proceso.wait() 
            
            print("⚠️ [GUARDIÁN] El sistema se cerró. Reiniciando en 5 segundos...")
        except Exception as e:
            print(f"❌ [GUARDIÁN] Error: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    actualizar_y_correr()
