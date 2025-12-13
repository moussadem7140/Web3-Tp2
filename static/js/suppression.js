/**
 * Pour faciliter les requêtes Ajax.
 */

/* eslint-disable no-unused-vars */


/*global envoyerRequeteAjax*/

"use strict";
const utilisateurs = document.getElementById("utilisateurs");
const nombre = utilisateurs.dataset.nombre;
async function supprimer(event) {
    try {
        event.preventDefault();
        const id = event.target.dataset.utilisateur;
        console.log("Résultat suppression:");
        const resultats = await envoyerRequeteAjax(
            "/api/supprimer_utilisateur",
            "GET",
            { id_utilisateur: id },
        );
        if (resultats.success) {
            const row = document.getElementById(`afficher-${id}`);
            row.remove();
            console.log("Utilisateur supprimé avec succès");
        }
        else {
            console.error("Échec de la suppression de l'utilisateur");
        }
    } catch (err) {
        if (err.name !== "AbortError") {
            console.error("Erreur AJAX :", err);
        }
    }
}


function initialisation() {
    console.log(nombre);
    for (let i = 0; i < parseInt(nombre); i++) {
        const boutonSupprimer = document.getElementById(`supprimer-${i}`);
        console.log(`supprimer-${i}`);
        boutonSupprimer.addEventListener("click", supprimer);
    }
    console.log("Initialisation suppression des utilisateurs");
}
window.addEventListener("load", initialisation);
