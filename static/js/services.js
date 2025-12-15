/*global*/

"use strict";

let offset = 0;
const limit = 6;

// Crée une carte HTML pour un service
function creerCarteService(service) {
    const col = document.createElement("div");
    col.className = "col-md-4 mb-3";

    const card = document.createElement("div");
    card.className = "card";

    const img = document.createElement("img");
    img.src = `/static/images/ajouts/${service.photo}`;
    img.width = 100;
    img.height = 250;
    img.className = "card-img-top";
    img.alt = "Image service";

    const cardBody = document.createElement("div");
    cardBody.className = "card-body";

    const titre = document.createElement("h5");
    titre.className = "card-title";
    titre.textContent = service.titre;

    const texte = document.createElement("p");
    texte.className = "card-text";
    texte.innerHTML = `<strong>Catégorie :</strong> ${service.nom_categorie}<br>
                       <strong>Localisation :</strong> ${service.localisation}`;

    const btnDetails = document.createElement("a");
    btnDetails.href = `/services/details_service/${service.id_service}`;
    btnDetails.className = "btn btn-primary m-2";
    btnDetails.textContent = "Voir détails";

    cardBody.appendChild(titre);
    cardBody.appendChild(texte);
    cardBody.appendChild(btnDetails);

    if (sessionStorage.getItem('identifiant') && !service.est_proprietaire) {
        const btnReserver = document.createElement("a");
        btnReserver.href = `/services/reserver/${service.id_service}`;
        btnReserver.className = "btn btn-primary m-2";
        btnReserver.textContent = "Réserver";
        cardBody.appendChild(btnReserver);
    }

    if (sessionStorage.getItem('role') === "admin" || service.est_proprietaire) {
        const btnSupprimer = document.createElement("a");
        btnSupprimer.href = `/services/supprimer/${service.id_service}`;
        btnSupprimer.className = "btn btn-danger m-2";
        btnSupprimer.textContent = "Supprimer";
        cardBody.appendChild(btnSupprimer);
    }

    card.appendChild(img);
    card.appendChild(cardBody);
    col.appendChild(card);
    return col;
}

async function chargerServices() {
    const response = await fetch(`/api/services?offset=${offset}&limit=${limit}`);
    const services = await response.json();

    const row = document.getElementById("row-services");

    if (!services || services.length === 0) {
        if (offset === 0) {
            const p = document.createElement("p");
            p.textContent = "Aucun service disponible.";
            row.appendChild(p);
        }
        return;
    }
    for (let i = 0; i < services.length; i++) {
        const service = services[i];
        const carte = creerCarteService(service);
        row.appendChild(carte);
    }

    offset += services.length;
}

function basDePageEstAffiche() {
    return (window.innerHeight + window.scrollY) >= (document.body.offsetHeight - 100);
}

function gererScroll() {
    if (basDePageEstAffiche()) {
        chargerServices();
    }
}

async function initialisation() {
    try{
       await chargerServices();
       while (document.body.offsetHeight < window.innerHeight) {
            const servicesAvant = offset;
            await chargerServices();
            if (offset === servicesAvant) break;
        }
       window.addEventListener("scroll", gererScroll);
    }catch(error){
        console.log(error);
    }

}

window.addEventListener("load", initialisation);

