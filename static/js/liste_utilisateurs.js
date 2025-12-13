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
    localStorage.setItem("historiqueRecherche", JSON.stringify(historique));
}

async function rechercher() {
    const aChercher = recherche.value.trim();

    if (aChercher.length < 4) {
        listeResultats.classList.add("d-none");
        listeResultats.innerHTML = "";
        return;
    }

    chargement.classList.remove("d-none");


    try {
        const resultats = await envoyerRequeteAjax(
            "/api/utilisateurs-recherche",
            "GET",
            { user: aChercher },
            controleur
        );

        afficherResultats(resultats);
        chargement.classList.add("d-none");
        controleur = null;
        console.log("Aucun  trouvé");
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
        console.log("Aucun résultat trouvé");
        return;
    }

    for (const service of resultats) {
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-action";
        li.textContent = service.courriel;
        li.style.cursor = "pointer";

        li.addEventListener("click", () => {
            sauvegarderHistorique(service.courriel);
            window.location.href = `/compte/liste_utilisateurs?id_unique=${service.id_utilisateur}`;
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
