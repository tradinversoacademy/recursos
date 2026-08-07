(function () {
  const endpoint = window.TRADINVERSO_LEADS_ENDPOINT || "";
  const endpointReady = endpoint && !endpoint.includes("PON_AQUI");
  const PROFILE_KEY = "tradinverso_lead_profile_v1";
  const ACCESS_KEY = "tradinverso_lead_access_v1";
  const PROFILE_DURATION = 90 * 24 * 60 * 60 * 1000;

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

  function revealSuccessTarget(form) {
    const selector = form.dataset.successTarget;
    const target = selector
      ? document.querySelector(selector)
      : document.querySelector("[data-masterclass-promo]");
    if (!target) return;

    target.hidden = false;
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }

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
        const redirect = form.dataset.redirect || (download ? "" : "recurso.html");
        const opensInNewTab = !download && /\.pdf(?:$|[?#])/i.test(redirect);
        const payload = {
          fecha: new Date().toISOString(),
          nombre: String(data.get("nombre") || "").trim(),
          email: String(data.get("email") || "").trim(),
          recurso: form.dataset.recurso || "recurso-sin-nombre",
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
          if (download) {
            if (status) {
              status.textContent = result.demo
                ? "Modo prueba activo. Descarga iniciada."
                : alreadyRecorded
                  ? "Descarga iniciada."
                  : "Datos guardados. Descarga iniciada.";
            }
            startDownload(download, form.dataset.downloadName);
            revealSuccessTarget(form);
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
            return;
          }

          if (status) {
            status.textContent = result.demo
              ? "Modo prueba activo. Abriendo el recurso..."
              : "Datos guardados. Abriendo el recurso...";
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

  function initMasterclassPromo() {
    if (!document.querySelector("[data-lead-form]") || document.querySelector("[data-masterclass-promo]")) return;

    const footer = document.querySelector(".social-footer");
    if (!footer) return;

    const section = document.createElement("section");
    section.className = "masterclass-promo";
    section.dataset.masterclassPromo = "";
    section.hidden = true;
    section.innerHTML = `
      <div>
        <span class="masterclass-promo-badge">Siguiente paso</span>
        <h2>Tu guía ya se está descargando</h2>
        <p>Mientras la revisas: en la clase gratuita te enseño cómo convertir estos conceptos en un proceso de trading sencillo, objetivo y acompañado.</p>
      </div>
      <a class="masterclass-button" href="https://clase.tradinverso.com/" target="_blank" rel="noopener">Ver la clase gratuita <span aria-hidden="true">→</span></a>
    `;

    const leadSection = document.querySelector("[data-lead-form]")?.closest("section");
    if (leadSection) {
      leadSection.after(section);
    } else {
      footer.before(section);
    }

    if (typeof window.tradinversoDecorateLinks === "function") {
      window.tradinversoDecorateLinks(section);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    initLeadForms();
    initChecklist();
    initMasterclassPromo();
  });
})();
