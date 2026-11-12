#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
BASE=/var/lib/webosbrew
TEST=$BASE/lglow-salva-prueba-tv20
[ "$(id -u)" = 0 ]
[ -d /usr/palm/applications/com.webos.app.fullhome/qml ]
[ ! -e "$TEST" ] || { echo 'ERROR: ya existe una prueba TV20'; exit 1; }
(cd "$BASE/fullhomecustom" && sha256sum -c "$HERE/base.sha256")
(cd "$HERE" && sha256sum -c archivos.sha256)
mkdir "$TEST"
cp -a "$BASE/fullhomecustom/qml" "$TEST/qml"
(cd "$TEST" && patch -p1 -i "$HERE/mainview.patch")
cp "$HERE/LglowSalvapantallas.qml" "$TEST/qml/UserInterfaceLayer/Containers/Main/"
cp -a "$HERE/imagenes" "$TEST/imagenes"
touch "$TEST/qml/.lglow-salva-prueba-tv20"
cp "$HERE/volver.sh" "$TEST/volver.sh"
echo 'PREPARADO TV20. Sin cambios al LGlow activo ni al arranque.'
