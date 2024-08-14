from flask import Flask
import secrets
from flask_bcrypt import Bcrypt

app = Flask(__name__)
secret_key_urlsafe = secrets.token_urlsafe(16)
app.secret_key = secret_key_urlsafe

bcrypt = Bcrypt(app)