(function () {
  "use strict";

  // Pase de biblioteca: quien se registra en la portada entra a todos los
  // recursos sin volver a rellenar nada. Quien llega a un recurso suelto desde
  // un Reel se registra solo en ese recurso, como hasta ahora.
  var PASS_KEY = "tradinverso_library_pass_v1";
  var PROFILE_KEY = "tradinverso_lead_profile_v1";
  var DURATION = 90 * 24 * 60 * 60 * 1000;

  function read(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || "null");
    } catch (error) {
      return null;
    }
  }

  function write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      // Con el almacenamiento bloqueado el sitio sigue siendo usable:
      // simplemente se pedirán los datos otra vez.
      return false;
    }
  }

  function valid(entry) {
    return Boolean(entry && entry.nombre && entry.email && Number(entry.expiresAt) > Date.now());
  }

  function getPass() {
    var pass = read(PASS_KEY);
    if (!valid(pass)) {
      try {
        localStorage.removeItem(PASS_KEY);
      } catch (error) {
        // Nada que limpiar.
      }
      return null;
    }
    return pass;
  }

  // Perfil de alguien que ya se registró en algún recurso suelto.
  function getKnownProfile() {
    var profile = read(PROFILE_KEY);
    return valid(profile) ? profile : null;
  }

  function grantPass(profile) {
    if (!profile || !profile.nombre || !profile.email) return null;

    var pass = {
      nombre: String(profile.nombre).trim(),
      email: String(profile.email).trim().toLowerCase(),
      expiresAt: Date.now() + DURATION
    };
    write(PASS_KEY, pass);
    return pass;
  }

  function revokePass() {
    try {
      localStorage.removeItem(PASS_KEY);
    } catch (error) {
      // Nada que limpiar.
    }
  }

  window.TradinversoAccess = {
    getPass: getPass,
    hasPass: function () {
      return Boolean(getPass());
    },
    getKnownProfile: getKnownProfile,
    grantPass: grantPass,
    revokePass: revokePass
  };
})();
