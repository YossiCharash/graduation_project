from flask import Flask

from routes.terrorists_route import Terrorists

app = Flask(__name__)
app.register_blueprint(Terrorists)





if __name__ == '__main__':
    app.run()
