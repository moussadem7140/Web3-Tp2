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
    'en_CA':'$'
}
@bp_services.route("/changer_locale/<locale>")
def changer_locale(locale):
    """Permet de changer la langue de la page"""
    session['langue'] = locale
    return redirect(url_for('accueil'))
def get_local():
    """Retourne la locale du cookie (par défaut fr_CA)"""
    return session.get('langue',BABEL_DEFAULT_LOCALE)

@bp_services.route("/liste_services")
def listes_services():
    with bd.creer_connexion() as conn:
        services = bd.get_services(conn, tous=True)
        if 'identifiant' in session:
            for service in services:
                if bd.verifier_proprietaire_service(conn, service['id_service'], session.get('identifiant')):
                    service['est_proprietaire'] = True
                else:
                    service['est_proprietaire'] = False
    return render_template("services/listes_services.jinja", services = services)

@bp_services.route("details_service/<int:id_service>")
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
            if 'identifiant' in session:
                service["est_proprietaire"]= bd.verifier_proprietaire_service(conn, id_service, session.get('identifiant'))
                       
        return render_template("services/service.jinja", service = service)

    except Error:
        abort(500, "Erreur en lien avec la base de données")
    
@bp_services.route("/ajouter_service", methods=['GET', 'POST'])
def ajouter_service():
    if not session.get('identifiant'):
        flash("Vous devez être connecté pour ajouter un service.", "error")
        abort(401)
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
                photo = request.files['image']
                nom_image = "image_" +titre+ ".png"
                chemin_complet = os.path.join(
                    app.config['CHEMIN_VERS_AJOUTS'], nom_image
                )
                photo.save(chemin_complet)
                photo = "/" + app.config['ROUTE_VERS_AJOUTS'] + "/" + nom_image
                service={
                    'titre': titre,
                    'localisation': localisation,
                    'description': description,
                    'cout': cout,
                    'actif': actif,
                    'id_categorie': id_categorie,
                    'photo': photo,
                    'id_utilisateur': session.get('identifiant'),
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
                    return redirect(url_for('accueil'), code= 303)

    return render_template('services/ajouter_service.jinja', class_titre = class_titre, class_localisation = class_localisation,class_description= class_description,
                           class_cout= class_cout, class_nom_photo= class_nom_photo,categories= categorie, titre = titre, localisation=localisation,
                           description=description, cout = cout, actif = actif, id_categorie= id_categorie)


@bp_services.route("/modifier_service/<int:id_service>", methods= ['GET', 'POST'])
def modifier_service(id_service):
    if not session.get('identifiant'):
        flash("Vous devez être connecté pour modifier un service.", "error")
        abort(401)
    with bd.creer_connexion() as conn:
        if not bd.verifier_proprietaire_service(conn, id_service, session.get('identifiant')) and session.get('role')!="admin":
            flash("Vous n'avez pas la permission de modifier ce service.", "error")
            abort(403)
    """Permet de modifier un service existant"""
    locale = get_local()

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
        class_photo = ''
        class_categorie =''

        if request.method == 'POST':
            titre = request.form.get("titre", "").strip()
            localisation = request.form.get("localisation", "").strip()
            description = request.form.get("description", "").strip()
            cout = request.form.get("cout", "").strip()
            photo = request.files['image']
            if not photo :
                class_photo = 'is-invalid'  
            nom_image = "image_" +titre+ ".png"
            chemin_complet = os.path.join(
                app.config['CHEMIN_VERS_AJOUTS'], nom_image
            )
            photo.save(chemin_complet)
            photo = "/" + app.config['ROUTE_VERS_AJOUTS'] + "/" + nom_image
    
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
            
            if not class_titre and not class_localisation and not class_description and not class_cout and not class_photo:
                with bd.creer_connexion() as conn:
                    bd.update_service(conn, id_service, titre, localisation, description, cout, actif, photo)
                    flash("Le service a été modifié avec succès.", "success")
                    return redirect(url_for('accueil'), 303)

        return render_template('services/modifier_service.jinja', service = service, class_titre = class_titre, class_localisation = class_localisation,
                           class_description = class_description, class_cout = class_cout, class_photo= class_photo, class_categorie= class_categorie)
    except Error :
        abort(500, "Erreur en lien avec la base de données")


@bp_services.route('/reserver/<int:id_service>', methods = ["GET","POST"])
def reserver(id_service):
    """Permet a un utilisateur de reserver un service"""
    class_date = ""
    class_heure = ""
    if request.method == "POST":
        if not session.get('identifiant'):
            flash("Vous devez être connecté pour réserver un service.", "error")
            abort(401)
        date = request.form.get('date', "").strip()
        heure = request.form.get('heure', "").strip()
        with bd.creer_connexion() as conn:
            service = bd.get_service(conn, id_service)
            if  float(service['cout']) > float(session.get('credit', 0)):
                    flash("Vous n'avez pas assez de crédit pour réserver ce service.", "error")
                    redirect(url_for('accueil'), code=303)
            elif bd.verifier_proprietaire_service(conn, id_service, session.get('identifiant')):
                    flash("Vous ne pouvez pas réserver votre propre service.", "error")
                    redirect(url_for('accueil'), code=303)
            elif not date or not heure or not bd.est_Disponible(conn, id_service, date, heure):
                    class_date = "is-invalid"
                    class_heure = "is-invalid"
            else:
                bd.ajouter_reservation(conn, id_service, session.get('identifiant'), date, heure)
                bd.update_credit_utilisateur(conn, service['id_utilisateur'] , session.get('identifiant'), service['cout'])
                flash("Réservation effectuée avec succès.", "success")
                return redirect(url_for('accueil'), code=303)
    
    return render_template("services/reservation.jinja" , class_date= class_date, class_heure= class_heure, id_service= id_service)

@bp_services.route('/supprimer/<int:id_service>', methods=['POST', 'GET'])
def supprimer(id_service):
    """Permet a un utilisateur de supprimer un service"""
    if not session.get('identifiant'):
        flash("Vous devez être connecté pour supprimer un service.", "error")
        abort(401)
    with bd.creer_connexion() as conn:
        if not bd.verifier_proprietaire_service(conn, id_service, session.get('identifiant')) or session.get('role')!="admin":
            flash("Vous n'avez pas la permission de supprimer ce service.", "error")
            abort(403)
        elif bd.verifier_service_reserve(conn, id_service):
            flash("Vous ne pouvez pas supprimer un service qui est réservé.", "error")
            return redirect(url_for('accueil'), code=303)
        else:
            try:
                bd.supprimer_service(conn, id_service)
                flash("Service supprimé avec succès.", "success")
            except Error:
                abort(500, "Erreur en lien avec la base de données")
            return redirect(url_for('accueil'), code=303)