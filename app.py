"""
Une application Flask d'échange de service
"""
import re
import os
import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template
from flask.logging import create_logger
from compte import bp_compte
from services import bp_services
from reservation import bp_reservation

def create_app():
    app = Flask(__name__)
    logger = create_logger(app)
    app.register_blueprint(bp_compte, url_prefix = '/compte')
    app.register_blueprint(bp_services, url_prefix = '/services')
    app.register_blueprint(bp_reservation, url_prefix = '/reservation')
    app.secret_key = "e468d2eb51a1fcea5386f35e887413d4fd3e091fdacb2ba3df28798e6fff98fa"

    @app.route("/")
    def connexion():
        return render_template("se_connecter.jinja")

    def televersement_image(fichier, nom_image):
        """Modification de l'image d'une annonce"""
        app.config['MORCEAUX_VERS_AJOUTS'] = ["static", "images"]

        app.config['ROUTE_VERS_AJOUTS'] = "/".join(app.config['MORCEAUX_VERS_AJOUTS'])

        app.config['CHEMIN_VERS_AJOUTS'] = os.path.join(
        app.instance_path.replace("instance", ""),
        *app.config['MORCEAUX_VERS_AJOUTS']
        )

        chemin_complet = os.path.join(
            app.config['CHEMIN_VERS_AJOUTS'], nom_image
        )
        fichier.save(chemin_complet)

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
app.run()
