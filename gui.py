from flaskwebgui import FlaskUI
from config.wsgi import application

FlaskUI(application).run()