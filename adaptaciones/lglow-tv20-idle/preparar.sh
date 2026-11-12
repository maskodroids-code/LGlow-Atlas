#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv20
DEST=/usr/palm/applications/com.webos.app.fullhome/qml
CTRL=/usr/lib/qml/WebOSCompositor/controllers/StarfishViewStateController.qml
PART=qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml
[ "$(id -u)" = 0 ]
[ ! -e "$DEST/.lglow-salva-prueba-tv20" ] || { echo 'ERROR: retirar primero la prueba del home'; exit 1; }
[ ! -e "$TEST/$PART.antes-idle" ] || { echo 'ERROR: ya existe esta correccion'; exit 1; }
echo 'aab926cb280e471af2977b6da42e92c1cc90c94b6e27bd5aa284215630bca3ed  '"$CTRL" | sha256sum -c -
echo 'e32be271f18d0e8d97e3898b6226021789d5908e3fc345a813c24b0276b7d3f5  '"$TEST/$PART" | sha256sum -c -
(cd "$HERE" && sha256sum -c archivos.sha256)
cp -p "$TEST/$PART" "$TEST/$PART.antes-idle"
cp "$HERE/LglowSalvapantallas.qml" "$TEST/$PART"
cp "$HERE/StarfishViewStateController.qml" "$TEST/StarfishViewStateController.qml"
echo 'CORRECCION PREPARADA. Sin montajes nuevos ni reinicio del compositor.'
