""" Api"""
from flask import Blueprint, jsonify, request,session,abort
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

