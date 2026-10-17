# Recursos TRADINVERSO

Biblioteca estática de recursos gratuitos de TRADINVERSO.

## Funcionamiento

- El vídeo o la herramienta principal se puede consultar sin registro.
- El formulario guarda el lead en Google Sheets.
- Tras enviar el formulario se abre la guía PDF correspondiente.
- Todos los recursos comparten la identidad visual azul y blanca de TRADINVERSO.
- La web se sirve en `https://recursos.tradinverso.com/` y cada recurso vive en su carpeta
  de la raíz: `https://recursos.tradinverso.com/<slug>/`. La carpeta `recursos/` solo guarda
  redirecciones de las URL antiguas (`/recursos/<slug>/`); no se editan ni se crean recursos ahí.

## Recursos activos

### IFVG

- `ifvg/index.html`: explicación, formulario, vídeo y descarga.
- `ifvg/recurso.html`: desarrollo completo del concepto.
- `ifvg/guia-ifvg.pdf`: guía descargable.
- `protocolo-mental-trader/`: protocolo de control mental y emocional.
- `protocolo-mental-trader/protocolo-mental-trader.pdf`: PDF descargable.
- `rango-asiatico/`: vídeo y guía visual sobre la manipulación del rango asiático.

### Método C3

- `metodo-c3/index.html`: vídeo completo del sistema formativo de TRADINVERSO.
- Este recurso no incluye formulario ni PDF.

### DATA TRADINVERSO

- `data-tradinverso/index.html`: vídeo de la aplicación, resumen y formulario.
- `data-tradinverso/recurso.html`: explicación completa del sistema DATA.
- `data-tradinverso/guia-data-tradinverso.pdf`: guía descargable.

### AMD + IFVG

- `amd-ifvg/index.html`: vídeo Loom, resumen y formulario.
- `amd-ifvg/recurso.html`: explicación completa de la operativa.
- `amd-ifvg/guia-amd-ifvg.pdf`: guía descargable.

### ORB Nasdaq

- `orb-nasdaq/index.html`: vídeo de YouTube, resumen y formulario.
- `orb-nasdaq/recurso.html`: explicación completa de la operativa.
- `orb-nasdaq/guia-orb-nasdaq.pdf`: guía descargable.

### Checklist antes de entrar

- `checklist-entrada-mercado/index.html`: acceso directo y formulario.
- `checklist-entrada-mercado/recurso.html`: checklist interactivo.
- `checklist-entrada-mercado/checklist.pdf`: versión imprimible.

## Archivos compartidos

- `index.html`: biblioteca general.
- `assets/css/base.css`: estilos.
- `assets/js/config.js`: dirección del registro en Google Sheets.
- `assets/js/leads.js`: envío del lead y apertura del PDF.
- `google-apps-script/Code.gs`: receptor de los datos.
