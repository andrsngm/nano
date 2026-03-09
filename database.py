from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # Roles: 'admin', 'tutor', 'evaluador', 'tutor_evaluador'
    rol = db.Column(db.String(30), nullable=False) 
    
    # Relación uno a uno
    tutor_perfil = db.relationship('Tutor', backref='usuario', uselist=False)

class Tutor(db.Model):
    __tablename__ = 'tutor'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    
    # --- MODIFICACIÓN AQUÍ ---
    # Agregamos el estado al perfil del tutor
    estado = db.Column(db.String(50), nullable=True) 
    # -------------------------
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Relación: tutor.jovenes -> lista de jóvenes
    jovenes = db.relationship('Joven', backref='tutor', lazy=True)

class Joven(db.Model):
    __tablename__ = 'jovenes'
    id = db.Column(db.Integer, primary_key=True)
    
    # --- Identificación del Joven ---
    nombres = db.Column(db.String(100), nullable=False)
    segundo_nombre = db.Column(db.String(100), nullable=True)
    apellidos = db.Column(db.String(100), nullable=False)
    segundo_apellido = db.Column(db.String(100), nullable=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    sexo = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    
    # --- Educación ---
    escuela = db.Column(db.String(200), nullable=False)
    grado = db.Column(db.String(50), nullable=False)
    
    # --- Estructura de Olimpiada ---
    categoria = db.Column(db.String(10), nullable=False) # 'A' o 'B'
    fase = db.Column(db.String(20), default='Estadal')
    
    # --- Ubicación ---
    estado = db.Column(db.String(50), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    parroquia = db.Column(db.String(100), nullable=False)
    
    # --- Logística ---
    talla_camisa = db.Column(db.String(5), nullable=True)
    condicion_salud = db.Column(db.Text, nullable=True)
    
    # --- Notas ---
    nota_estadal = db.Column(db.Float, default=0.0)
    nota_regional = db.Column(db.Float, default=0.0)
    nota_nacional = db.Column(db.Float, default=0.0)
    nota_final = db.Column(db.Float, default=0.0)

    # --- DATOS DEL REPRESENTANTE ---
    rep_nombre1 = db.Column(db.String(100), nullable=True)
    rep_nombre2 = db.Column(db.String(100), nullable=True)
    rep_apellido1 = db.Column(db.String(100), nullable=True)
    rep_apellido2 = db.Column(db.String(100), nullable=True)
    rep_cedula = db.Column(db.String(20), nullable=True)
    rep_parentesco = db.Column(db.String(50), nullable=True)
    rep_profesion = db.Column(db.String(100), nullable=True)
    rep_telefono = db.Column(db.String(20), nullable=True)
    rep_estado = db.Column(db.String(100), nullable=True)
    rep_municipio = db.Column(db.String(100), nullable=True)
    rep_parroquia = db.Column(db.String(100), nullable=True)
    
    # Relación con Tutor
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = db.Column(db.Integer, primary_key=True)
    notas_habilitadas = db.Column(db.Boolean, default=False)