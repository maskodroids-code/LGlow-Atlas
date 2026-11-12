#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
FILE=$TEST/qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml
[ "$(id -u)" = 0 ]
[ ! -e "$DEST/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: primero volver al LGlow estable'; exit 1; }
[ -f "$TEST/qml/.lglow-salva-prueba-tv18" ]
HASH=$(sha256sum "$FILE")
case "$HASH" in
    47c1e11bd56e3d2457c16b09304e544e7d4db4bdb750796dc7338949a022b61a*|5c1f06bc3ce099a0eb0b8cad21b3c47bc4e871b7705cde580769f06cae7754c5*) ;;
    *) echo 'ERROR: componente de prueba desconocido; no se cambia nada'; exit 1 ;;
esac
[ ! -e "$FILE.antes-arte" ] || { echo 'ERROR: ya existe respaldo de esta prueba'; exit 1; }
(cd "$HERE" && sha256sum -c archivos.sha256)
mkdir -p "$TEST/imagenes"
cp "$HERE"/imagenes/*.jpg "$TEST/imagenes/"
cp -p "$FILE" "$FILE.antes-arte"
cp "$HERE/LglowSalvapantallas.qml" "$FILE"
echo 'ARTE PREPARADO. No se cambio el LGlow activo ni el arranque.'
