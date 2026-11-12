#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=/var/lib/webosbrew/fullhomecustom/qml
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv18
[ "$(id -u)" = 0 ] || { echo 'ERROR: requiere root'; exit 1; }
[ ! -e "$TEST" ] || { echo 'ERROR: ya existe una prueba; detenerse para revisarla'; exit 1; }
command -v patch >/dev/null
echo '==> verificando la version de MainView de LGlow TV18'
(cd /var/lib/webosbrew/fullhomecustom && md5sum -c "$HERE/base.md5")
mkdir -p "$TEST"
cp -a "$SRC" "$TEST/qml"
(cd "$TEST" && patch -p1 -i "$HERE/mainview.patch")
cp "$HERE/LglowSalvapantallas.qml" "$TEST/qml/UserInterfaceLayer/Containers/Main/"
touch "$TEST/qml/.lglow-salva-prueba-tv18"
cp "$HERE/volver.sh" "$TEST/volver.sh"
echo 'PREPARADO: copia de prueba con espera de 30 segundos; aun no esta activa.'
