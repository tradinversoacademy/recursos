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

  // Perfil que leads.js guarda al enviar cualquier formulario (90 días).
  function getSavedProfile() {
    try {
      var profile = JSON.parse(localStorage.getItem("tradinverso_lead_profile_v1") || "null");
      if (!profile || !profile.nombre || !profile.email || Number(profile.expiresAt) <= Date.now()) return null;
      return profile;
    } catch (error) {
      return null;
    }
  }

  function decorateLinks(root) {
    var scope = root || document;
    var profile = getSavedProfile();

    scope.querySelectorAll('a[href*="clase.tradinverso.com"], a[href*="calendly.com"]').forEach(function (link) {
      try {
        var url = new URL(link.href);
        var isCalendly = url.hostname.indexOf("calendly.com") !== -1;

        // Si ya conocemos al lead, Calendly recibe sus datos y no se los vuelve a pedir.
        if (isCalendly && profile && !url.searchParams.get("email")) {
          url.searchParams.set("name", profile.nombre);
          url.searchParams.set("email", profile.email);
        }

        if (!url.searchParams.get("utm_source")) {
          url.searchParams.set("utm_source", "recursos");
        }
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
      return current && resource.category === current.category && !resource.featured;
    });
    var others = available.filter(function (resource) {
      return sameCategory.indexOf(resource) === -1 && !resource.featured;
    });
    var featured = available.filter(function (resource) {
      return resource.featured;
    });

    // Dos recursos afines y uno destacado: el visitante siempre tiene a mano
    // el camino hacia el programa.
    var related = sameCategory.concat(others).slice(0, 2);
    if (featured.length) {
      related.push(featured[related.length % featured.length]);
    }
    related = related.concat(sameCategory.concat(others).slice(2)).slice(0, 3);
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

  // Quien tiene el pase de biblioteca ya se registró: en los recursos no se le
  // vuelve a pedir nada, solo se le da lo que venía a buscar.
  function initLibraryPass() {
    var access = window.TradinversoAccess;
    if (!access || !access.hasPass()) return;

    var pass = access.getPass();

    document.querySelectorAll("[data-lead-form]").forEach(function (form) {
      if (form.dataset.libraryAccess !== undefined) return;

      var panel = form.closest(".lead-panel") || form.parentElement;
      var download = form.dataset.download
        || (/\.pdf(?:$|[?#])/i.test(form.dataset.redirect || "") ? form.dataset.redirect : "");
      var calendly = form.dataset.calendly || "";
      var redirect = form.dataset.redirect || "";

      var unlocked = document.createElement("div");
      unlocked.className = "gate-known";

      var identity = document.createElement("div");
      identity.className = "returning-lead";
      identity.innerHTML = '<div class="returning-lead-copy">'
        + "<span>Acceso completo</span>"
        + "<strong></strong>"
        + "<small>Tienes la biblioteca desbloqueada. Este recurso es tuyo.</small>"
        + "</div>";
      identity.querySelector("strong").textContent = "Hola, " + pass.nombre;
      unlocked.appendChild(identity);

      var action = document.createElement("a");
      action.className = "primary-button";

      if (download) {
        action.href = download;
        action.setAttribute("download", form.dataset.downloadName || "");
        action.textContent = "Descargar ahora ";
      } else if (calendly) {
        var url = calendly;
        try {
          var parsed = new URL(calendly);
          parsed.searchParams.set("name", pass.nombre);
          parsed.searchParams.set("email", pass.email);
          url = parsed.toString();
        } catch (error) {
          // Se usa el enlace tal cual.
        }
        action.href = url;
        action.target = "_blank";
        action.rel = "noopener";
        action.textContent = "Elegir día y hora ";
      } else if (redirect.startsWith("#")) {
        action.href = redirect;
        action.textContent = "Ver el contenido ";
        action.addEventListener("click", function (event) {
          event.preventDefault();
          var target = document.querySelector(redirect);
          var hideAfter = form.dataset.hideAfterSuccess
            ? document.querySelector(form.dataset.hideAfterSuccess)
            : null;
          if (target) {
            target.hidden = false;
            if (hideAfter) hideAfter.hidden = true;
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      } else if (/^https?:\/\//i.test(redirect)) {
        action.href = redirect;
        action.target = "_blank";
        action.rel = "noopener";
        action.textContent = "Abrir la plantilla ";
      } else {
        action.href = redirect || "recurso.html";
        action.textContent = "Abrir el recurso ";
      }

      var arrow = document.createElement("span");
      arrow.setAttribute("aria-hidden", "true");
      arrow.textContent = "→";
      action.appendChild(arrow);

      // Sin formulario de por medio, la descarga no dejaría rastro en la hoja.
      // Se registra al pulsar, una sola vez por recurso y sesión.
      var registrado = false;
      action.addEventListener("click", function () {
        if (!registrado) {
          registrado = true;
          if (typeof window.tradinversoTrackLead === "function") {
            window.tradinversoTrackLead({
              nombre: pass.nombre,
              email: pass.email,
              recurso: form.dataset.recurso || "recurso-sin-nombre"
            });
          }
        }

        // Quien tiene el pase se salta el formulario, así que sin esto nunca
        // vería el paso a la comunidad. Se le muestra el mismo panel.
        if (typeof window.tradinversoShowSuccess !== "function" || calendly) return;

        if (download) {
          window.tradinversoShowSuccess({
            modal: true,
            title: "Tu guía se está descargando",
            fallbackUrl: download,
            fallbackText: "¿No ha empezado la descarga?",
            fallbackLabel: "Descárgala aquí",
            fallbackDownload: form.dataset.downloadName || ""
          });
        } else if (/^https?:\/\//i.test(redirect)) {
          window.tradinversoShowSuccess({
            modal: true,
            title: "Ya tienes acceso",
            fallbackUrl: redirect,
            fallbackText: "¿No se ha abierto la pestaña?",
            fallbackLabel: "Ábrela aquí"
          });
        }
      });

      unlocked.appendChild(action);

      form.hidden = true;
      panel.appendChild(unlocked);
    });
  }

  // La barra solo se separa del fondo cuando ya hay scroll: arriba del todo
  // se ve como siempre, sin línea ni sombra.
  function initStickyTopbar() {
    var topbar = document.querySelector(".topbar");
    if (!topbar) return;

    function marcar(pegada) {
      topbar.classList.toggle("is-stuck", pegada);
    }

    // El observador detecta el momento exacto en que la barra toca el borde
    // superior, sin depender de que lleguen eventos de scroll.
    if (typeof window.IntersectionObserver === "function") {
      new IntersectionObserver(function (entradas) {
        marcar(entradas[0].intersectionRatio < 1);
      }, { threshold: [1], rootMargin: "-1px 0px 0px 0px" }).observe(topbar);
      return;
    }

    var pendiente = false;
    window.addEventListener("scroll", function () {
      if (pendiente) return;
      pendiente = true;
      window.requestAnimationFrame(function () {
        pendiente = false;
        marcar(window.scrollY > 8);
      });
    }, { passive: true });
    marcar(window.scrollY > 8);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTopbarCta();
    initStickyTopbar();
    initRelatedResources();
    initLibraryPass();
    decorateLinks(document);
  });
})();
