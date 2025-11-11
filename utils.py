"""
Fichier contient les fonctions utiles et qui sont repeter dans plusieurs endroit
"""
import os
import hashlib
from flask import render_template

def hacher_mdp(mdp_en_clair):
    """Prend un mot de passe en clair et lui applique une fonction de hachage"""
    return hashlib.sha512(mdp_en_clair.encode()).hexdigest()

def valider_formulaire(nom, courriel, credit, mdp, mdp_repeat, regex_email, regex_mdp, regex_html):
    """permet de valider le formulaire d'inscription"""
    erreurs = {}

    if not nom :
        erreurs["class_nom"] = "is-invalid"
    else:
        erreurs["class_nom"] = "is-valid"


    if not regex_html.match(courriel) or not regex_email.match(courriel) or not courriel:
        erreurs["class_courriel"] = "is-invalid"
    else:
        erreurs["class_courriel"] = "is-valid"

    try:
        credit_val = float(credit)
        if credit_val != 0:
            erreurs["class_credit"] = "is-invalid"
        else:
            erreurs["class_credit"] = "is-valid"
    except ValueError:
        erreurs["class_credit"] = "is-invalid"

    if not mdp or not mdp_repeat or mdp != mdp_repeat:
        erreurs["class_mdp"] = "is-invalid"
        erreurs["class_mdp_repeat"] = "is-invalid"
    else:
        erreurs["class_mdp"] = "is-valid"
        erreurs["class_mdp_repeat"] = "is-valid"

    return erreurs

def get_page_erreur(code, message):
    """ Permet de gérer les pages d'erreurs """
    return render_template('erreur.jinja', code=code, message=message)
