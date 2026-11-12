#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=/var/lib/webosbrew/fullhomecustom
TEST=/var/lib/webosbrew/lglow-chile-prueba-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
[ "$(id -u)" = 0 ]
[ ! -e "$TEST" ] || { echo 'ERROR: ya existe la prueba; detenerse'; exit 1; }
[ ! -e "$DEST/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: retirar la prueba anterior'; exit 1; }
(cd "$SRC" && sha256sum -c "$HERE/base.sha256")
(cd "$HERE" && sha256sum -c archivos.sha256)
mkdir "$TEST"
cp -a "$SRC/qml" "$TEST/qml"
for PATCH in "$HERE"/patches/*.patch; do (cd "$TEST" && patch -p1 -i "$PATCH"); done
cp "$HERE/LglowChile.qml" "$HERE/Indicadores.js" "$TEST/qml/UserInterfaceLayer/Containers/Main/"
touch "$TEST/qml/.lglow-chile-prueba-tv18"
echo 'TARJETAS PREPARADAS. No se activo ningun montaje ni se cambio el arranque.'
