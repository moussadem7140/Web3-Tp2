"""Gestion du bluprint de compte utilisateur"""
import re
from flask import Blueprint, request, render_template, redirect, flash, session, url_for, abort, current_app as app
import utils
import bd

bp_compte = Blueprint('compte', __name__)

#regex pour verifier s'il y a une balise html dans les champs
REGEXE_EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
REGEX_MDP = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
REGEX_HTML = re.compile( r'^[^<>]*$')

@bp_compte.route('/ajouter_utilisateur', methods = ["GET","POST"])
def ajouter_utilisateur():
    """Route vers la page de création du compte si GET si non Creation du compte si POST"""

    if request.method == "POST":
        if 'identifiant' not in session:
            abort(401)
        elif session.get('role') != 'admin':
            flash("Vous n'avez pas la permission de faire cette action.", "error")
            abort(403)
        else:
            courriel = request.form.get('courriel', '').strip()
            mdp = request.form.get('mdp', '').strip()
            mdp_repeat = request.form.get('mdp_repeat', '').strip()

            erreurs = utils.valider_formulaire(courriel, mdp, mdp_repeat, REGEXE_EMAIL, REGEX_MDP, REGEX_HTML)
            if "is-invalid" in erreurs.values():
                return render_template(
                    'compte/ajouter_utilisateur.jinja',
                    courriel=courriel,
                    mdp = mdp,
                    mdp_repeat = mdp_repeat,
                    titre="Création de compte",
                    class_nom=erreurs.get("class_nom", ""),
                    class_courriel=erreurs.get("class_courriel", ""),
                    class_mdp=erreurs.get("class_mdp", ""),
                    class_mdp_repeat=erreurs.get("class_mdp_repeat", "")
                )

            with bd.creer_connexion() as conn:
                user_doublon = bd.verifie_doublon_courriel(conn,courriel)
                if user_doublon is None:
                    user = {
                        "courriel": courriel,
                        "mdp": utils.hacher_mdp(mdp)
                    }
                    bd.creer_user(conn, user)
                    flash("Utilisateur créé avec succès.", "success")
                else:
                    flash(
                        "Cet utilisateur est déjà enregistré. "
                        "Essayez de vous connecter ou utilisez un autre courriel.", "error"
                    )
                    return redirect(url_for("compte.ajouter_utilisateur"), code=303)

            return redirect(url_for('accueil'), code=303)

    return render_template("compte/ajouter_utilisateur.jinja")

@bp_compte.route('/se_connecter', methods = ["GET","POST"])
def se_connecter():
    """Permet a l'utilisateur de se connecter et le rediriger vers la page d'accueil"""
    if request.method == "POST":

        courriel = request.form.get('courriel', "").strip()
        mdp = request.form.get('mdp', "").strip()
        with bd.creer_connexion() as conn:
            user = bd.authentification(conn,courriel,utils.hacher_mdp(mdp))
            if user is not None:
                session.clear()
                session.permanent = True
                session['identifiant'] = user["id_utilisateur"]
                session['courriel'] = user["courriel"]
                session['role'] = user["role"]
                session['credit'] = user["credit"]
                session['langue'] =  "fr_CA"
                flash("Connexion réussie.", "success")
                return redirect(url_for('accueil'), code=303)
            else:
                flash("Les identifiants saisis sont incorrects.", "error")
                return render_template('compte/se_connecter.jinja',
                                    class_mdp="is-invalid",
                                    class_courriel="is-invalid",
                                    courriel = courriel,
                                    titre="Connexion")
    return render_template('compte/se_connecter.jinja')

@bp_compte.route('/se_deconnecter')
def se_deconnecter():
    """Permet a l'utilisateur de se deconnecter et le rediriger vers la page d'accueil"""
    if 'identifiant' not in session:
        abort(401)
    else:
        session.clear()
        flash("Déconnexion réussie.", "success")
        return redirect(url_for('accueil'), code=303)

@bp_compte.route('/liste_utilisateurs')
def liste_utilisateurs():
    """Permet d'afficher la liste des utilisateurs"""
    if 'identifiant' not in session:
        abort(401)
    elif session.get('role') != 'admin':
        flash("Vous n'avez pas la permission de faire cette action.", "error")
        abort(403)
    else:
        with bd.creer_connexion() as conn:
            if(request.args.get('id_unique')):
                id_utilisateur=request.args.get('id_unique')
                utilisateurs = bd.get_liste_compte(conn,id_utilisateur)
                flash("Utilisateur trouvé avec succès.", "success")
            else:
                utilisateurs = bd.get_liste_compte(conn)
                flash("Liste des utilisateurs chargée avec succès.", "success")
        return render_template('compte/liste_utilisateurs.jinja', utilisateurs=utilisateurs)

@bp_compte.route('/supprimer_utilisateur/<int:id_utilisateur>', methods=['POST'])
def supprimer_utilisateur(id_utilisateur):
    """Permet de supprimer un utilisateur"""
    if 'identifiant' not in session:
        abort(401)
    if session.get('role') != 'admin':
        flash("Vous n'avez pas la permission de faire cette action.", "error")
        abort(403)
    with bd.creer_connexion() as conn:
        bd.get_supprimer_utilisateur(conn, id_utilisateur)
        flash("Utilisateur supprimé avec succès.", "success")

    return redirect(url_for('compte.liste_utilisateurs'), code=303)
