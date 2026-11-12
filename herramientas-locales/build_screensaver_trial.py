from pathlib import Path
import difflib
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile

root = Path(__file__).resolve().parent.parent
base = root / 'work/tv18/mod/qml/UserInterfaceLayer/Containers/MainView.qml'
component = root / 'outputs/LglowSalvapantallas.qml'
text = base.read_text(encoding='utf-8')
assert 'LglowSalvapantallas' not in text
insert = '''
    // [lglow-salva-tv18] Prueba local del home; no toca el compositor.
    LglowSalvapantallas {
        id: lglowSalva
        anchors.fill: parent
        windowController: rootWindow
        timeoutMs: 30000 // PRUEBA: 30 segundos. Definitivo: 300000.
        allowed: root.visible && rootWindow.active && systemProperties.isAppForeground
                 && rootWindow.windowState === "maximized" && uiController.homeShown
                 && !uiController.isEditMode && !uiController.isRecentMode
                 && !lglowPanel.open && !lglowMenu.open
        recommendations: paraTi.picks
        fallbackImage: lglowTema.fondo
        onCerrado: {
            if (systemProperties.isAppForeground && rootWindow.active)
                appListArea.forceActiveFocus();
        }
    }
'''
# Confirm the menu visibility property before generating a binding.
menu = Path('C:/lglow-main/tv/qml/fullhome/LglowMenu.qml').read_text(encoding='utf-8')
if 'property bool open:' not in menu:
    raise RuntimeError('Revisar la interfaz de LglowMenu antes de generar el paquete')
pos = text.rfind('}')
assert pos >= 0 and not text[pos+1:].strip()
modified = text[:pos] + insert + text[pos:]
name = 'qml/UserInterfaceLayer/Containers/MainView.qml'
patch = ''.join(difflib.unified_diff(text.splitlines(keepends=True), modified.splitlines(keepends=True), fromfile='a/' + name, tofile='b/' + name))
digest = hashlib.md5(text.encode('utf-8')).hexdigest()
work = Path(tempfile.mkdtemp(prefix='saver-check-', dir=root / 'work'))
(work / name).parent.mkdir(parents=True)
(work / name).write_text(text, encoding='utf-8', newline='\n')
patchfile = work / 'mainview.patch'
patchfile.write_text(patch, encoding='utf-8', newline='\n')
git = 'C:/Users/chris/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
subprocess.run([git, '-c', 'core.autocrlf=false', 'apply', '--check', str(patchfile)], cwd=work, check=True, capture_output=True)
subprocess.run([git, '-c', 'core.autocrlf=false', 'apply', str(patchfile)], cwd=work, check=True, capture_output=True)
assert (work / name).read_text(encoding='utf-8') == modified

prepare = '''#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=/var/lib/webosbrew/fullhomecustom/qml
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv18
[ "$(id -u)" = 0 ] || { echo 'ERROR: requiere root'; exit 1; }
[ ! -e "$TEST" ] || { echo 'ERROR: ya existe una prueba; detenerse para revisarla'; exit 1; }
command -v patch >/dev/null
echo '==> verificando la version de MainView de LGlow TV18'
(cd /var/lib/webosbrew/fullhomecustom && md5sum -c "$HERE/base.md5")
mkdir -p "$TEST"
cp -a "$SRC" "$TEST/qml"
(cd "$TEST" && patch -p1 -i "$HERE/mainview.patch")
cp "$HERE/LglowSalvapantallas.qml" "$TEST/qml/UserInterfaceLayer/Containers/Main/"
touch "$TEST/qml/.lglow-salva-prueba-tv18"
cp "$HERE/volver.sh" "$TEST/volver.sh"
echo 'PREPARADO: copia de prueba con espera de 30 segundos; aun no esta activa.'
'''
activate = '''#!/bin/sh
set -eu
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
[ "$(id -u)" = 0 ]
[ -f "$TEST/qml/.lglow-salva-prueba-tv18" ]
[ ! -e "$DEST/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: la prueba ya esta activa'; exit 1; }
mount | grep -F " $DEST " >/dev/null || { echo 'ERROR: LGlow no esta montado; detenerse'; exit 1; }
mount --bind "$TEST/qml" "$DEST"
pid=$(pidof com.webos.app.home || true)
[ -z "$pid" ] || kill -9 $pid
sleep 2
luna-send -n 1 luna://com.webos.applicationManager/launch '{"id":"com.webos.app.home"}'
echo 'PRUEBA DEL PROTECTOR ACTIVA: espera 30 segundos sin usar el control.'
echo 'No se modifico el arranque. Reiniciar recupera el LGlow anterior.'
'''
rollback = '''#!/bin/sh
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
'''
entries = {
    'LglowSalvapantallas.qml': component.read_bytes(),
    'mainview.patch': patch.encode('utf-8'),
    'base.md5': (digest + '  ' + name + '\n').encode('ascii'),
    'preparar.sh': prepare.encode('utf-8'),
    'probar.sh': activate.encode('utf-8'),
    'volver.sh': rollback.encode('utf-8'),
    'LEEME.txt': '''Prueba experimental del protector de LGlow para la segunda TV, 50UP7500PSF 03.53.45.
Solo se activa dentro del home visible, activo, maximizado y fuera de menus/edicion/recientes.
Espera de prueba: 30 segundos. Objetivo final: 5 minutos tras validar navegacion e inactividad.
Reutiliza imagenes de las recomendaciones cargadas por ParaTi; sin clave ni peticiones TMDB nuevas.
Sin imagen disponible usa el fondo del home. Reloj/fecha y su posicion se actualizan durante el protector.
preparar.sh copia el QML personalizado actual a una carpeta de prueba y valida MainView antes de parchear.
probar.sh superpone temporalmente esa carpeta sobre el montaje de LGlow existente y relanza el home.
volver.sh retira solo el montaje marcado de esta prueba y relanza el LGlow anterior.
Reiniciar la TV restaura el LGlow anterior: no se instalan scripts de arranque nuevos.
Los datos de prueba preparados en /var/lib permanecen guardados, pero no se activan solos.
Sin cambios al compositor, particiones originales, configuracion, tiles, bloqueo de actualizaciones ni otras apps.
No probado aun en ejecucion QML. No sustituye al protector del sistema ni promete controlar teclas reservadas por LG.
No usar en la primera TV: el archivo base y app de destino son distintos.
'''.encode('utf-8')
}
archive = root / 'outputs/lglow-protector-prueba-tv18.tar.gz'
with tarfile.open(archive, 'w:gz') as tf:
    for name, data in entries.items():
        assert b'\r' not in data
        info = tarfile.TarInfo('lglow-salva-tv18/' + name)
        info.size = len(data)
        info.mode = 0o644
        tf.addfile(info, io.BytesIO(data))
print(json.dumps({'archive':str(archive), 'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(), 'base_md5':digest, 'patch_roundtrip':'PASS', 'qml_runtime':'NOT TESTED'}))
