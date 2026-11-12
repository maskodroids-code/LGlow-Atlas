#!/bin/sh
set -eu
BASE=/var/lib/webosbrew
APP=com.webos.app.fullhome
ORIG=/usr/palm/applications/$APP/qml
MOD=$BASE/fullhomecustom/qml
EMPTY=/tmp/lglow-port-empty
[ "$(id -u)" = 0 ]
[ -f "$MOD/main.qml" ]
if mount | grep -F " $ORIG " >/dev/null; then
    echo 'ERROR: el home ya tiene un montaje; detenerse para revisarlo'
    exit 1
fi
mkdir -p "$EMPTY"
mount --bind "$MOD" "$ORIG"
for d in /tmp/checkpoint/$APP /mnt/lg/cmn_data/checkpoint/$APP; do
    [ ! -d "$d" ] || mount --bind "$EMPTY" "$d"
done
pid=$(pidof "$APP" || true)
[ -z "$pid" ] || kill -9 $pid
sleep 2
luna-send -n 1 luna://com.webos.applicationManager/launch '{"id":"com.webos.app.fullhome"}'
echo 'PRUEBA TEMPORAL ACTIVA. Reiniciar la TV recupera los montajes originales.'
