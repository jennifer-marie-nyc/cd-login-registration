from flask_app import app
from flask_app.controllers.users import *

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port='5150')