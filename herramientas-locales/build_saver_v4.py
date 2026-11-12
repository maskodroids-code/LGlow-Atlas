from pathlib import Path
import hashlib
import io
import tarfile
import time

root = Path(__file__).resolve().parent.parent
old = (root / 'outputs/LglowSalvapantallas-v3.qml').read_bytes()
text = old.decode('utf-8').replace('import QtQuick 2.6\n', 'import QtQuick 2.6\nimport WebOSServices 1.0\n', 1)
text = text.replace('// Protector local del home. No cambia el protector ni el compositor de LG.', '// Protector local: coordina la solicitud de LG solo mientras esta visible.')
insert = '''    // La suscripcion desaparece al cerrar el protector o salir del home.
    // No modifica ajustes persistentes ni simula pulsaciones del control.
    Loader {
        id: powerGuard
        active: saver.showing && saver.allowed
        sourceComponent: Component {
            Service {
                appId: rootWindow.appId
                Component.onCompleted: call("luna://com.webos.service.tvpower/",
                    "power/registerScreenSaverRequest",
                    JSON.stringify({clientName: "lglow.home.saver", subscribe: true}))
                Component.onDestruction: cancel()
                onCallSuccess: {
                    var r = response;
                    if (typeof r === "string") {
                        try { r = JSON.parse(r); } catch (e) { return; }
                    }
                    if (!r || r.timestamp === undefined) return;
                    var reply = powerReply.createObject(saver);
                    reply.call("luna://com.webos.service.tvpower/",
                        "power/responseScreenSaverRequest", JSON.stringify({
                            clientName: "lglow.home.saver",
                            ack: !(saver.showing && saver.allowed),
                            timestamp: r.timestamp
                        }));
                }
                onCallFailure: console.log("[lglow-salva] LG no acepto la suscripcion")
                onError: console.log("[lglow-salva] error de suscripcion a LG")
            }
        }
    }

    Component {
        id: powerReply
        Service {
            appId: rootWindow.appId
            onCallSuccess: destroy()
            onCallFailure: { console.log("[lglow-salva] LG rechazo la respuesta"); destroy(); }
            onError: { console.log("[lglow-salva] error al responder a LG"); destroy(); }
        }
    }

'''
text = text.replace('    function updateClock() {', insert + '    function updateClock() {', 1)
new = text.encode('utf-8')
(root / 'outputs/LglowSalvapantallas-v4.qml').write_bytes(new)
script = '''#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
[ "$(id -u)" = 0 ]
[ ! -e "$DEST/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: primero volver al LGlow anterior'; exit 1; }
[ -f "$TEST/qml/.lglow-salva-prueba-tv18" ]
(cd "$TEST" && sha256sum -c "$HERE/base.sha256")
FILE=$TEST/qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml
[ ! -e "$FILE.antes-v4" ] || { echo 'ERROR: ya existe respaldo v4'; exit 1; }
cp -p "$FILE" "$FILE.antes-v4"
cp "$HERE/LglowSalvapantallas.qml" "$FILE"
echo 'V4 PREPARADA. El LGlow activo y su arranque siguen intactos.'
'''
entries = {'LglowSalvapantallas.qml': new, 'actualizar.sh': script.encode(),
           'base.sha256': (hashlib.sha256(old).hexdigest() + '  qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml\n').encode()}
archive = root / 'outputs/lglow-protector-v4-tv18.tar.gz'
with tarfile.open(archive, 'w:gz') as tf:
    for name, data in entries.items():
        assert b'\r' not in data
        info = tarfile.TarInfo('lglow-salva-v4-tv18/' + name)
        info.size, info.mode, info.mtime = len(data), 0o644, int(time.time())
        tf.addfile(info, io.BytesIO(data))
print(hashlib.sha256(archive.read_bytes()).hexdigest(), archive)
