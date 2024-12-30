import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '1e761ce75fdec22fa4168dc9d317a553'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'rentsafe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SEND_NOTIFICATIONS = True  
    SEND_EMAILS = True
    
    # Email server configuration
    MAIL_SERVER = 'smtp.gmail.com'  
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'agrdevanshi25@gmail.com'  
    MAIL_PASSWORD = 'ahpc vwmm pvhh axng'       
    MAIL_USE_SSL = True


    logging.basicConfig(
        level=logging.DEBUG,  
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        handlers=[
            logging.StreamHandler()         
        ]
    )