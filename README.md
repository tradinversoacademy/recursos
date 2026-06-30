# Recursos DavidRoser.fx / TRADINVERSO

Proyecto estático para crear landings y recursos visuales de captación.

## Recursos activos

- `recursos/checklist-entrada-mercado/index.html`: landing con formulario del checklist.
- `recursos/checklist-entrada-mercado/recurso.html`: checklist interactivo.
- `recursos/checklist-entrada-mercado/checklist.pdf`: PDF descargable.
- `recursos/orb-nasdaq/index.html`: landing con formulario del recurso ORB.
- `recursos/orb-nasdaq/recurso.html`: resumen ORB con vídeo de YouTube incrustado.

## Estructura

- `index.html`: biblioteca general de recursos.
- `assets/css/base.css`: estilos compartidos.
- `assets/js/config.js`: URL del formulario conectado a Google Sheets.
- `assets/js/leads.js`: envío del lead y apertura del recurso.
- `google-apps-script/Code.gs`: script para pegar en Google Apps Script.

## Google Sheets

Columnas usadas: fecha, nombre, email, recurso, origen, campaña, consentimiento, estado, notas.

Cada formulario envía el nombre del recurso en la columna `recurso`, por ejemplo `checklist-entrada-mercado` u `orb-nasdaq`.
