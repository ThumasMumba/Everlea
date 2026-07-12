from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Instantiated here (not in app.py) so models.py and app.py can both
# import them without creating a circular import.
db = SQLAlchemy()
login_manager = LoginManager()
