""" Api"""
from flask import Blueprint, jsonify, request,session,abort, flash, redirect, url_for, current_app as app
import utils
import bd

bp_api = Blueprint('api', __name__)

@bp_api.route('/services')
def api_services():
    """Retourne les services pour le défilement infini"""
    offset = int(request.args.get("offset", 0))
    limite = int(request.args.get("limit", 6))

    with bd.creer_connexion() as conn:
        services = bd.get_services_api(conn, offset, limite)
        for s in services:
            s["est_proprietaire"] = bd.verifier_proprietaire_service(
                conn, s["id_service"], session.get("identifiant")
            )
    return jsonify(services)

@bp_api.route('/suggestion-recherche')
def suggestion_rechercher():
    """Sugestion de recherche"""
    query = request.args.get('query', '').strip().lower()

    if not query or len(query) < 2:
        return jsonify([])

    with bd.creer_connexion() as conn:
        resultat = bd.get_api_recherche(conn, query)

    return jsonify(resultat)

@bp_api.route('/verifier-courriel')
def verifier_courriel():
    """ Vérification du courriel """
    courriel = request.args.get('courriel')

    with bd.creer_connexion() as conn:
        user_doublon = bd.verifie_doublon_courriel(conn, courriel)

    return jsonify({"existe": user_doublon})

@bp_api.route('/utilisateurs-recherche')
def utilisateurs_recherche():
    """ recherche"""
    user = request.args.get('user', '').strip().lower()

    if not user or len(user) < 2:
        return jsonify([])

    with bd.creer_connexion() as conn:
        resultat = bd.get_api_recherche2(conn, user)

    return jsonify(resultat)

@bp_api.route('/verifier-disponibilite')
def verifier_disponibilite():
    flash( "dans api" )
    """Vérifie la disponibilité d'un service via l'API"""
    id_service = request.args.get('id_service', type=int)
    heure = request.args.get('heure', type=str)
    date = request.args.get('date', type=str)
    with bd.creer_connexion() as conn:
        est_disponible = bd.est_Disponible(conn, id_service, date, heure)

    # Retourner la clé 'disponible' pour correspondre au code JS
    return jsonify({"disponible": est_disponible, "message": "ok"})
@bp_api.route('/supprimer_utilisateur', methods=['GET'])
def supprimer_utilisateur():
    """Permet de supprimer un utilisateur"""
    id_utilisateur = request.args.get('id_utilisateur', type=int)
    if 'identifiant' not in session:
        abort(401)
    if session.get('role') != 'admin':
        flash("Vous n'avez pas la permission de faire cette action.", "error")
        abort(403)
    with bd.creer_connexion() as conn:
        bd.get_supprimer_utilisateur(conn, id_utilisateur)
        flash("Utilisateur supprimé avec succès.", "success")
        return jsonify({"success": True})
    return jsonify({"success": False})
@bp_api.route("/accueil")
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
        return jsonify(services)

@bp_api.route('/supprimer_service', methods=['POST', 'GET'])
def supprimer_service():
    """Permet de supprimer un service via AJAX"""
    id_service = request.args.get('id_service', type=int)
    if 'identifiant' not in session:
        return jsonify({"success": False, "message": "Non connecté"}), 401

    with bd.creer_connexion() as conn:
        if not bd.verifier_proprietaire_service(conn, id_service, session.get('identifiant')) \
           and session.get('role') != "admin":
            return jsonify({"success": False, "message": "Pas la permission"}), 403

        if bd.verifier_service_reserve(conn, id_service):
            return jsonify({"success": False, "message": "Service réservé"}), 409

        bd.supprimer_service(conn, id_service)

    return jsonify({"success": True})