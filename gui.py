from flaskwebgui import FlaskUI
from barpos.wsgi import application

FlaskUI(application).run()