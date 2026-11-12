#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
[ "$(id -u)" = 0 ]
[ -f "$TEST/qml/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: no existe la prueba preparada'; exit 1; }
[ ! -e "$DEST/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: primero volver al LGlow anterior'; exit 1; }
(cd "$TEST" && md5sum -c "$HERE/base.md5")
FILE=$TEST/qml/UserInterfaceLayer/Containers/MainView.qml
[ ! -e "$FILE.antes-loader" ] || { echo 'ERROR: ya existe una actualizacion; revisar'; exit 1; }
cp -p "$FILE" "$FILE.antes-loader"
(cd "$TEST" && patch -p1 -i "$HERE/loader.patch")
cp "$HERE/LglowSalvapantallas.qml" "$TEST/qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml"
echo 'CORRECCION PREPARADA. El LGlow activo no se ha modificado.'
