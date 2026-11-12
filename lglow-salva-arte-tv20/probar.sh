#!/bin/sh
set -eu
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv20
DEST=/usr/palm/applications/com.webos.app.fullhome/qml
[ "$(id -u)" = 0 ]
[ -f "$TEST/qml/.lglow-salva-prueba-tv20" ]
[ ! -e "$DEST/.lglow-salva-prueba-tv20" ] || { echo 'ERROR: la prueba ya esta activa'; exit 1; }
mount | grep -F " $DEST " >/dev/null || { echo 'ERROR: LGlow no esta montado; detenerse'; exit 1; }
mount --bind "$TEST/qml" "$DEST"
pid=$(pidof com.webos.app.fullhome || true)
[ -z "$pid" ] || kill -9 $pid
sleep 2
luna-send -n 1 luna://com.webos.applicationManager/launch '{"id":"com.webos.app.fullhome"}'
echo 'PRUEBA DEL PROTECTOR ACTIVA: espera 30 segundos sin usar el control.'
echo 'No se modifico el arranque. Reiniciar recupera el LGlow anterior.'
