import re
import os
from datetime import datetime
from flask import Flask, render_template, abort, request, redirect, make_response, url_for, Blueprint, current_app as app, session, flash
import mysql.connector
from mysql.connector import Error
from babel import dates ,numbers
import bd
bp_services = Blueprint('services', __name__)

balises_html = re.compile(r'<(.*)>.*?|<(.*) />')
langues_disponibles = ["en_CA", "fr_CA"]
BABEL_DEFAULT_LOCALE = "fr_CA"
devise ={
    'fr_CA':'CAD',
    'en_CA':'CAD'
}
@bp_services.route("/changer_locale")
def changer_locale():
    """Permet de changer la langue de la page"""
    locale = request.args.get("locale", BABEL_DEFAULT_LOCALE)
    if locale not in langues_disponibles:
        return redirect(url_for('services.accueil'))
    reponse = make_response(redirect(request.referrer or '/'))
    reponse.set_cookie("langue", locale)
    return reponse

def get_local():
    """Retourne la locale du cookie (par défaut fr_CA)"""
    return request.cookies.get('langue',BABEL_DEFAULT_LOCALE)

@bp_services.route("/")
def accueil():
    """Affiche les  cinq derniers services de particuliers ajoutés selon la date d’ajout, du plus récent au plus ancien"""

    with bd.creer_connexion() as conn:
        services = bd.get_services(conn)

    return render_template("services/accueil.jinja", services = services)

@bp_services.route("/liste_services")
def listes_services():
    """Affiche les  cinq derniers services de particuliers ajoutés selon la date d’ajout, du plus récent au plus ancien"""
    with bd.creer_connexion() as conn:
        services = bd.get_services(conn, tous=True)
    return render_template("services/listes_services.jinja", services = services)

@bp_services.route("details_services/<int:id_service>")
def details_service(id_service):
    """Affiche les détails d'un service"""
    locale = get_local()
    try :
        with bd.creer_connexion() as conn:
            service = bd.get_service(conn, id_service)
        if service is None:
            abort(404, "Jeu non trouvé")
        if service.get('date_creation'):
            service['date_creation']=dates.format_datetime(service['date_creation'],locale=locale)
        if service.get('cout') is not None:
            service['cout']=numbers.format_currency(service['cout'],devise[locale],locale=locale)

        return render_template("services/service.jinja", service = service)

    except Error:
        abort(500, "Erreur en lien avec la base de données")
    
@bp_services.route("/ajouter_service", methods=['GET', 'POST'])
def ajouter_service():
    """Permet d'ajouter un service"""

    class_titre = ''
    class_localisation = ''
    class_description = ''
    class_categorie =''
    class_cout = ''
    class_nom_photo = ''

    titre = ""
    localisation = ""
    description = ""
    cout = "0"
    actif = 1
    id_categorie = ""
    photo = ""

    with bd.creer_connexion() as conn:
        categorie  = bd.get_categories(conn)

        if request.method == 'POST':
                titre = request.form.get("titre", "").strip()
                localisation = request.form.get("localisation", "").strip()
                description = request.form.get("description", "").strip()
                cout = request.form.get("cout", "0").strip()
                actif = int(request.form.get("actif", 1))
                id_categorie = request.form.get("id_categorie", default="")
                photo = request.form.get("photo", "").strip()
                service={
                    'titre': titre,
                    'localisation': localisation,
                    'description': description,
                    'cout': cout,
                    'actif': actif,
                    'id_categorie': id_categorie,
                    'photo': photo,
                    'id_utilisateur': 1,
                    'date_creation': datetime.now()
                }
                if id_categorie:
                    try:
                        id_categorie=int(id_categorie)
                    except ValueError:
                        class_categorie ='is-invalid'

                if 'actif' in request.form:
                    try:
                        actif = int(request.form.getlist('actif')[-1])
                    except ValueError:
                        actif = 1

                if not titre or balises_html.search(titre) or len(titre)< 1 or len(titre) > 50:
                    class_titre = 'is-invalid'

                if not localisation or balises_html.search(localisation) or len(localisation) < 1 or len(localisation) > 50:
                    class_localisation = 'is-invalid'


                if not description or balises_html.search(description) or len(description) < 5 or len(description) > 2000:
                    class_description = 'is-invalid'

                if not photo or balises_html.search(photo) or len(photo) < 6 or len(photo) > 50:
                    class_nom_photo = 'is-invalid'

                try:
                    cout = float(cout)
                    if cout < 0:
                        class_cout = 'is-invalid'
                except ValueError:
                    class_cout = 'is-invalid'


                if not class_titre and not class_localisation and not class_description and not class_categorie and not class_cout and not class_nom_photo:
                    bd.add_service(conn, service)
                    flash("Le service a été ajouté avec succès.", "success")
                    return redirect(url_for('services.acceuil'), code= 303)

    return render_template('ajouter_service.jinja', class_titre = class_titre, class_localisation = class_localisation,class_description= class_description,
                           class_cout= class_cout, class_nom_photo= class_nom_photo,categories= categorie, titre = titre, localisation=localisation,
                           description=description, cout = cout, actif = actif, id_categorie= id_categorie)


@bp_services.route("/modifier_service", methods= ['GET', 'POST'])
def modifier_service():
    """Permet de modifier un service existant"""
    locale = get_local()
    id_service = request.args.get("id_service", type=int)

    if not id_service:
        abort(400, "id_service du service manque dans l'URL")
    try :
        with bd.creer_connexion() as conn:
            service = bd.get_service(conn, id_service)

            if not service :
                abort(404, "Service non trouvé")
        if service.get('date_creation'):
            service['date_creation'] = dates.format_datetime(service['date_creation'], locale=locale)

        class_titre = ''
        class_localisation = ''
        class_description = ''
        class_cout = ''

        if request.method == 'POST':
            titre = request.form.get("titre", "").strip()
            localisation = request.form.get("localisation", "").strip()
            description = request.form.get("description", "").strip()
            cout = request.form.get("cout", "").strip()
            try:
                actif = int(request.form.getlist('actif')[-1])
            except (ValueError, IndexError):
                actif = service['actif']

            if not titre or balises_html.search(titre) or len(titre)< 1 or len(titre) > 50:
                class_titre = 'is-invalid'

            if not localisation or balises_html.search(localisation) or len(localisation) < 1 or len(localisation) > 50:
                class_localisation = 'is-invalid'


            if not description or balises_html.search(description) or len(description) < 5 or len(description) > 2000:
                class_description = 'is-invalid'

            try:
                cout = float(cout)
                if cout < 0:
                    class_cout = 'is-invalid'
            except ValueError:
                class_cout = 'is-invalid'

            if not class_titre and not class_localisation and not class_description and not class_cout:
                with bd.creer_connexion() as conn:
                    with conn.get_curseur() as curseur:
                        bd.update_service(conn, id_service, titre, localisation, description, cout, actif)
                        flash("Le service a été modifié avec succès.", "success")
                        return redirect(url_for('services.acceuil'), 303)

        return render_template('services/modifier_service.jinja', service = service, class_titre = class_titre, class_localisation = class_localisation,
                           class_description = class_description, class_cout = class_cout)
    except Error :
        abort(500, "Erreur en lien avec la base de données")



