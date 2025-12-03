import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:MYSQL123@localhost:3306/uir_presence'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail Configuration for Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'oumaimajabrane23@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')   # À remplacer par le mot de passe d'application
    MAIL_DEFAULT_SENDER = 'oumaimajabrane23@gmail.com'
