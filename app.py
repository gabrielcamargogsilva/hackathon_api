import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
import db

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")
    app.teardown_appcontext(db.close_db)

    from api.quiz import quiz_bp
    from api.flashcards import flashcards_bp
    from api.lacunas import lacunas_bp
    from api.jogadores import jogadores_bp

    app.register_blueprint(quiz_bp, url_prefix="/quiz")
    app.register_blueprint(flashcards_bp, url_prefix="/flashcards")
    app.register_blueprint(lacunas_bp, url_prefix="/lacunas")
    app.register_blueprint(jogadores_bp)

    @app.cli.command("init-db")
    def init_db_cmd():
        db.init_db()
        print("Tabelas criadas.")

    @app.get("/")
    def home():
        return {"status": "API on"}

    @app.errorhandler(500)
    def erro_interno(_e):
        _ = _e
        return {"erro": "Erro interno do servidor."}, 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
