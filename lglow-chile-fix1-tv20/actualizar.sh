#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST=/var/lib/webosbrew/lglow-chile-prueba-tv20
DEST=/usr/palm/applications/com.webos.app.fullhome/qml
FILE=$TEST/qml/UserInterfaceLayer/Containers/Main/Indicadores.js
[ "$(id -u)" = 0 ]
[ ! -e "$DEST/.lglow-chile-prueba-tv20" ] || { echo 'ERROR: retirar primero la prueba con volver.sh'; exit 1; }
[ -f "$TEST/qml/.lglow-chile-prueba-tv20" ]
[ ! -e "$FILE.antes-correccion1" ] || { echo 'ERROR: ya existe respaldo de esta correccion'; exit 1; }
echo '93012fde4bc3260ace0e86c333e1cf529264c71855678c1af1c54b92f020c189  '"$FILE" | sha256sum -c -
(cd "$HERE" && sha256sum -c archivos.sha256)
cp -p "$FILE" "$FILE.antes-correccion1"
cp "$HERE/Indicadores.js" "$FILE"
echo 'CORRECCION PREPARADA. Sin cambios al arranque ni al LGlow estable.'
