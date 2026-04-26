from flask import Flask, redirect, url_for
from extensions import db
from config import Config
from flask_wtf.csrf import CSRFProtect
import os

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Creeaza folderul uploads daca nu exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)

    from routes.pacienti import pacienti_bp
    from routes.medici import medici_bp
    from routes.programari import programari_bp
    from routes.analiza import analiza_bp

    app.register_blueprint(pacienti_bp)
    app.register_blueprint(medici_bp)
    app.register_blueprint(programari_bp)
    app.register_blueprint(analiza_bp)

    @app.route('/')
    def index():
        return redirect(url_for('programari.lista'))

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=False)