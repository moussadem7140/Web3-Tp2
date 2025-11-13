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
import bd
def create_app():
    app = Flask(__name__)
    logger = create_logger(app)
    app.register_blueprint(bp_compte, url_prefix = '/compte')
    app.register_blueprint(bp_services, url_prefix = '/services')
    app.register_blueprint(bp_reservation, url_prefix = '/reservation')
    app.secret_key = "e468d2eb51a1fcea5386f35e887413d4fd3e091fdacb2ba3df28798e6fff98fa"

    @app.route("/")
    def accueil():
        """Page d'accueil"""
        with bd.creer_connexion() as conn:
            services = bd.get_services(conn)
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
