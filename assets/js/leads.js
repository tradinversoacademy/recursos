(function () {
  const endpoint = window.TRADINVERSO_LEADS_ENDPOINT || "";
  const endpointReady = endpoint && !endpoint.includes("PON_AQUI");
  const PROFILE_KEY = "tradinverso_lead_profile_v1";
  const ACCESS_KEY = "tradinverso_lead_access_v1";
  const PROFILE_DURATION = 90 * 24 * 60 * 60 * 1000;
  const SUCCESS_TITLE_ID = "tradinverso-success-title";

  function getParams() {
    // Solo devuelve valor si viene de verdad en la URL: los formularios ya
    // declaran su origen por defecto en el campo oculto.
    const params = new URLSearchParams(window.location.search);
    return {
      origen: params.get("origen") || params.get("utm_source") || ""
    };
  }

  function saveDemoLead(payload) {
    const key = "tradinverso_demo_leads";
    const previous = readStoredValue(key, []);
    writeStoredValue(key, previous.concat(payload).slice(-50));
  }

  function readStoredValue(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key) || "null") || fallback;
    } catch (error) {
      return fallback;
    }
  }

  function writeStoredValue(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      return false;
    }
  }

  function removeStoredValue(key) {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      // The form remains usable when storage is blocked by the browser.
    }
  }

  function normalizeEmail(value) {
    return String(value || "").trim().toLowerCase();
  }

  function getSavedProfile() {
    const profile = readStoredValue(PROFILE_KEY, null);
    if (!profile || !profile.nombre || !profile.email || Number(profile.expiresAt) <= Date.now()) {
      removeStoredValue(PROFILE_KEY);
      removeStoredValue(ACCESS_KEY);
      return null;
    }

    return profile;
  }

  function saveProfile(payload) {
    writeStoredValue(PROFILE_KEY, {
      nombre: payload.nombre,
      email: normalizeEmail(payload.email),
      expiresAt: Date.now() + PROFILE_DURATION
    });
  }

  function getAccessState() {
    const state = readStoredValue(ACCESS_KEY, null);
    if (!state || Number(state.expiresAt) <= Date.now() || !state.resources) {
      removeStoredValue(ACCESS_KEY);
      return { expiresAt: Date.now() + PROFILE_DURATION, resources: {} };
    }

    return state;
  }

  function getAccessKey(email, resource) {
    return normalizeEmail(email) + "::" + String(resource || "").trim().toLowerCase();
  }

  function hasRecordedAccess(email, resource) {
    return Boolean(getAccessState().resources[getAccessKey(email, resource)]);
  }

  function markRecordedAccess(email, resource) {
    const state = getAccessState();
    state.expiresAt = Date.now() + PROFILE_DURATION;
    state.resources[getAccessKey(email, resource)] = Date.now();
    writeStoredValue(ACCESS_KEY, state);
  }

  function clearSavedIdentity() {
    removeStoredValue(PROFILE_KEY);
    removeStoredValue(ACCESS_KEY);
  }

  function buildLeadUrl(payload) {
    const params = new URLSearchParams();

    Object.entries(payload).forEach(([key, value]) => {
      params.set(key, String(value || ""));
    });

    params.set("_cache", String(Date.now()));
    return endpoint + (endpoint.includes("?") ? "&" : "?") + params.toString();
  }

  async function sendLead(payload) {
    if (!endpointReady) {
      saveDemoLead(payload);
      return { demo: true };
    }

    await new Promise((resolve) => {
      const image = new Image();
      const timeout = window.setTimeout(resolve, 2200);

      image.onload = () => {
        window.clearTimeout(timeout);
        resolve();
      };
      image.onerror = () => {
        window.clearTimeout(timeout);
        resolve();
      };
      image.src = buildLeadUrl(payload);
    });

    return { demo: false };
  }

  // Registro sin formulario: lo usa site.js cuando alguien que ya tiene el pase
  // de biblioteca descarga un recurso. Sin esto, esas descargas no dejan rastro.
  window.tradinversoTrackLead = function (data) {
    if (!data || !data.email || !data.recurso) return;

    sendLead({
      fecha: new Date().toISOString(),
      nombre: String(data.nombre || "").trim(),
      email: String(data.email || "").trim(),
      recurso: data.recurso,
      via: data.via || "recurso",
      origen: getParams().origen || "organico",
      consentimiento: "si",
      notas: data.notas || ""
    });
  };

  function isContactRequest(form) {
    return /revision-caso/i.test(form.dataset.recurso || "");
  }

  function applySavedProfile(form, profile) {
    if (!profile) return;

    const nameInput = form.querySelector('[name="nombre"]');
    const emailInput = form.querySelector('[name="email"]');
    const consentInput = form.querySelector('[name="consentimiento"]');
    const resource = form.dataset.recurso || "recurso-sin-nombre";
    const contactRequest = isContactRequest(form);
    const alreadyRecorded = hasRecordedAccess(profile.email, resource);

    if (nameInput) nameInput.value = profile.nombre;
    if (emailInput) emailInput.value = profile.email;
    [nameInput, emailInput].forEach((input) => {
      const field = input && input.closest(".field");
      if (field) field.hidden = true;
    });

    if (consentInput && (!contactRequest || alreadyRecorded)) {
      consentInput.checked = true;
      const consent = consentInput.closest(".consent");
      if (consent) consent.hidden = true;
    }

    const identity = document.createElement("div");
    identity.className = "returning-lead";
    identity.innerHTML = `
      <div class="returning-lead-copy">
        <span>Datos reconocidos</span>
        <strong>Hola, ${escapeHtml(profile.nombre)}</strong>
        <small>${contactRequest && !alreadyRecorded
          ? "Solo confirma que quieres que contactemos contigo."
          : "No necesitas volver a escribir tu nombre y email en este dispositivo."}</small>
      </div>
      <button class="returning-lead-change" type="button">No soy yo</button>
    `;
    identity.querySelector("button").addEventListener("click", () => {
      clearSavedIdentity();
      window.location.reload();
    });
    form.prepend(identity);
  }

  function escapeHtml(value) {
    const element = document.createElement("span");
    element.textContent = String(value || "");
    return element.innerHTML;
  }

  function startDownload(url, filename) {
    const link = document.createElement("a");
    link.href = url;
    link.download = filename || "";
    link.hidden = true;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  // Calendly acepta el nombre y el email por query string: así el lead no
  // vuelve a escribir lo que ya ha puesto en el formulario.
  function buildCalendlyUrl(baseUrl, payload) {
    try {
      const url = new URL(baseUrl);
      url.searchParams.set("name", payload.nombre);
      url.searchParams.set("email", payload.email);
      return url.toString();
    } catch (error) {
      return baseUrl;
    }
  }

  // Si la descarga o la pestaña nueva no llegan a abrirse, el visitante tiene
  // aquí el enlace directo en lugar de quedarse sin el recurso.
  function setSuccessFallback(target, options) {
    const fallback = target.querySelector("[data-success-fallback]");
    if (!fallback) return;

    if (!options.fallbackUrl) {
      fallback.hidden = true;
      return;
    }

    const link = document.createElement("a");
    link.href = options.fallbackUrl;
    link.textContent = options.fallbackLabel || "Ábrelo aquí";
    if (options.fallbackDownload !== undefined) {
      link.setAttribute("download", options.fallbackDownload || "");
    } else {
      link.target = "_blank";
      link.rel = "noopener";
    }

    fallback.textContent = (options.fallbackText || "¿No se ha abierto?") + " ";
    fallback.appendChild(link);
    fallback.hidden = false;
  }

  function openSuccessModal(panel) {
    const overlay = document.querySelector("[data-success-overlay]");
    const slot = overlay && overlay.querySelector("[data-success-slot]");
    if (!overlay || !slot) return false;

    slot.appendChild(panel);
    overlay.hidden = false;
    document.body.classList.add("has-success-modal");

    const primary = overlay.querySelector(".community-button")
      || overlay.querySelector("[data-success-close]");
    if (primary) primary.focus({ preventScroll: true });
    return true;
  }

  function closeSuccessModal() {
    const overlay = document.querySelector("[data-success-overlay]");
    if (!overlay || overlay.hidden) return;

    overlay.hidden = true;
    document.body.classList.remove("has-success-modal");

    // Al cerrarlo vuelve a su hueco de la página: sigue siendo el siguiente paso.
    const anchor = document.querySelector("[data-success-anchor]");
    const panel = document.querySelector("[data-masterclass-promo]");
    if (anchor && panel) anchor.appendChild(panel);
  }

  // Cuando el recurso se descarga o se abre en otra pestaña, el panel se
  // muestra como modal: dejarlo dentro de la página lo deja en segundo plano
  // y el visitante nunca llega a ver el paso a la comunidad.
  function showSuccess(options) {
    const settings = options || {};
    const target = settings.target || document.querySelector("[data-masterclass-promo]");
    if (!target) return;

    const titulo = target.querySelector("[data-success-title]");
    if (titulo && settings.title) titulo.textContent = settings.title;
    setSuccessFallback(target, settings);

    target.hidden = false;

    const esPanelPropio = target.dataset.masterclassPromo !== undefined;
    if (settings.modal && esPanelPropio && openSuccessModal(target)) return;

    if (settings.scroll !== false) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  // site.js lo usa para quien ya tiene el pase y no pasa por el formulario.
  window.tradinversoShowSuccess = showSuccess;

  function initLeadForms() {
    const params = getParams();
    const savedProfile = getSavedProfile();

    document.querySelectorAll("[data-lead-form]").forEach((form) => {
      const status = form.querySelector("[data-form-status]");
      const origenInput = form.querySelector('[name="origen"]');

      if (origenInput && params.origen) origenInput.value = params.origen;
      applySavedProfile(form, savedProfile);

      form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const submitButton = form.querySelector('button[type="submit"]');
        const data = new FormData(form);
        const configuredRedirect = form.dataset.redirect || "";
        const download = form.dataset.download
          || (/\.pdf(?:$|[?#])/i.test(configuredRedirect) ? configuredRedirect : "");
        const calendly = form.dataset.calendly || "";
        const redirect = form.dataset.redirect || (download || calendly ? "" : "recurso.html");
        // Las páginas de contacto traen su propio bloque de confirmación: ahí
        // manda el de la página y no se abre modal.
        const pageSuccessTarget = form.dataset.successTarget
          ? document.querySelector(form.dataset.successTarget)
          : null;
        // Un destino externo (una plantilla en Drive, por ejemplo) se abre aparte
        // para no sacar al visitante del recurso.
        const externo = /^https?:\/\//i.test(redirect);
        const opensInNewTab = Boolean(calendly) || externo || (!download && /\.pdf(?:$|[?#])/i.test(redirect));
        const payload = {
          fecha: new Date().toISOString(),
          nombre: String(data.get("nombre") || "").trim(),
          email: String(data.get("email") || "").trim(),
          recurso: form.dataset.recurso || "recurso-sin-nombre",
          via: form.dataset.libraryAccess !== undefined ? "biblioteca" : "recurso",
          origen: String(data.get("origen") || params.origen || "organico"),
          consentimiento: data.get("consentimiento") ? "si" : "no",
          notas: ""
        };

        if (!payload.nombre || !payload.email || payload.consentimiento !== "si") {
          if (status) status.textContent = "Revisa nombre, email y consentimiento.";
          return;
        }

        const alreadyRecorded = hasRecordedAccess(payload.email, payload.recurso);
        if (submitButton) submitButton.disabled = true;
        if (status) {
          status.textContent = alreadyRecorded
            ? "Preparando tu recurso..."
            : "Guardando tus datos...";
        }
        const resourceWindow = opensInNewTab ? window.open("about:blank", "_blank") : null;

        try {
          const result = alreadyRecorded
            ? { demo: false, skipped: true }
            : await sendLead(payload);
          saveProfile(payload);
          markRecordedAccess(payload.email, payload.recurso);

          // Con los datos recién capturados, los enlaces a Calendly de esta
          // misma página ya no vuelven a pedirlos.
          if (typeof window.tradinversoDecorateLinks === "function") {
            window.tradinversoDecorateLinks(document);
          }

          // Registro desde la portada: concede el pase a toda la biblioteca.
          if (form.dataset.libraryAccess !== undefined) {
            if (window.TradinversoAccess) window.TradinversoAccess.grantPass(payload);
            if (status) status.textContent = "Acceso concedido. Ya puedes entrar a todos los recursos.";
            if (submitButton) submitButton.disabled = false;
            document.dispatchEvent(new CustomEvent("tradinverso:library-unlocked"));
            return;
          }

          if (calendly) {
            const calendlyUrl = buildCalendlyUrl(calendly, payload);
            if (status) status.textContent = "Abriendo el calendario con tus datos...";
            if (resourceWindow) {
              resourceWindow.opener = null;
              resourceWindow.location.href = calendlyUrl;
            } else {
              window.open(calendlyUrl, "_blank", "noopener");
            }
            // Respaldo visible por si el navegador bloquea la pestaña emergente.
            document.querySelectorAll("[data-calendly-fallback]").forEach((link) => {
              link.href = calendlyUrl;
            });
            showSuccess({
              target: pageSuccessTarget,
              modal: !pageSuccessTarget,
              title: "Ya puedes elegir día y hora",
              fallbackUrl: calendlyUrl,
              fallbackText: "¿No se ha abierto el calendario?",
              fallbackLabel: "Ábrelo aquí"
            });
            if (submitButton) submitButton.disabled = false;
            return;
          }

          if (download) {
            if (status) {
              status.textContent = result.demo
                ? "Modo prueba activo. Descarga iniciada."
                : alreadyRecorded
                  ? "Descarga iniciada."
                  : "Datos guardados. Descarga iniciada.";
            }
            startDownload(download, form.dataset.downloadName);
            showSuccess({
              target: pageSuccessTarget,
              modal: !pageSuccessTarget,
              title: "Tu guía se está descargando",
              fallbackUrl: download,
              fallbackText: "¿No ha empezado la descarga?",
              fallbackLabel: "Descárgala aquí",
              fallbackDownload: form.dataset.downloadName || ""
            });
            if (submitButton) submitButton.disabled = false;
            return;
          }

          if (redirect.startsWith("#")) {
            const target = document.querySelector(redirect);
            const hideAfterSuccess = form.dataset.hideAfterSuccess
              ? document.querySelector(form.dataset.hideAfterSuccess)
              : null;
            if (status) status.textContent = form.dataset.successMessage || "Datos enviados. Puedes ver el recurso.";
            if (submitButton) submitButton.disabled = false;
            if (target) {
              target.hidden = false;
              if (hideAfterSuccess) hideAfterSuccess.hidden = true;
              target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
            // El contenido revelado no es el final del recorrido, pero aquí el
            // visitante se queda en la página: el panel va debajo, sin modal
            // que le tape lo que acaba de desbloquear.
            const promo = document.querySelector("[data-masterclass-promo]");
            if (promo && promo !== target) {
              showSuccess({ target: promo, title: "Ya tienes acceso", scroll: false });
            }
            return;
          }

          if (status) {
            status.textContent = result.demo
              ? "Modo prueba activo. Abriendo el recurso..."
              : "Datos guardados. Abriendo el recurso...";
          }
          // El recurso se abre en otra pestaña y el navegador la enfoca. El
          // modal se queda esperando aquí para cuando el lead vuelva.
          if (opensInNewTab) {
            showSuccess({
              target: pageSuccessTarget,
              modal: !pageSuccessTarget,
              title: "Ya tienes acceso",
              fallbackUrl: redirect,
              fallbackText: "¿No se ha abierto la pestaña?",
              fallbackLabel: "Ábrela aquí"
            });
            if (submitButton) submitButton.disabled = false;
          }
          window.setTimeout(() => {
            if (resourceWindow) {
              resourceWindow.opener = null;
              resourceWindow.location.href = redirect;
            } else {
              window.location.href = redirect;
            }
          }, 650);
        } catch (error) {
          if (resourceWindow) resourceWindow.close();
          if (status) status.textContent = "No se ha podido guardar. Inténtalo otra vez.";
          if (submitButton) submitButton.disabled = false;
        }
      });
    });
  }

  function initChecklist() {
    const checklist = document.querySelector("[data-checklist]");
    if (!checklist) return;

    const checks = Array.from(checklist.querySelectorAll('input[type="checkbox"]'));
    const percent = document.querySelector("[data-progress-percent]");
    const ring = document.querySelector("[data-progress-ring]");
    const decision = document.querySelector("[data-decision]");
    const reset = document.querySelector("[data-reset-checklist]");
    const storageKey = checklist.dataset.storageKey || "tradinverso_checklist";
    const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");

    checks.forEach((check) => {
      check.checked = Boolean(saved[check.id]);
      check.addEventListener("change", update);
    });

    if (reset) {
      reset.addEventListener("click", () => {
        checks.forEach((check) => {
          check.checked = false;
        });
        update();
      });
    }

    function update() {
      const done = checks.filter((check) => check.checked).length;
      const value = checks.length ? Math.round((done / checks.length) * 100) : 0;
      const nextSaved = {};

      checks.forEach((check) => {
        nextSaved[check.id] = check.checked;
      });

      localStorage.setItem(storageKey, JSON.stringify(nextSaved));
      if (percent) percent.textContent = value + "%";
      if (ring) ring.style.setProperty("--progress", Math.round(value * 3.6) + "deg");
      if (decision) {
        decision.textContent = value >= 85
          ? "Entrada validada. Si el precio confirma, la operación tiene plan."
          : value >= 60
            ? "Faltan filtros importantes. Espera confirmación o reduce exposición."
            : "No hay suficiente calidad. La mejor operación puede ser no entrar.";
      }
    }

    update();
  }

  function initSuccessPanel() {
    if (!document.querySelector("[data-lead-form]") || document.querySelector("[data-masterclass-promo]")) return;

    const footer = document.querySelector(".social-footer");
    if (!footer) return;

    // Tras descargar, el paso más pequeño y más probable es entrar a la
    // comunidad. La clase gratuita queda como segundo paso en el mismo panel.
    const comunidad = window.TRADINVERSO_COMUNIDAD_URL || "";
    const section = document.createElement("section");
    section.className = "masterclass-promo success-promo";
    section.dataset.masterclassPromo = "";
    section.hidden = true;
    section.innerHTML = `
      <div>
        <span class="masterclass-promo-badge">Ya es tuyo</span>
        <h2 id="${SUCCESS_TITLE_ID}" data-success-title>Tu guía se está descargando</h2>
        <p class="success-fallback" data-success-fallback hidden></p>
        <p>Ahora entra en la comunidad gratuita de WhatsApp: hacemos operativas en directo, comparto contenido exclusivo que no publico en ningún otro sitio, aviso de cada recurso nuevo y puedes preguntar tus dudas.</p>
        <ul class="community-points">
          <li>Operativas en directo</li>
          <li>Contenido gratuito en exclusiva</li>
          <li>Avisos de nuevos recursos</li>
          <li>Resolvemos tus dudas</li>
        </ul>
      </div>
      <div class="success-actions-stack">
        ${comunidad
          ? `<a class="masterclass-button community-button" href="${comunidad}" target="_blank" rel="noopener">Entrar a la comunidad <span aria-hidden="true">→</span></a>`
          : ""}
        <a class="success-secondary" href="https://clase.tradinverso.com/" target="_blank" rel="noopener">O ver primero la clase gratuita <span aria-hidden="true">→</span></a>
      </div>
    `;

    // El panel vive en la página dentro de este hueco y se mueve al modal
    // cuando hace falta, así que la copia y los listeners son siempre los mismos.
    const anchor = document.createElement("div");
    anchor.dataset.successAnchor = "";
    anchor.appendChild(section);

    const leadSection = document.querySelector("[data-lead-form]")?.closest("section");
    if (leadSection) {
      leadSection.after(anchor);
    } else {
      footer.before(anchor);
    }

    const overlay = document.createElement("div");
    overlay.className = "success-overlay";
    overlay.dataset.successOverlay = "";
    overlay.hidden = true;
    overlay.innerHTML = `
      <div class="success-overlay-shell" role="dialog" aria-modal="true" aria-labelledby="${SUCCESS_TITLE_ID}">
        <button class="success-close" type="button" data-success-close aria-label="Cerrar">&times;</button>
        <div data-success-slot></div>
      </div>
    `;
    document.body.appendChild(overlay);

    overlay.addEventListener("click", (event) => {
      if (event.target === overlay || event.target.closest("[data-success-close]")) {
        closeSuccessModal();
      }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeSuccessModal();
    });

    if (typeof window.tradinversoDecorateLinks === "function") {
      window.tradinversoDecorateLinks(section);
    }

    trackPromoClicks(section);
  }

  // Deja constancia en la hoja de quién da el paso a la comunidad y desde qué
  // recurso, para saber cuál de ellos convierte mejor.
  function trackPromoClicks(section) {
    const origen = getResourceSlug();

    [
      { selector: ".community-button", recurso: "comunidad-whatsapp", via: "comunidad" },
      { selector: ".success-secondary", recurso: "clase-gratuita", via: "clase" }
    ].forEach(({ selector, recurso, via }) => {
      const link = section.querySelector(selector);
      if (!link) return;

      let registrado = false;
      link.addEventListener("click", () => {
        if (registrado) return;
        registrado = true;

        const profile = getSavedProfile();
        if (!profile) return;

        window.tradinversoTrackLead({
          nombre: profile.nombre,
          email: profile.email,
          recurso: recurso,
          via: via,
          notas: origen ? "desde " + origen : ""
        });
      });
    });
  }

  function getResourceSlug() {
    const parts = window.location.pathname.split("/").filter(Boolean);
    for (let i = parts.length - 1; i >= 0; i--) {
      if (parts[i] === "recursos" && parts[i + 1] && parts[i + 1].indexOf(".html") === -1) {
        return parts[i + 1];
      }
    }
    return "";
  }

  document.addEventListener("DOMContentLoaded", () => {
    initLeadForms();
    initChecklist();
    initSuccessPanel();
  });
})();
