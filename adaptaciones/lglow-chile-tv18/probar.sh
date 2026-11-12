#!/bin/sh
set -eu
TEST=/var/lib/webosbrew/lglow-chile-prueba-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
[ "$(id -u)" = 0 ]
[ -f "$TEST/qml/.lglow-chile-prueba-tv18" ]
[ ! -e "$DEST/.lglow-chile-prueba-tv18" ] || { echo 'ERROR: prueba ya activa'; exit 1; }
mount | grep -F " $DEST " >/dev/null
mount --bind "$TEST/qml" "$DEST"
pid=$(pidof com.webos.app.home || true)
[ -z "$pid" ] || kill -9 $pid
sleep 2
luna-send -n 1 luna://com.webos.applicationManager/launch '{"id":"com.webos.app.home"}'
echo 'PRUEBA ACTIVA. Bajar hasta el final de las apps y pulsar abajo otra vez.'
echo 'Reiniciar la TV recupera el inicio anterior. No se modifico el compositor.'
