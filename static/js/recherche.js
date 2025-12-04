/**
 * Pour faciliter les requêtes Ajax.
 */

/* eslint-disable no-unused-vars */


/*global envoyerRequeteAjax*/

"use strict";

let controleur = null;

const recherche = document.getElementById("search");
const chargement = document.getElementById("chargement");
const listeResultats = document.getElementById("resultats-recherche");

function sauvegarderHistorique(terme) {
    let historique = JSON.parse(localStorage.getItem("historiqueRecherche")) || [];

    // éviter doublons
    if (!historique.includes(terme)) {
        historique.unshift(terme);
    }

    // max 10 items
    historique = historique.slice(0, 10);

    localStorage.setItem("historiqueRecherche", JSON.stringify(historique));
}

async function rechercher() {
    const aChercher = recherche.value.trim();

    if (aChercher.length < 3) {
        listeResultats.classList.add("d-none");
        listeResultats.innerHTML = "";
        return;
    }

    chargement.classList.remove("d-none");

    if (controleur) controleur.abort();
    controleur = new AbortController();

    try {
        const resultats = await envoyerRequeteAjax(
            "/api/suggestion-recherche",
            "GET",
            { query: aChercher },
            controleur
        );

        afficherResultats(resultats);
        chargement.classList.add("d-none");
        controleur = null;
    } catch (err) {
        if (err.name !== "AbortError") {
            console.error("Erreur AJAX :", err);
        }
        listeResultats.innerHTML = "";
        listeResultats.classList.add("d-none");
        chargement.classList.add("d-none");
    }
}

function afficherResultats(resultats) {
    listeResultats.innerHTML = "";

    if (!resultats || resultats.length === 0) {
        listeResultats.classList.add("d-none");
        return;
    }

    for (const service of resultats) {
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-action";
        li.textContent = service.titre;
        li.style.cursor = "pointer";

        li.addEventListener("click", () => {
            sauvegarderHistorique(service.titre);
            window.location.href = `/services/details_service/${service.id_service}`;
        });

        listeResultats.appendChild(li);
    }

    listeResultats.classList.remove("d-none");
}

function lancerRechercheFinale() {
    const terme = recherche.value.trim();
    if (terme.length >= 1) {
        sauvegarderHistorique(terme);
        window.location.href = `/services/recherche?query=${encodeURIComponent(terme)}`;
    }
}

function initialisation() {
    recherche.addEventListener("input", rechercher);

    // Appui sur Entrée → lancer recherche
    recherche.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            lancerRechercheFinale();
        }
    });

    // Cacher suggestions si clic ailleurs
    document.addEventListener("click", (e) => {
        if (!listeResultats.contains(e.target) && e.target !== recherche) {
            listeResultats.classList.add("d-none");
        }
    });
}

window.addEventListener("load", initialisation);
