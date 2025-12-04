"""
Une application Flask d'échange de service
"""
import os
import dotenv

from dotenv import load_dotenv
from mysql.connector import Error
from flask import Flask, render_template, session
from flask.logging import create_logger

from compte import bp_compte
from services import bp_services
from api import bp_api
import bd

if not os.getenv('BD_UTILISATEUR'):
    dotenv.load_dotenv('.env')

project_home = '/home/Valdess/420-05C-FX-TP3'
load_dotenv(os.path.join(project_home, '.env'))

def create_app():
    app = Flask(__name__)
    app.secret_key = "e468d2eb51a1fcea5386f35e887413d4fd3e091fdacb2ba3df28798e6fff98fa"
    # Liste des sous-répertoires vers "ajouts"
    app.config['MORCEAUX_VERS_AJOUTS'] = ["static", "images", "ajouts"]

# Pour donner static/images/ajouts". Assurez-vous que ce dossier existe !
    app.config['ROUTE_VERS_AJOUTS'] = "/".join(app.config['MORCEAUX_VERS_AJOUTS'])


    app.config['CHEMIN_VERS_AJOUTS'] = os.path.join(
        app.root_path,
        *app.config['MORCEAUX_VERS_AJOUTS']
    )
    logger = create_logger(app)
    app.register_blueprint(bp_compte, url_prefix = '/compte')
    app.register_blueprint(bp_services, url_prefix = '/services')
    app.register_blueprint(bp_api, url_prefix='/api')
    
    @app.route("/")
    def accueil():
        """Page d'accueil"""
        with bd.creer_connexion() as conn:
            services = bd.get_services(conn)
            if 'identifiant' in session:
                for service in services:
                    if bd.verifier_proprietaire_service(conn, service['id_service'], session.get('identifiant')):
                        service['est_proprietaire'] = True
                    else:
                        service['est_proprietaire'] = False
        return render_template("accueil.jinja", services = services)

    @app.errorhandler(400)
    def bad_request(e):
        """Gère les erreurs 400"""
        logger.exception(e)
        return render_template('page_erreur.jinja', message="Paramètre(s) manquant(s) " + str(e.description), code = 400), 400


    @app.errorhandler(404)
    def not_found(e):
        """Gère les erreurs 404"""
        logger.exception(e)
        msg = getattr(e, 'description', "Page inexistante")

        return render_template("page_erreur.jinja", message = msg, code = 404), 404
    @app.errorhandler(403)
    def forbidden(e):
        """Gère les erreurs 403"""
        logger.exception(e)
        return render_template('page_erreur.jinja', message="Vous n'avez pas la permission de faire cette action.", code = 403), 403

    @app.errorhandler(401)
    def unauthorized(e):
        """Gère les erreurs 401"""
        logger.exception(e)
        return render_template('page_erreur.jinja', message="Vous devez être connecté pour faire cette action.", code = 401), 401

    @app.errorhandler(500)
    def internal_server_error(e):
        """Gère les erreurs 500"""
        logger.exception(e)

        message = "Le serveur a rencontré un problème, veuillez retourner à l'accueil."

        if e.original_exception and isinstance(e.original_exception, Error):
            message = "erreur en lien avec la base de donnée"

        return render_template('page_erreur.jinja', message= message, code = 500 ), 500
    return app

app = create_app()
app.run(debug=True)
