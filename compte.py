"""Gestion du bluprint de compte utilisateur"""
import re
from flask import Blueprint, request, render_template, redirect, flash, session, url_for
import utils
import bd

bp_compte = Blueprint('compte', __name__)

#regex pour verifier s'il y a une balise html dans les champs
REGEXE_EMAIL = re.compile(r"^(?!.*\.\.)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$")
REGEX_MDP = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$")
REGEX_HTML = re.compile(r"<[^>]+>")

@bp_compte.route('/ajouter_utilisateur', methods = ["GET","POST"])
def creer_compte():
    """Route vers la page de création du compte si GET si non Creation du compte si POST"""

    if request.method == "POST":
        courriel = request.form.get('courriel', '').strip()
        credit = request.form.get('credit', '').strip()
        mdp = request.form.get('mdp')
        mdp_repeat = request.form.get('mdp_repeat')

        erreurs = utils.valider_formulaire(courriel, credit, mdp, mdp_repeat, REGEXE_EMAIL, REGEX_MDP, REGEX_HTML)
        if "is-invalid" in erreurs.values():
            return render_template(
                'compte/creer_compte.jinja',
                courriel=courriel,
                credit=credit,
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
                    "mdp": utils.hacher_mdp(mdp),
                    "credit": credit,
                }
                bd.creer_user(conn, user)
            else:
                flash(
                    "Cet utilisateur est déjà enregistré. "
                    "Essayez de vous connecter ou utilisez un autre courriel.", "error"
                )
                return redirect(url_for("gestion_compte.ajouter_utilisateur"), code=303)
        return redirect("/", code=303)
    return redirect("gestion_compte/liste_utilisateurs.jinja")


@bp_compte.route('/se_connecter', methods = ["GET","POST"])
def se_connecter():
    """Permet a l'utilisateur de se connecter et le rediriger vers la page d'accueil"""
    if request.method == "POST":

        courriel = request.form.get('courriel')
        mdp = request.form.get('mdp')

        if not REGEXE_EMAIL.match(courriel) or courriel == "" and mdp == "":
            return render_template('se_connecter.jinja',class_mdp="is-invalid",
                                   class_courriel="is-invalid",
                                   courriel = courriel,titre="Connexion")

        if mdp == "":
            return render_template('se_connecter.jinja',class_mdp="is-invalid",
                                   class_courriel="is-valid",courriel = courriel,
                                     titre="Connexion")

        with bd.creer_connexion() as conn:
            user = bd.authentification(conn,courriel,utils.hacher_mdp(mdp))

        if user is not None:
            session.clear()
            session.permanent = True
            session['identifiant'] = user["id_utilisateur"]
            session['courriel'] = user["courriel"]
            session['est_admin'] = user["est_administrateur"]
            session['langue'] =  "fr_CA"
            flash("Connexion réussie.", "success")
            return redirect(url_for('services.accueil'), code=303)
        else:
            flash("Les identifiants saisis sont incorrects.", "error")
            return render_template('se_connecter.jinja',
                                   class_mdp="is-invalid",
                                   class_courriel="is-invalid",
                                   courriel = courriel,
                                   titre="Connexion")
    return render_template('se_connecter.jinja')

@bp_compte.route('/liste_utilisateurs')
def liste_utilisateurs():
    """Afficher la liste """
    if 'role' not in session or session['role'] != 'admin':
        flash("Accès réservé à l’administrateur.")

    with bd.creer_connexion() as conn:
        utilisateurs = bd.get_liste_compte(conn)
    return render_template('liste_utilisateurs.jinja', utilisateurs=utilisateurs)


@bp_compte.route("/supprimer_compte/<int:id_utilisateur>", methods=["POST"])
def supprimer_compte(id_utilisateur):
    """Permet à l’administrateur de supprimer un compte"""
    if session.get('role') != 'admin':
        flash("Accès réservé à l’administrateur.")
        return redirect("/")

    with bd.creer_connexion() as conn:
        bd.get_supprimer_utilisateur(conn, id_utilisateur)
    flash("Utilisateur supprimé avec succès.", "success")

    return redirect(url_for("liste_utilisateurs"))

