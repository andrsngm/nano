from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import func, select
from config import Config
from database import db, Usuario, Tutor, Joven, Configuracion

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    with app.app_context():
        db.create_all()
        # Inicialización de datos maestros
        if not db.session.execute(select(Usuario).filter_by(username='admin')).scalar_one_or_none():
            admin = Usuario(username='admin', password='123', rol='admin')
            db.session.add(admin)
        if not db.session.execute(select(Configuracion)).scalar_one_or_none():
            conf = Configuracion(notas_habilitadas=False)
            db.session.add(conf)
        db.session.commit()

    # --- RUTAS DE ACCESO ---
    @app.route('/')
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard' if current_user.rol == 'admin' else 'tutor_dashboard'))
        return render_template('login.html')

    @app.route('/login', methods=['POST'])
    def login_post():
        u = request.form.get('username')
        p = request.form.get('password')
        user = db.session.execute(select(Usuario).filter_by(username=u, password=p)).scalar_one_or_none()
        if user:
            login_user(user)
            return redirect(url_for('admin_dashboard' if user.rol == 'admin' else 'tutor_dashboard'))
        flash("Credenciales incorrectas", "danger")
        return redirect(url_for('login'))

    # --- RUTAS ADMINISTRADOR ---
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.rol != 'admin': return redirect(url_for('login'))
        
        raw_stats = db.session.query(
            Joven.estado,
            Joven.categoria,
            func.count(Joven.id).label('cantidad')
        ).group_by(Joven.estado, Joven.categoria).all()

        stats_procesadas = {}
        for estado, categoria, cantidad in raw_stats:
            if estado not in stats_procesadas:
                stats_procesadas[estado] = {'A': 0, 'B': 0, 'total': 0}
            
            if categoria == 'A':
                stats_procesadas[estado]['A'] = cantidad
            elif categoria == 'B':
                stats_procesadas[estado]['B'] = cantidad
            
            stats_procesadas[estado]['total'] += cantidad

        return render_template('admin/dashboard.html', 
                               total_tutores=db.session.query(Tutor).count(), 
                               total_jovenes=db.session.query(Joven).count(), 
                               config=db.session.execute(select(Configuracion)).scalar_one(),
                               stats=stats_procesadas)

    @app.route('/admin/lista_tutores')
    @login_required
    def lista_tutores():
        if current_user.rol != 'admin': return redirect(url_for('login'))
        tutores = db.session.execute(select(Tutor)).scalars().all()
        return render_template('admin/lista_tutores.html', tutores=tutores)

    @app.route('/admin/crear_tutor', methods=['GET', 'POST'])
    @login_required
    def crear_tutor():
        if current_user.rol != 'admin': return redirect(url_for('login'))
        if request.method == 'POST':
            user_tutor = request.form.get('username')
            cedula_tutor = request.form.get('cedula')
            estado_tutor = request.form.get('estado')
            
            es_tutor = request.form.get('rol_tutor')
            es_evaluador = request.form.get('rol_evaluador')
            rol_final = 'tutor_evaluador' if (es_tutor and es_evaluador) else ('evaluador' if es_evaluador else 'tutor')

            if db.session.execute(select(Usuario).filter_by(username=user_tutor)).scalar_one_or_none():
                flash(f"El nombre de usuario '{user_tutor}' ya existe.", "warning")
                return redirect(url_for('crear_tutor'))
            
            tutor_existente = db.session.execute(select(Tutor).filter_by(cedula=cedula_tutor)).scalar_one_or_none()
            if tutor_existente:
                flash(f"La cédula {cedula_tutor} ya pertenece al tutor {tutor_existente.nombre} {tutor_existente.apellido}.", "danger")
                return redirect(url_for('crear_tutor'))

            nuevo_u = Usuario(username=user_tutor, password=request.form.get('password'), rol=rol_final)
            db.session.add(nuevo_u)
            db.session.flush() 

            nuevo_t = Tutor(
                nombre=request.form.get('nombre'), 
                apellido=request.form.get('apellido'), 
                cedula=cedula_tutor, 
                telefono=request.form.get('telefono'),
                estado=estado_tutor,
                usuario_id=nuevo_u.id
            )
            db.session.add(nuevo_t)
            db.session.commit()
            flash(f"Usuario {rol_final} creado correctamente.", "success")
            return redirect(url_for('lista_tutores'))
        return render_template('admin/crear_tutor.html')

    @app.route('/admin/editar_tutor/<int:tutor_id>', methods=['POST'])
    @login_required
    def editar_tutor_admin(tutor_id):
        if current_user.rol != 'admin': return redirect(url_for('login'))
        
        tutor = db.session.get(Tutor, tutor_id)
        if tutor:
            # Actualización de datos del Tutor
            tutor.nombre = request.form.get('nombre')
            tutor.apellido = request.form.get('apellido')
            tutor.cedula = request.form.get('cedula')
            tutor.telefono = request.form.get('telefono')
            tutor.estado = request.form.get('estado')

            # --- ACTUALIZACIÓN DE CREDENCIALES (NUEVO) ---
            usuario = tutor.usuario
            nuevo_username = request.form.get('username')
            nueva_password = request.form.get('password')

            if nuevo_username:
                usuario.username = nuevo_username
            
            # Solo actualiza la contraseña si se escribió algo en el campo
            if nueva_password and nueva_password.strip() != "":
                usuario.password = nueva_password

            # --- ACTUALIZACIÓN DE ROLES ---
            es_tutor = request.form.get('rol_tutor')
            es_evaluador = request.form.get('rol_evaluador')
            
            if es_tutor and es_evaluador:
                rol_final = 'tutor_evaluador'
            elif es_evaluador:
                rol_final = 'evaluador'
            else:
                rol_final = 'tutor'
                
            usuario.rol = rol_final
            
            db.session.commit()
            flash(f"Datos y credenciales de {tutor.nombre} actualizados correctamente", "success")
        
        return redirect(url_for('lista_tutores'))

    @app.route('/admin/promocionar_fase', methods=['POST'])
    @login_required
    def promocionar_fase():
        if current_user.rol != 'admin': return redirect(url_for('login'))
        metodo = request.form.get('metodo') 
        f_act = request.form.get('fase_actual') 
        f_sig = request.form.get('fase_siguiente') 
        cant = int(request.form.get('cantidad'))
        cat = request.form.get('categoria')

        query_base = select(Joven).filter_by(fase=f_act, categoria=cat)
        
        if metodo == 'nacional':
            seleccionados = db.session.execute(query_base.order_by(Joven.nota_final.desc()).limit(cant)).scalars().all()
            for j in seleccionados: j.fase = f_sig
        else:
            estados = db.session.execute(select(Joven.estado).distinct()).scalars().all()
            for est in estados:
                seleccionados = db.session.execute(
                    query_base.filter_by(estado=est).order_by(Joven.nota_final.desc()).limit(cant)
                ).scalars().all()
                for j in seleccionados: j.fase = f_sig
                    
        db.session.commit()
        flash(f"Clasificados movidos a {f_sig}", "success")
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/ver_base_datos')
    @login_required
    def ver_base_datos():
        if current_user.rol != 'admin': return redirect(url_for('login'))
        jovenes = db.session.execute(select(Joven)).scalars().all()
        return render_template('admin/ver_base_datos.html', jovenes=jovenes)

    @app.route('/admin/editar_joven/<int:joven_id>', methods=['POST'])
    @login_required
    def editar_joven_admin(joven_id):
        if current_user.rol != 'admin': return redirect(url_for('login'))
        
        j = db.session.get(Joven, joven_id)
        if j:
            def to_float(val):
                if not val: return 0.0
                try: return float(str(val).replace('.', '').replace(',', '.'))
                except: return 0.0

            j.nombres = request.form.get('nombres').title()
            j.segundo_nombre = request.form.get('segundo_nombre').title() if request.form.get('segundo_nombre') else None
            j.apellidos = request.form.get('apellidos').title()
            j.segundo_apellido = request.form.get('segundo_apellido').title() if request.form.get('segundo_apellido') else None
            j.cedula = request.form.get('cedula')
            j.edad = int(request.form.get('edad'))
            
            sex_in = request.form.get('sexo')
            j.sexo = "Masculino" if sex_in in ['M', 'Masculino'] else "Femenino"
            
            j.telefono = request.form.get('telefono')
            j.email = request.form.get('email')
            j.escuela = request.form.get('escuela')
            j.grado = request.form.get('grado')
            j.estado = request.form.get('estado')
            j.municipio = request.form.get('municipio')
            j.parroquia = request.form.get('parroquia')
            
            j.rep_nombre1 = request.form.get('rep_nombre1').title() if request.form.get('rep_nombre1') else None
            j.rep_nombre2 = request.form.get('rep_nombre2').title() if request.form.get('rep_nombre2') else None
            j.rep_apellido1 = request.form.get('rep_apellido1').title() if request.form.get('rep_apellido1') else None
            j.rep_apellido2 = request.form.get('rep_apellido2').title() if request.form.get('rep_apellido2') else None
            j.rep_cedula = request.form.get('rep_cedula')
            j.rep_parentesco = request.form.get('rep_parentesco')
            j.rep_profesion = request.form.get('rep_profesion').title() if request.form.get('rep_profesion') else None
            j.rep_telefono = request.form.get('rep_telefono')
            
            j.fase = request.form.get('fase')
            j.categoria = request.form.get('categoria')
            j.nota_estadal = to_float(request.form.get('nota_estadal'))
            j.nota_regional = to_float(request.form.get('nota_regional'))
            j.nota_nacional = to_float(request.form.get('nota_nacional'))
            
            if j.fase == 'Estadal': j.nota_final = j.nota_estadal
            elif j.fase == 'Regional': j.nota_final = j.nota_regional
            else: j.nota_final = j.nota_nacional
            
            db.session.commit()
            flash(f"Registro de {j.nombres} actualizado correctamente", "success")
        
        return redirect(url_for('ver_base_datos'))

    # --- RUTAS TUTOR ---
    @app.route('/tutor/dashboard')
    @login_required
    def tutor_dashboard():
        if 'tutor' not in current_user.rol: return redirect(url_for('cargar_notas_lista'))
        tutor_actual = db.session.execute(select(Tutor).filter_by(usuario_id=current_user.id)).scalar_one()
        mis_jovenes = db.session.execute(select(Joven).filter_by(tutor_id=tutor_actual.id)).scalars().all()
        return render_template('tutor/dashboard.html', jovenes=mis_jovenes)

    @app.route('/tutor/registrar_joven', methods=['GET', 'POST'])
    @login_required
    def registrar_joven():
        if 'tutor' not in current_user.rol: return redirect(url_for('login'))
        
        if request.method == 'POST':
            cedula = request.form.get('cedula')
            sexo_raw = request.form.get('sexo')
            edad_str = request.form.get('edad')

            existe = db.session.execute(select(Joven).filter_by(cedula=cedula)).scalar_one_or_none()
            if existe:
                flash(f"La cédula {cedula} ya está registrada a nombre de {existe.nombres} {existe.apellidos}.", "danger")
                return redirect(url_for('registrar_joven'))

            if not sexo_raw:
                flash("El campo 'Sexo' es obligatorio.", "warning")
                return redirect(url_for('registrar_joven'))

            sexo_final = "Masculino" if sexo_raw in ['M', 'Masculino'] else "Femenino"

            tutor_perfil = db.session.execute(select(Tutor).filter_by(usuario_id=current_user.id)).scalar_one()
            edad = int(edad_str)
            
            if 15 <= edad <= 17:
                cat_asignada = 'A'
            elif 18 <= edad <= 22:
                cat_asignada = 'B'
            else:
                flash("La edad debe estar entre 15 y 22 años.", "danger")
                return redirect(url_for('registrar_joven'))

            rep_cedula = request.form.get('rep_cedula')
            if edad <= 17 and not rep_cedula:
                flash("Los datos del representante son obligatorios para menores de 18 años.", "danger")
                return redirect(url_for('registrar_joven'))

            nuevo = Joven(
                nombres=request.form.get('nombres').title(),
                segundo_nombre=request.form.get('segundo_nombre').title() if request.form.get('segundo_nombre') else None,
                apellidos=request.form.get('apellidos').title(),
                segundo_apellido=request.form.get('segundo_apellido').title() if request.form.get('segundo_apellido') else None,
                cedula=cedula,
                edad=edad,
                sexo=sexo_final,
                escuela=request.form.get('escuela'),
                grado=request.form.get('grado'),
                estado=request.form.get('estado'),
                municipio=request.form.get('municipio'),
                parroquia=request.form.get('parroquia'),
                telefono=request.form.get('telefono'),
                email=request.form.get('email'),
                talla_camisa=request.form.get('talla_camisa'),
                condicion_salud=request.form.get('condicion_salud'),
                categoria=cat_asignada,
                fase='Estadal',
                tutor_id=tutor_perfil.id,
                rep_nombre1=request.form.get('rep_nombre1').title() if request.form.get('rep_nombre1') else None,
                rep_nombre2=request.form.get('rep_nombre2').title() if request.form.get('rep_nombre2') else None,
                rep_apellido1=request.form.get('rep_apellido1').title() if request.form.get('rep_apellido1') else None,
                rep_apellido2=request.form.get('rep_apellido2').title() if request.form.get('rep_apellido2') else None,
                rep_cedula=rep_cedula,
                rep_parentesco=request.form.get('rep_parentesco'),
                rep_profesion=request.form.get('rep_profesion').title() if request.form.get('rep_profesion') else None,
                rep_telefono=request.form.get('rep_telefono'),
                rep_estado=request.form.get('rep_estado'),
                rep_municipio=request.form.get('rep_municipio'),
                rep_parroquia=request.form.get('rep_parroquia')
            )
            
            db.session.add(nuevo)
            db.session.commit()
            flash(f"Joven registrado exitosamente en Categoría {cat_asignada}", "success")
            return redirect(url_for('tutor_dashboard'))
            
        return render_template('tutor/registrar_joven.html')

    @app.route('/tutor/editar_joven/<int:joven_id>', methods=['POST'])
    @login_required
    def editar_joven_tutor(joven_id):
        if 'tutor' not in current_user.rol: return redirect(url_for('login'))
        tutor_perfil = db.session.execute(select(Tutor).filter_by(usuario_id=current_user.id)).scalar_one()
        j = db.session.get(Joven, joven_id)
        
        if j and j.tutor_id == tutor_perfil.id:
            j.nombres = request.form.get('nombres').title()
            j.segundo_nombre = request.form.get('segundo_nombre').title() if request.form.get('segundo_nombre') else None
            j.apellidos = request.form.get('apellidos').title()
            j.segundo_apellido = request.form.get('segundo_apellido').title() if request.form.get('segundo_apellido') else None
            j.cedula = request.form.get('cedula')
            j.edad = int(request.form.get('edad'))
            
            sex_in = request.form.get('sexo')
            j.sexo = "Masculino" if sex_in in ['M', 'Masculino'] else "Femenino"
            
            j.telefono = request.form.get('telefono')
            j.email = request.form.get('email')
            j.escuela = request.form.get('escuela')
            j.grado = request.form.get('grado')
            j.estado = request.form.get('estado')
            j.municipio = request.form.get('municipio')
            j.parroquia = request.form.get('parroquia')
            
            j.rep_nombre1 = request.form.get('rep_nombre1').title() if request.form.get('rep_nombre1') else None
            j.rep_nombre2 = request.form.get('rep_nombre2').title() if request.form.get('rep_nombre2') else None
            j.rep_apellido1 = request.form.get('rep_apellido1').title() if request.form.get('rep_apellido1') else None
            j.rep_apellido2 = request.form.get('rep_apellido2').title() if request.form.get('rep_apellido2') else None
            j.rep_cedula = request.form.get('rep_cedula')
            j.rep_telefono = request.form.get('rep_telefono')
            j.rep_parentesco = request.form.get('rep_parentesco')
            
            if 15 <= j.edad <= 17: j.categoria = 'A'
            elif 18 <= j.edad <= 22: j.categoria = 'B'

            db.session.commit()
            flash(f"Datos de {j.nombres} actualizados correctamente.", "success")
        else:
            flash("Acceso no autorizado.", "danger")
        return redirect(url_for('tutor_dashboard'))

    @app.route('/tutor/eliminar_joven/<int:joven_id>', methods=['POST'])
    @login_required
    def eliminar_joven_tutor(joven_id):
        if 'tutor' not in current_user.rol: return redirect(url_for('login'))
        tutor_perfil = db.session.execute(select(Tutor).filter_by(usuario_id=current_user.id)).scalar_one()
        j = db.session.get(Joven, joven_id)
        if j and j.tutor_id == tutor_perfil.id:
            db.session.delete(j)
            db.session.commit()
            flash("Participante eliminado.", "warning")
        return redirect(url_for('tutor_dashboard'))

    @app.route('/evaluador/cargar_notas')
    @login_required
    def cargar_notas_lista():
        if 'evaluador' not in current_user.rol: return redirect(url_for('login'))
        jovenes = db.session.execute(select(Joven)).scalars().all()
        config = db.session.execute(select(Configuracion)).scalar_one()
        return render_template('evaluador/lista_notas.html', jovenes=jovenes, config=config)

    @app.route('/evaluador/guardar_nota/<int:joven_id>', methods=['POST'])
    @login_required
    def guardar_nota(joven_id):
        joven = db.session.get(Joven, joven_id)
        nota_raw = request.form.get('nota')
        nota_str = nota_raw.replace('.', '').replace(',', '.')
        nota = float(nota_str)
        
        if joven.fase == 'Estadal': joven.nota_estadal = nota
        elif joven.fase == 'Regional': joven.nota_regional = nota
        else: joven.nota_nacional = nota
        
        joven.nota_final = nota
        db.session.commit()
        return redirect(url_for('cargar_notas_lista'))

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)