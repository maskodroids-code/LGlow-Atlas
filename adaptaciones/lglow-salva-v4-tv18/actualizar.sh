#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
[ "$(id -u)" = 0 ]
[ ! -e "$DEST/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: primero volver al LGlow anterior'; exit 1; }
[ -f "$TEST/qml/.lglow-salva-prueba-tv18" ]
(cd "$TEST" && sha256sum -c "$HERE/base.sha256")
FILE=$TEST/qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml
[ ! -e "$FILE.antes-v4" ] || { echo 'ERROR: ya existe respaldo v4'; exit 1; }
cp -p "$FILE" "$FILE.antes-v4"
cp "$HERE/LglowSalvapantallas.qml" "$FILE"
echo 'V4 PREPARADA. El LGlow activo y su arranque siguen intactos.'
