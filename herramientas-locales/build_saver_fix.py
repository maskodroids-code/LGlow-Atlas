from pathlib import Path
import difflib
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
import time

root = Path(__file__).resolve().parent.parent
base = root / 'work/tv18/mod/qml/UserInterfaceLayer/Containers/MainView.qml'
work = Path(tempfile.mkdtemp(prefix='saver-loader-', dir=root / 'work'))
rel = 'qml/UserInterfaceLayer/Containers/MainView.qml'
(work / rel).parent.mkdir(parents=True)
(work / rel).write_bytes(base.read_bytes())
with tarfile.open(root / 'outputs/lglow-protector-prueba-tv18.tar.gz') as tf:
    initial_patch = tf.extractfile('lglow-salva-tv18/mainview.patch').read()
patch_file = work / 'initial.patch'
patch_file.write_bytes(initial_patch)
git = 'C:/Users/chris/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
subprocess.run([git, '-c', 'core.autocrlf=false', 'apply', str(patch_file)], cwd=work, check=True, capture_output=True)
old = (work / rel).read_text(encoding='utf-8')
start = old.index('    // [lglow-salva-tv18]')
assert old[start:].count('    LglowSalvapantallas {') == 1
end = old.rfind('}')
safe = '''    // [lglow-salva-tv18] Carga aislada: un error del protector no invalida el home.
    Loader {
        id: lglowSalvaLoader
        anchors.fill: parent
        z: 10000
        source: "Main/LglowSalvapantallas.qml"
        onLoaded: {
            item.windowController = rootWindow;
            item.timeoutMs = 30000; // prueba, despues se cambiara a cinco minutos
            item.recommendations = Qt.binding(function() { return paraTi.picks; });
            item.fallbackImage = Qt.binding(function() { return lglowTema.fondo; });
            item.allowed = Qt.binding(function() {
                return root.visible && rootWindow.active && systemProperties.isAppForeground
                    && rootWindow.windowState === "maximized" && uiController.homeShown
                    && !uiController.isEditMode && !uiController.isRecentMode
                    && !lglowPanel.open && !lglowMenu.open;
            });
        }
        onStatusChanged: {
            if (status === Loader.Error)
                console.log("[lglow-salva] No se pudo cargar el protector; home conservado");
        }
    }

    Connections {
        target: lglowSalvaLoader.item
        ignoreUnknownSignals: true
        onCerrado: {
            if (systemProperties.isAppForeground && rootWindow.active)
                appListArea.forceActiveFocus();
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 16
        z: 10001
        visible: lglowSalvaLoader.status === Loader.Error
        text: "No se pudo cargar el protector. LGlow sigue disponible."
        color: "#FF6C80"
        font.pixelSize: 24
    }
'''
new = old[:start] + safe + old[end:]
assert new.count('id: lglowSalvaLoader') == 1
assert '    LglowSalvapantallas {' not in new
patch = ''.join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True), fromfile='a/' + rel, tofile='b/' + rel))
patch_file = work / 'loader.patch'
patch_file.write_text(patch, encoding='utf-8', newline='\n')
subprocess.run([git, '-c', 'core.autocrlf=false', 'apply', '--check', str(patch_file)], cwd=work, check=True, capture_output=True)
subprocess.run([git, '-c', 'core.autocrlf=false', 'apply', str(patch_file)], cwd=work, check=True, capture_output=True)
assert (work / rel).read_text(encoding='utf-8') == new
digest = hashlib.md5(old.encode('utf-8')).hexdigest()
script = '''#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
[ "$(id -u)" = 0 ]
[ -f "$TEST/qml/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: no existe la prueba preparada'; exit 1; }
[ ! -e "$DEST/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: primero volver al LGlow anterior'; exit 1; }
(cd "$TEST" && md5sum -c "$HERE/base.md5")
FILE=$TEST/qml/UserInterfaceLayer/Containers/MainView.qml
[ ! -e "$FILE.antes-loader" ] || { echo 'ERROR: ya existe una actualizacion; revisar'; exit 1; }
cp -p "$FILE" "$FILE.antes-loader"
(cd "$TEST" && patch -p1 -i "$HERE/loader.patch")
cp "$HERE/LglowSalvapantallas.qml" "$TEST/qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml"
echo 'CORRECCION PREPARADA. El LGlow activo no se ha modificado.'
'''
component = (root / 'outputs/LglowSalvapantallas-v3.qml').read_bytes()
assert b'onFinished:' not in component
entries = {'loader.patch': patch.encode('utf-8'), 'base.md5': (digest + '  ' + rel + '\n').encode('ascii'), 'LglowSalvapantallas.qml':component, 'actualizar.sh':script.encode('utf-8')}
archive = root / 'outputs/lglow-protector-correccion-v3-tv18.tar.gz'
with tarfile.open(archive, 'w:gz') as tf:
    for name, data in entries.items():
        assert b'\r' not in data
        info = tarfile.TarInfo('lglow-salva-fix-tv18/' + name)
        info.size = len(data)
        info.mode = 0o644
        info.mtime = int(time.time())
        tf.addfile(info, io.BytesIO(data))
print(json.dumps({'archive':str(archive), 'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(), 'loader_patch_roundtrip':'PASS', 'qml_runtime':'NOT TESTED'}))
