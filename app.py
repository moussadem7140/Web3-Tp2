"""
Une application Flask d'échange de service
"""
import re
from datetime import datetime
from flask import Flask, render_template, abort, request, redirect, make_response
from babel import dates ,numbers
from flask.logging import create_logger
from mysql.connector import Error

import bd

app = Flask(__name__)
logger = create_logger(app)

balises_html = re.compile(r'<(.*)>.*?|<(.*) />')
langues_disponibles = ["en_CA", "fr_CA"]
BABEL_DEFAULT_LOCALE = "fr_CA"
devise ={
    'fr_CA':'CAD',
    'en_CA':'CAD'
}
@app.route("/")
def services_particulier():
    """Affiche les  cinq derniers services de particuliers ajoutés selon la date d’ajout, du plus récent au plus ancien"""

    with bd.creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute('''SELECT s.id_service, s.titre, s.localisation, s.date_creation,s.photo, c.nom_categorie
                            FROM services s JOIN categories c ON s.id_categorie = c.id_categorie
                            WHERE s.actif = 1 ORDER By s.date_creation DESC LIMIT 5''')
            services = curseur.fetchall()

    return render_template("accueil.jinja", services = services)


@app.route("/changer_locale")
def changer_locale():
    """Permet de changer la langue de la page"""
    locale = request.args.get("locale", BABEL_DEFAULT_LOCALE)
    if locale not in langues_disponibles:
        return redirect('/')
    reponse = make_response(redirect(request.referrer or '/'))
    reponse.set_cookie("langue", locale)
    return reponse

def get_local():
    """Retourne la locale du cookie (par défaut fr_CA)"""
    return request.cookies.get('langue',BABEL_DEFAULT_LOCALE)

@app.route("/liste_services")
def listes_services():
    """Affiche les  cinq derniers services de particuliers ajoutés selon la date d’ajout, du plus récent au plus ancien"""
    with bd.creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute('''SELECT s.id_service, s.titre, s.localisation, s.date_creation,s.photo, c.nom_categorie
                            FROM services s JOIN categories c ON s.id_categorie = c.id_categorie ORDER By s.date_creation''')
            services = curseur.fetchall()

    return render_template("listes_services.jinja", services = services)

@app.route("/service/<int:id_service>")
def details_service(id_service):
    """Affiche les détails d'un service"""
    locale = get_local()
    try :
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute('''SELECT s.id_service, s.titre, s.localisation, s.description, s.cout, s.date_creation, s.actif, c.nom_categorie
                            FROM services s JOIN categories c ON s.id_categorie = c.id_categorie
                            WHERE s.id_service = %(id)s''',
                {
                    "id": id_service
                })
                service = curseur.fetchone()

        if service is None:
            abort(404, "Jeu non trouvé")
        if service.get('date_creation'):
            service['date_creation']=dates.format_datetime(service['date_creation'],locale=locale)
        if service.get('cout') is not None:
            service['cout']=numbers.format_currency(service['cout'],devise[locale],locale=locale)

        return render_template("service.jinja", service = service)

    except Error:
        abort(500, "Erreur en lien avec la base de données")


@app.route("/ajouter_service", methods=['GET', 'POST'])
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
        with conn.get_curseur() as curseur:
            curseur.execute("""
            SELECT id_categorie, nom_categorie FROM categories """)
            categorie = curseur.fetchall()

            if request.method == 'POST':
                titre = request.form.get("titre", "").strip()
                localisation = request.form.get("localisation", "").strip()
                description = request.form.get("description", "").strip()
                cout = request.form.get("cout", "0").strip()
                actif = int(request.form.get("actif", 1))
                id_categorie = request.form.get("id_categorie", default="")
                photo = request.form.get("photo", "").strip()

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
                    date_creation = datetime.now()
                    curseur.execute('''INSERT INTO services(titre, description,localisation, actif, cout, id_categorie, date_creation, photo)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''', (titre,description, localisation, actif, cout, id_categorie, date_creation, photo))
                    conn.commit()
                    return redirect('/confirmation_service', code= 303)

    return render_template('ajouter_service.jinja', class_titre = class_titre, class_localisation = class_localisation,class_description= class_description,
                           class_cout= class_cout, class_nom_photo= class_nom_photo,categories= categorie, titre = titre, localisation=localisation,
                           description=description, cout = cout, actif = actif, id_categorie= id_categorie)


@app.route("/modifier_service", methods= ['GET', 'POST'])
def modifier_service():
    """Permet de modifier un service existant"""
    locale = get_local()
    id_service = request.args.get("id_service", type=int)

    if not id_service:
        abort(400, "id_service du service manque dans l'URL")
    try :
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute('SELECT s.*, c.nom_categorie FROM services s ' \
                'JOIN categories c ON s.id_categorie = c.id_categorie WHERE id_service = %(id)s',
                {"id": id_service})
                service = curseur.fetchone()

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
                        curseur.execute('''UPDATE services
                                    SET titre = %s, localisation = %s, description = %s, cout =%s, actif = %s
                                    WHERE id_service = %s''', (titre, localisation, description, cout, actif, id_service))
                        conn.commit()
                        return redirect('/confirmation_service', 303)

        return render_template('modifier_service.jinja', service = service, class_titre = class_titre, class_localisation = class_localisation,
                           class_description = class_description, class_cout = class_cout)
    except Error :
        abort(500, "Erreur en lien avec la base de données")

@app.route("/confirmation_service")
def confirmation_service():
    """Message de confirmation"""
    return render_template("confirmation_service.jinja")


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
