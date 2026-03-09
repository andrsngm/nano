from app import app, db, Usuario  # Ajusta 'Usuario' al nombre de tu modelo
from werkzeug.security import generate_password_hash

def cambiar_credenciales():
    with app.app_context():
        # 1. Buscamos al usuario actual
        admin_actual = Usuario.query.filter_by(username='admin').first()
        
        if admin_actual:
            print("--- Iniciando cambio de credenciales ---")
            
            # 2. Definimos los nuevos datos
            # RECOMENDACIÓN: No uses 'admin' como nombre de usuario por seguridad
            nuevo_usuario = "admin" 
            nueva_clave = "Usuario-Administrador1" # Cambia esto por tu clave real
            
            # 3. Aplicamos los cambios con hashing
            admin_actual.username = nuevo_usuario
            admin_actual.password = generate_password_hash(nueva_clave)
            
            try:
                db.session.commit()
                print(f"ÉXITO: El usuario ahora es '{nuevo_usuario}'")
                print("La contraseña ha sido encriptada y actualizada.")
            except Exception as e:
                db.session.rollback()
                print(f"ERROR al guardar en base de datos: {e}")
        else:
            print("ERROR: No se encontró ningún usuario con el nombre 'admin'.")

if __name__ == "__main__":
    cambiar_credenciales()