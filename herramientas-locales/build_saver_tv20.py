from pathlib import Path
import difflib, hashlib, io, subprocess, tarfile, tempfile, time

root = Path(__file__).resolve().parent.parent
rel = 'qml/UserInterfaceLayer/Containers/MainView.qml'
base = (root / 'work/port/fullhome' / rel).read_bytes()
assert hashlib.sha256(base).hexdigest() == 'c86d24c527c05b0218c90eb7629ef4e0d8d61a93fe6d4805043b2e999c92a8f1'
old = base.decode()
loader_source = next((root / 'work').glob('saver-loader-*/qml/UserInterfaceLayer/Containers/MainView.qml')).read_text(encoding='utf-8')
start = loader_source.index('    // [lglow-salva-tv18]')
loader = loader_source[start:loader_source.rfind('}')]
loader = loader.replace('tv18', 'tv20').replace('rootWindow.windowState === "maximized" && ', '').replace(' && !uiController.isRecentMode', '')
assert 'windowState' not in loader and 'isRecentMode' not in loader
new = old[:old.rfind('}')] + loader + '}\n'
patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/'+rel, tofile='b/'+rel))
check = Path(tempfile.mkdtemp(prefix='saver-tv20-', dir=root/'work'))
(check/rel).parent.mkdir(parents=True)
(check/rel).write_bytes(base)
(check/'mainview.patch').write_text(patch, encoding='utf-8', newline='\n')
git = 'C:/Users/chris/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
subprocess.run([git, '-c', 'core.autocrlf=false', 'apply', str(check/'mainview.patch')], cwd=check, check=True, capture_output=True)
assert (check/rel).read_text(encoding='utf-8') == new
entries = {}
with tarfile.open(root/'outputs/lglow-protector-arte-tv18.tar.gz') as tf:
    for info in tf.getmembers():
        short = info.name.split('/',1)[1]
        if short.startswith('imagenes/') or short == 'LglowSalvapantallas.qml':
            data = tf.extractfile(info).read()
            if short.endswith('.qml'): data = data.replace(b'lglow-salva-prueba-tv18', b'lglow-salva-prueba-tv20')
            entries[short] = data
entries['mainview.patch'] = patch.encode()
entries['base.sha256'] = (hashlib.sha256(base).hexdigest()+'  '+rel+'\n').encode()
entries['preparar.sh'] = b'''#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
BASE=/var/lib/webosbrew
TEST=$BASE/lglow-salva-prueba-tv20
[ "$(id -u)" = 0 ]
[ -d /usr/palm/applications/com.webos.app.fullhome/qml ]
[ ! -e "$TEST" ] || { echo 'ERROR: ya existe una prueba TV20'; exit 1; }
(cd "$BASE/fullhomecustom" && sha256sum -c "$HERE/base.sha256")
(cd "$HERE" && sha256sum -c archivos.sha256)
mkdir "$TEST"
cp -a "$BASE/fullhomecustom/qml" "$TEST/qml"
(cd "$TEST" && patch -p1 -i "$HERE/mainview.patch")
cp "$HERE/LglowSalvapantallas.qml" "$TEST/qml/UserInterfaceLayer/Containers/Main/"
cp -a "$HERE/imagenes" "$TEST/imagenes"
touch "$TEST/qml/.lglow-salva-prueba-tv20"
cp "$HERE/volver.sh" "$TEST/volver.sh"
echo 'PREPARADO TV20. Sin cambios al LGlow activo ni al arranque.'
'''
with tarfile.open(root/'outputs/lglow-protector-prueba-tv18.tar.gz') as tf:
    for name in ['probar.sh','volver.sh']:
        data = tf.extractfile('lglow-salva-tv18/'+name).read()
        entries[name] = data.replace(b'tv18',b'tv20').replace(b'com.webos.app.home',b'com.webos.app.fullhome')
entries['archivos.sha256'] = ''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in entries.items()).encode()
out = root/'outputs/lglow-protector-arte-prueba-tv20.tar.gz'
with tarfile.open(out,'w:gz') as tf:
    for name,data in entries.items():
        if name.endswith('.sh'): assert b'\r' not in data
        info=tarfile.TarInfo('lglow-salva-arte-tv20/'+name)
        info.size,info.mode,info.mtime=len(data),0o644,int(time.time())
        tf.addfile(info,io.BytesIO(data))
print('Patch roundtrip OK')
print(hashlib.sha256(out.read_bytes()).hexdigest(),out)
