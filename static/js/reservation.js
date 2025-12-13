/**
 * Pour faciliter les requêtes Ajax.
 */

/* eslint-disable no-unused-vars */


/*global envoyerRequeteAjax*/

"use strict";
let controleur = null;
const heure = document.getElementById("heure");
const date = document.getElementById("date");
const buttonReserver = document.getElementById("reserver");
async function verifier_Dispo() {
    const h = heure.value.trim();
    const d = date.value.trim();
    console.log(h);
    console.log(d);
    if (h.length == 0 || d.length == 0) {
        return;
    }
    try {
        // Annule la requête précédente si elle est toujours en cours
        if (controleur) {
            controleur.abort();
        }
        controleur = new AbortController();
        const resultats = await envoyerRequeteAjax(
            "/api/verifier-disponibilite",
            "GET",
            { date: d, heure: h, id_service: buttonReserver.dataset.service },
            controleur
        );
        console.log("Résultat disponibilité:", resultats);
        if (resultats.disponible === false) {
            buttonReserver.disabled = true;
            heure.classList.add("is-invalid");
            date.classList.add("is-invalid");
        } else {
            buttonReserver.disabled = false;
            heure.classList.remove("is-invalid");
            date.classList.remove("is-invalid");
        }
    } catch (err) {
        if (err.name !== "AbortError") {
            console.error("Erreur AJAX :", err);
        }
    }
}

function initialisation() {
    heure.addEventListener("input", verifier_Dispo);
    date.addEventListener("input", verifier_Dispo);
}

window.addEventListener("load", initialisation);
