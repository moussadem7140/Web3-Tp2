"use strict";

/*global envoyerRequeteAjax*/

async function supprimerService(event) {
    try {
        event.preventDefault();

        const id = event.target.dataset.service;
        console.log("Suppression du service :", id);

        const resultats = await envoyerRequeteAjax(
            "/api/supprimer_service",
            "GET",
            { id_service: id }
        );

        if (resultats.success) {
            const carte = document.getElementById(`service-${id}`);
            if (carte) carte.remove();
            console.log("Service supprimé avec succès");
        } else {
            console.error("Échec de la suppression du service :", resultats.message);
        }
    } catch (err) {
        if (err.name !== "AbortError") {
            console.error("Erreur AJAX :", err);
        }
    }
}

function initialisationSuppressionServices() {
    const boutons = document.querySelectorAll(".btn-supprimer-service");
    boutons.forEach(bouton => {
        bouton.addEventListener("click", supprimerService);
    });
    console.log("Initialisation suppression des services terminée");
}

window.addEventListener("load", initialisationSuppressionServices);
