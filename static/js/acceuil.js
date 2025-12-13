/**
 * Pour faciliter les requêtes Ajax.
 */

/* eslint-disable no-unused-vars */


/*global envoyerRequeteAjax*/

"use strict";
let controleur = null;
const liste_services = document.getElementById("services");
let role = liste_services.dataset.role;
async function afficher_services() {


    try {
        const resultats = await envoyerRequeteAjax(
            "/api/accueil",
            "GET",
            {},
            controleur
        );

        afficherResultats(resultats);
        console.log("parfait");
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
            liste_services.innerHTML = "";
            let html = "";
            console.log(resultats.length);
                for (const service of resultats) {
                    const photo = service.photo
                    const reserveBtn = (service.est_proprietaire === false) ? `<a href="/services/reserver/${service.id_service}" class="btn btn-primary m-2">Reserver</a>` : '';
                    const supprimerBtn = (service.est_proprietaire === true || role==="admin") ? `<a href="/services/supprimer/${service.id_service}" class="btn btn-primary m-2">Supprimer</a>` : '';
                    html += `
                    <div class="col-md-4 mb-3">
                        <div class="card shadow-sm">+
                            <img src="${photo}" class="card-img-top card-img p-2" alt="Image par défaut">
                            <div class="card-body">
                                <h5 class="card-title">${service.titre}</h5>
                                <p class="card-text">
                                    <strong>Catégorie :</strong> ${service.nom_categorie} <br>
                                    <strong>Localisation :</strong> ${service.localisation}
                                </p>
                                <a href="/services/${service.id_service}" class="btn btn-primary m-2">Voir détails</a>
                                ${reserveBtn}
                                ${supprimerBtn}
                            </div>
                        </div>
                    </div>`;
                    console.log("service affiché");
                }
                liste_services.innerHTML = html;
            }

function initialisation() {
    setInterval(afficher_services, 5000);
}

window.addEventListener("load", initialisation);
