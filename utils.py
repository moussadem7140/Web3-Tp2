"""
Fichier contient les fonctions utiles et qui sont repeter dans plusieurs endroit
"""
import os
import hashlib
from flask import render_template, current_app

def hacher_mdp(mdp_en_clair):
    """Prend un mot de passe en clair et lui applique une fonction de hachage"""
    return hashlib.sha512(mdp_en_clair.encode()).hexdigest()

def valider_formulaire(courriel, mdp, mdp_repeat, regex_email, regex_mdp, regex_html):
    """permet de valider le formulaire d'inscription"""
    erreurs = {}

    if not regex_html.match(courriel) or not regex_email.match(courriel) or not courriel:
        erreurs["class_courriel"] = "is-invalid"
    else:
        erreurs["class_courriel"] = "is-valid"

    if not regex_mdp.match(mdp) or not mdp or not mdp_repeat or mdp != mdp_repeat:
        erreurs["class_mdp"] = "is-invalid"
        erreurs["class_mdp_repeat"] = "is-invalid"
    else:
        erreurs["class_mdp"] = "is-valid"
        erreurs["class_mdp_repeat"] = "is-valid"

    return erreurs

def get_image_path(id_service):
    """Retourne le chemin web de l'image si elle existe, sinon celui d'une image par défaut"""
    nom_image  = f"service_{id_service}"
    chemin_fichier = os.path.join(current_app.root_path, "static", "images", nom_image)

    if os.path.exists(chemin_fichier):
        return f"/static/images/{nom_image}"

    return "/static/images/defaut.png"


def get_page_erreur(code, message):
    """ Permet de gérer les pages d'erreurs """
    return render_template('erreur.jinja', code=code, message=message)
