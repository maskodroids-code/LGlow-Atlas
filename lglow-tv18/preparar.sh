#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
FULL=/var/lib/webosbrew/fullhomecustom
STAGE=$HERE/staging
APP=com.webos.app.home
[ "$(id -u)" = 0 ] || { echo 'ERROR: requiere root'; exit 1; }
[ -d /var/lib/webosbrew ] || { echo 'ERROR: falta Homebrew Channel'; exit 1; }
[ ! -e "$FULL" ] || { echo 'ERROR: fullhomecustom ya existe; detenerse para revisarlo'; exit 1; }
[ ! -e "$STAGE" ] || { echo 'ERROR: staging ya existe; detenerse para revisarlo'; exit 1; }
command -v patch >/dev/null || { echo 'ERROR: falta patch'; exit 1; }
if mount | grep -F " /usr/palm/applications/$APP/qml " >/dev/null; then
    echo 'ERROR: ya existe un montaje del home; detenerse para revisarlo'
    exit 1
fi
echo '==> comprobando originales de com.webos.app.home (50UP7500PSF, 03.53.45)'
(cd /usr/palm/applications/$APP && md5sum -c "$HERE/patches/originales.md5")
mkdir -p "$STAGE"
cp -a /usr/palm/applications/$APP/qml "$STAGE/qml"
for p in "$HERE"/patches/*.patch; do
    (cd "$STAGE" && patch -p1 -i "$p")
done
cp "$HERE"/qml/*.qml "$STAGE/qml/UserInterfaceLayer/Containers/Main/"
cp "$HERE/config.example.json" "$STAGE/config.json"
chmod 600 "$STAGE/config.json"
mkdir -p "$STAGE/tiles"
cp "$HERE/fondos/perla.jpg" "$STAGE/fondo.jpg"
cp "$HERE/fondos/perla.jpg" "$STAGE/fondo-perla.jpg"
cp "$HERE/fondos/aurora.jpg" "$STAGE/fondo-aurora.jpg"
mv "$STAGE" "$FULL"
echo 'PREPARADO TV18. No se activo ningun montaje ni script de arranque.'
echo 'No se modificaron compositor, precargas ni originales de LG.'
