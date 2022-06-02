from flaskwebgui import FlaskUI
from epsilonpos.wsgi import application

FlaskUI(application).run()