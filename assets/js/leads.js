(function () {
  const endpoint = window.TRADINVERSO_LEADS_ENDPOINT || "";
  const endpointReady = endpoint && !endpoint.includes("PON_AQUI");

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

  function initLeadForms() {
    const params = getParams();

    document.querySelectorAll("[data-lead-form]").forEach((form) => {
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
        const opensInNewTab = /\.pdf(?:$|[?#])/i.test(redirect);
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
        const resourceWindow = opensInNewTab ? window.open("about:blank", "_blank") : null;

        try {
          const result = await sendLead(payload);
          if (redirect.startsWith("#")) {
            const target = document.querySelector(redirect);
            if (status) status.textContent = "Datos enviados. Puedes ver el vídeo.";
            if (submitButton) submitButton.disabled = false;
            if (target) {
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

  document.addEventListener("DOMContentLoaded", () => {
    initLeadForms();
    initChecklist();
  });
})();
