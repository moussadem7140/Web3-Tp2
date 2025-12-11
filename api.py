""" Api"""
from flask import Blueprint, jsonify, request,session,abort
import utils
import bd

bp_api = Blueprint('api', __name__)

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

