#!/bin/sh
set -eu
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv20
DEST=/usr/palm/applications/com.webos.app.fullhome/qml
CTRL=/usr/lib/qml/WebOSCompositor/controllers/StarfishViewStateController.qml
[ "$(id -u)" = 0 ]
[ -f "$TEST/StarfishViewStateController.qml" ]
[ ! -e "$DEST/.lglow-salva-prueba-tv20" ]
echo 'aab926cb280e471af2977b6da42e92c1cc90c94b6e27bd5aa284215630bca3ed  '"$CTRL" | sha256sum -c -
mount | grep -F " $DEST " >/dev/null
if mount | grep -F " $CTRL " >/dev/null; then
    echo 'ERROR: el controlador ya tiene un montaje'; exit 1
fi
mount --bind "$TEST/qml" "$DEST"
if ! mount --bind "$TEST/StarfishViewStateController.qml" "$CTRL"; then
    umount "$DEST"; exit 1
fi
echo 'Reiniciando interfaz grafica. Si falla, ejecutar reboot por SSH.'
initctl restart surface-manager
echo 'PRUEBA IDLE ACTIVA. Pulsar Home al volver la imagen. Reiniciar TV revierte ambos montajes.'
