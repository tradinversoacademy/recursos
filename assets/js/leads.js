(function () {
  const endpoint = window.TRADINVERSO_LEADS_ENDPOINT || "";
  const endpointReady = endpoint && !endpoint.includes("PON_AQUI");
  const profileKey = "tradinverso_lead_profile";

  function getLeadProfile() {
    try {
      const profile = JSON.parse(localStorage.getItem(profileKey) || "null");
      return profile && profile.email && profile.consentimiento === "si" ? profile : null;
    } catch (error) {
      return null;
    }
  }

  function saveLeadProfile(payload) {
    try {
      localStorage.setItem(profileKey, JSON.stringify({
        nombre: payload.nombre,
        email: payload.email,
        consentimiento: payload.consentimiento,
        registrado: payload.fecha
      }));
    } catch (error) {
      // El formulario sigue funcionando aunque el navegador bloquee el almacenamiento.
    }
  }

  function showRegisteredAccess(form, profile) {
    const redirect = form.dataset.redirect || "recurso.html";
    const isInformationForm = (form.dataset.recurso || "").includes("informacion");
    const access = document.createElement("div");
    access.className = "registered-access";

    const copy = document.createElement("div");
    const title = document.createElement("strong");
    const text = document.createElement("span");
    title.textContent = `Hola${profile.nombre ? `, ${profile.nombre}` : ""}`;
    text.textContent = isInformationForm
      ? "Ya tenemos tus datos. Puedes ver el contenido directamente."
      : "Ya estás registrado. Este recurso está listo para ti.";
    copy.append(title, text);

    const actions = document.createElement("div");
    actions.className = "registered-actions";

    const link = document.createElement("a");
    link.className = "primary-button";
    link.href = redirect;
    link.textContent = isInformationForm ? "Ver el vídeo" : "Abrir recurso";

    const reset = document.createElement("button");
    reset.className = "profile-reset";
    reset.type = "button";
    reset.textContent = "Cambiar datos";
    reset.addEventListener("click", () => {
      localStorage.removeItem(profileKey);
      window.location.reload();
    });

    actions.append(link, reset);
    access.append(copy, actions);
    form.replaceWith(access);
  }

  function getParams() {
    const params = new URLSearchParams(window.location.search);
    return {
      origen: params.get("origen") || params.get("utm_source") || "organico",
      campana: params.get("campana") || params.get("utm_campaign") || "sin-campana"
    };
  }

  function saveDemoLead(payload) {
    const key = "tradinverso_demo_leads";
    const previous = JSON.parse(localStorage.getItem(key) || "[]");
    previous.push(payload);
    localStorage.setItem(key, JSON.stringify(previous.slice(-50)));
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

    const request = fetch(buildLeadUrl(payload), {
      method: "GET",
      mode: "no-cors",
      cache: "no-store",
      keepalive: true
    });
    const timeout = new Promise((_, reject) => {
      window.setTimeout(() => reject(new Error("Tiempo de espera agotado")), 8000);
    });

    await Promise.race([request, timeout]);

    return { demo: false };
  }

  function initLeadForms() {
    const params = getParams();
    const profile = getLeadProfile();

    document.querySelectorAll("[data-lead-form]").forEach((form) => {
      if (profile) {
        showRegisteredAccess(form, profile);
        return;
      }

      const status = form.querySelector("[data-form-status]");
      const origenInput = form.querySelector('[name="origen"]');
      const campanaInput = form.querySelector('[name="campana"]');

      if (origenInput) origenInput.value = params.origen;
      if (campanaInput) campanaInput.value = params.campana;

      form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const submitButton = form.querySelector('button[type="submit"]');
        const data = new FormData(form);
        const redirect = form.dataset.redirect || "recurso.html";
        const payload = {
          fecha: new Date().toISOString(),
          nombre: String(data.get("nombre") || "").trim(),
          email: String(data.get("email") || "").trim(),
          recurso: form.dataset.recurso || "recurso-sin-nombre",
          origen: String(data.get("origen") || params.origen),
          campana: String(data.get("campana") || params.campana),
          consentimiento: data.get("consentimiento") ? "si" : "no",
          estado: "nuevo",
          notas: ""
        };

        if (!payload.nombre || !payload.email || payload.consentimiento !== "si") {
          if (status) status.textContent = "Revisa nombre, email y consentimiento.";
          return;
        }

        if (submitButton) submitButton.disabled = true;
        if (status) status.textContent = "Guardando tus datos...";

        try {
          const result = await sendLead(payload);
          saveLeadProfile(payload);
          if (status) {
            status.textContent = result.demo
              ? "Modo prueba activo. Abriendo el recurso..."
              : "Datos guardados. Abriendo el recurso...";
          }
          window.setTimeout(() => {
            window.location.href = redirect;
          }, 650);
        } catch (error) {
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

  document.addEventListener("DOMContentLoaded", () => {
    initLeadForms();
    initChecklist();
  });
})();
