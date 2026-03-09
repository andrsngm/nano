import os

class Config:
    # Llave actualizada para el nuevo nombre
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'olimpiada_nanotecnologia_2026_secreta'
    
    # Nombre de la base de datos actualizado
    SQLALCHEMY_DATABASE_URI = 'sqlite:///olimpiadas_nanotecnologia.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False