# Recursos DavidRoser.fx / TRADINVERSO

Proyecto estático para crear landings y recursos visuales de captación.

## Estructura

- `recursos/checklist-entrada-mercado/index.html`: landing con formulario.
- `recursos/checklist-entrada-mercado/recurso.html`: recurso que se abre tras dejar los datos.
- `assets/css/base.css`: estilos compartidos.
- `assets/js/config.js`: URL del formulario conectado a Google Sheets.
- `assets/js/leads.js`: envío del lead y apertura del recurso.
- `google-apps-script/Code.gs`: script para pegar en Google Apps Script.

## Activar Google Sheets

1. Crea una Google Sheet con una pestaña llamada `Leads`.
2. Abre Extensiones > Apps Script.
3. Pega el contenido de `google-apps-script/Code.gs`.
4. Despliega como aplicación web.
5. Copia la URL del despliegue.
6. Pégala en `assets/js/config.js`, sustituyendo `PON_AQUI_TU_URL_DE_APPS_SCRIPT`.

Columnas usadas: fecha, nombre, email, recurso, origen, campaña, consentimiento, estado, notas.

Sin URL configurada, el formulario funciona en modo prueba: guarda una copia local en el navegador y abre el recurso.
