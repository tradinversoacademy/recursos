(function () {
  "use strict";

  var VSL_URL = "https://clase.tradinverso.com/";

  function getResourceSlug() {
    // La web vive en /recursos/ (nombre del repo) y los recursos en /recursos/recursos/<slug>/,
    // así que buscamos el último segmento "recursos" seguido de una carpeta.
    var parts = window.location.pathname.split("/").filter(Boolean);
    for (var i = parts.length - 1; i >= 0; i--) {
      if (parts[i] === "recursos" && parts[i + 1] && parts[i + 1].indexOf(".html") === -1) {
        return parts[i + 1];
      }
    }
    return null;
  }

  function decorateLinks(root) {
    var scope = root || document;
    scope.querySelectorAll('a[href*="clase.tradinverso.com"], a[href*="calendly.com"]').forEach(function (link) {
      try {
        var url = new URL(link.href);
        if (url.searchParams.get("utm_source")) return;
        url.searchParams.set("utm_source", "recursos");
        link.href = url.toString();
      } catch (error) {
        // Un enlace malformado no debe romper el resto de la página.
      }
    });
  }

  window.tradinversoDecorateLinks = decorateLinks;

  function initTopbarCta() {
    var topbar = document.querySelector(".topbar");
    if (!topbar || topbar.querySelector(".nav-pill-cta")) return;

    var cta = document.createElement("a");
    cta.className = "nav-pill nav-pill-cta";
    cta.href = VSL_URL;
    cta.target = "_blank";
    cta.rel = "noopener";
    cta.appendChild(document.createTextNode("Clase gratuita "));
    var arrow = document.createElement("span");
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "→";
    cta.appendChild(arrow);

    var pill = topbar.querySelector(".nav-pill");
    var row = topbar.querySelector(".button-row");
    if (row) {
      row.appendChild(cta);
    } else if (pill && pill.parentElement === topbar) {
      row = document.createElement("div");
      row.className = "button-row";
      topbar.insertBefore(row, pill);
      row.appendChild(pill);
      row.appendChild(cta);
    } else {
      topbar.appendChild(cta);
    }
  }

  function buildRelatedCard(resource) {
    var card = document.createElement("article");
    card.className = "resource-list-card";

    var top = document.createElement("div");
    top.className = "resource-list-top";
    var symbol = document.createElement("span");
    symbol.className = "resource-symbol";
    symbol.textContent = resource.symbol;
    var type = document.createElement("span");
    type.className = "resource-list-type";
    type.textContent = resource.type;
    top.appendChild(symbol);
    top.appendChild(type);

    var title = document.createElement("h3");
    title.textContent = resource.title;
    var description = document.createElement("p");
    description.textContent = resource.description;
    var link = document.createElement("a");
    link.href = "../" + resource.slug + "/index.html";
    link.appendChild(document.createTextNode(resource.cta + " "));
    var arrow = document.createElement("span");
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "→";
    link.appendChild(arrow);

    card.appendChild(top);
    card.appendChild(title);
    card.appendChild(description);
    card.appendChild(link);
    return card;
  }

  function initRelatedResources() {
    var slug = getResourceSlug();
    var footer = document.querySelector(".social-footer");
    var catalog = window.TRADINVERSO_RESOURCES || [];
    if (!slug || !footer || !catalog.length) return;
    if (document.querySelector("[data-related-resources]")) return;

    var current = catalog.find(function (resource) {
      return resource.slug === slug;
    });
    var available = catalog.filter(function (resource) {
      return resource.slug !== slug && !resource.hidden;
    });
    var sameCategory = available.filter(function (resource) {
      return current && resource.category === current.category;
    });
    var others = available.filter(function (resource) {
      return !current || resource.category !== current.category;
    });
    var related = sameCategory.concat(others).slice(0, 3);
    if (!related.length) return;

    var section = document.createElement("section");
    section.className = "library-section related-resources";
    section.dataset.relatedResources = "";
    section.setAttribute("aria-label", "Más recursos gratuitos");

    var heading = document.createElement("div");
    heading.className = "section-heading";
    var headingCopy = document.createElement("div");
    var kicker = document.createElement("span");
    kicker.className = "section-kicker";
    kicker.textContent = "Sigue aprendiendo";
    var title = document.createElement("h2");
    title.textContent = "Más recursos gratuitos";
    headingCopy.appendChild(kicker);
    headingCopy.appendChild(title);
    var libraryLink = document.createElement("a");
    libraryLink.className = "nav-pill";
    libraryLink.href = "../../index.html";
    libraryLink.textContent = "Ver la biblioteca completa";
    heading.appendChild(headingCopy);
    heading.appendChild(libraryLink);

    var grid = document.createElement("div");
    grid.className = "resource-list-grid";
    related.forEach(function (resource) {
      grid.appendChild(buildRelatedCard(resource));
    });

    section.appendChild(heading);
    section.appendChild(grid);
    footer.parentElement.insertBefore(section, footer);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTopbarCta();
    initRelatedResources();
    decorateLinks(document);
  });
})();
