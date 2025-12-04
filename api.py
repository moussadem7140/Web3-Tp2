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