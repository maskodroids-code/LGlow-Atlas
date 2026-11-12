#!/bin/sh
set -eu
DEST=/usr/palm/applications/com.webos.app.home/qml
[ "$(id -u)" = 0 ]
if [ ! -e "$DEST/.lglow-salva-prueba-tv18" ]; then
    echo 'La prueba no esta montada. No se cambia nada.'
    exit 0
fi
umount "$DEST"
pid=$(pidof com.webos.app.home || true)
[ -z "$pid" ] || kill -9 $pid
sleep 2
luna-send -n 1 luna://com.webos.applicationManager/launch '{"id":"com.webos.app.home"}'
echo 'Restaurado el montaje anterior de LGlow; configuracion y tiles intactos.'
