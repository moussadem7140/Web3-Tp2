/**
 * Pour faciliter les requêtes Ajax.
 */

/* eslint-disable no-unused-vars */


/*global envoyerRequeteAjax*/

"use strict";

/* eslint-disable no-useless-escape */
const regexEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const REGEX_HTML = /^[^<>]*$/;

const courriel = document.getElementById("courriel");

/**
 * Validation du courriel via AJAX au blur, uniquement si le format est correct
 */
function validationCourriel() {

    courriel.addEventListener("blur", async function () {
        const valeur = this.value.trim();

        if (valeur === "" || !regexEmail.test(valeur) || !REGEX_HTML.test(valeur)) {
            courriel.classList.add("is-invalid");
            courriel.nextElementSibling.textContent = "Votre courriel doit être correct et ne doit pas contenir de caractères spéciaux.";
            return;
        }

        try {
            const parametres = { courriel: valeur };
            const resultat = await envoyerRequeteAjax("../api/verifier-courriel", "GET", parametres);

            if (resultat.existe) {
                courriel.classList.add("is-invalid");
                courriel.nextElementSibling.textContent = "Ce courriel est déjà utilisé.";
            } else {
                courriel.classList.remove("is-invalid");
                courriel.nextElementSibling.textContent = "";
            }
        } catch (error) {
            console.error("Erreur AJAX :", error);
        }
    });
}

/**
 * Valide un champ localement (sans AJAX)
 */
function validerChamp(champ, nomChamp, tousChamps) {
    const valeur = champ.value.trim();

    champ.classList.remove("is-invalid");
    champ.nextElementSibling.textContent = "";

    switch (nomChamp) {
        case "courriel":
            if (!regexEmail.test(valeur) || !REGEX_HTML.test(valeur)) {
                champ.classList.add("is-invalid");
                champ.nextElementSibling.textContent = "Votre courriel doit être correct et ne doit pas contenir de caractères spéciaux.";
            }
            break;

        case "mdp":
            if (valeur === "") {
                champ.classList.add("is-invalid");
                champ.nextElementSibling.textContent = "Le mot de passe est obligatoire.";
            }
            break;

        case "mdp_repeat":
            if (valeur === "" || valeur !== tousChamps.mdp.value.trim()) {
                champ.classList.add("is-invalid");
                champ.nextElementSibling.textContent = "Les mots de passe ne correspondent pas.";
            }
            break;
    }
}
/**
 * Ajoute des écouteurs pour valider les champs individuellement au blur et nettoyer les erreurs à l'input
 */
function validationChampsIndividuels() {
    const champs = {
        courriel: document.getElementById("courriel"),
        mdp: document.getElementById("mdp"),
        mdp_repeat: document.getElementById("mdp_repeat")
    };

    for (let nomChamp in champs) {
        const champ = champs[nomChamp];

        champ.addEventListener("blur", function () {
            validerChamp(champ, nomChamp, champs);
        });

        champ.addEventListener("input", function () {
            champ.classList.remove("is-invalid");
            champ.nextElementSibling.textContent = "";
        });
    }
}

/**
 * Validation complète au submit
 */
async function validerFormulaire(event) {
    event.preventDefault();

    const champs = {
        courriel: document.getElementById("courriel"),
        mdp: document.getElementById("mdp"),
        mdp_repeat: document.getElementById("mdp_repeat")
    };

    let formulaireValide = true;
    for (let nomChamp in champs) {
        const champ = champs[nomChamp];
        validerChamp(champ, nomChamp, champs);
        if (champ.classList.contains("is-invalid")) {
            formulaireValide = false;
        }
    }
    if (!formulaireValide) {
        return;
    }

    try {
        const parametres = { courriel: champs.courriel.value.trim() };
        const resultat = await envoyerRequeteAjax("../api/verifier-courriel", "GET", parametres);

        if (resultat.existe) {
            champs.courriel.classList.add("is-invalid");
            champs.courriel.nextElementSibling.textContent = "Ce courriel est déjà utilisé.";
            return;
        }
    } catch (error) {
        console.error("Erreur AJAX :", error);
        return;
    }

    event.target.submit();
}

/**
 * Initialisation au chargement de la page
 */
function initialisation() {
    validationCourriel();
    validationChampsIndividuels();

    document.getElementById("formCreerCompte").addEventListener("submit", validerFormulaire);
}

window.addEventListener("load", initialisation);
