#!/bin/sh
set -eu
APP=com.webos.app.home
for d in /usr/palm/applications/$APP/qml /tmp/checkpoint/$APP /mnt/lg/cmn_data/checkpoint/$APP; do
    if mount | grep -F " $d " >/dev/null; then umount "$d"; fi
done
pid=$(pidof "$APP" || true)
[ -z "$pid" ] || kill -9 $pid
sleep 2
luna-send -n 1 luna://com.webos.applicationManager/launch '{"id":"com.webos.app.home"}'
echo 'Montajes de prueba retirados. No se borraron archivos.'
