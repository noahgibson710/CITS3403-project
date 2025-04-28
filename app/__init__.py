from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes import main  # import the Blueprint
    app.register_blueprint(main) # register it

    return app
