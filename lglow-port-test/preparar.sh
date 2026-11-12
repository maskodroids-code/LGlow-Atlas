#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
FULL=/var/lib/webosbrew/fullhomecustom
STAGE=$HERE/staging
[ "$(id -u)" = 0 ] || { echo 'ERROR: requiere root'; exit 1; }
[ ! -e "$FULL" ] || { echo 'ERROR: fullhomecustom ya existe; detenerse para revisarlo'; exit 1; }
[ ! -e "$STAGE" ] || { echo 'ERROR: staging ya existe; detenerse para revisarlo'; exit 1; }
command -v patch >/dev/null
for part in fullhome home; do
    echo "==> comprobando originales: $part"
    (cd "/usr/palm/applications/com.webos.app.$part" && md5sum -c "$HERE/patches/$part/originales.md5")
done
mkdir -p "$STAGE"
cp -a /usr/palm/applications/com.webos.app.fullhome/qml "$STAGE/qml"
for p in "$HERE"/patches/fullhome/*.patch; do
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
echo 'PREPARADO. No se activo ningun montaje ni script de arranque.'
echo 'No se modificaron compositor, precargas ni particiones de LG.'
