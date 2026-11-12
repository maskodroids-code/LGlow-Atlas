from pathlib import Path
import hashlib
import json
import shutil
import tarfile

cwd = Path(__file__).resolve().parent.parent
src = Path('C:/lglow-main')
pkg = cwd / 'work' / 'trial-package'
pkg.mkdir(exist_ok=False)
shutil.copytree(cwd / 'work/port/patches', pkg / 'patches')
shutil.copytree(src / 'tv/qml/fullhome', pkg / 'qml')
shutil.copytree(src / 'tv/fondos', pkg / 'fondos')
shutil.copy2(src / 'tv/config.example.json', pkg / 'config.example.json')
shutil.copy2(src / 'LICENSE', pkg / 'LICENSE')
qs = (src / 'tv/quicksettings/QuickSettings.qml').read_text(encoding='utf-8')
assert qs.count('import YSM.SystemUI 1.0') == 1
(pkg / 'QuickSettings-adaptado-NO-ACTIVAR.qml').write_text(qs.replace('import YSM.SystemUI 1.0', 'import SystemUIComponent 1.0'), encoding='utf-8', newline='\n')

prepare = '''#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
FULL=/var/lib/webosbrew/fullhomecustom
STAGE=$HERE/staging
[ "$(id -u)" = 0 ] || { echo 'ERROR: requiere root'; exit 1; }
[ ! -e "$FULL" ] || { echo 'ERROR: fullhomecustom ya existe; detenerse para revisarlo'; exit 1; }
[ ! -e "$STAGE" ] || { echo 'ERROR: staging ya existe; detenerse para revisarlo'; exit 1; }
command -v patch >/dev/null
for part in fullhome home; do
    echo "==> comprobando originales: $part"
    (cd "/usr/palm/applications/com.webos.app.$part" && md5sum -c "$HERE/patches/$part/originales.md5")
done
mkdir -p "$STAGE"
cp -a /usr/palm/applications/com.webos.app.fullhome/qml "$STAGE/qml"
for p in "$HERE"/patches/fullhome/*.patch; do
    (cd "$STAGE" && patch -p1 -i "$p")
done
cp "$HERE"/qml/*.qml "$STAGE/qml/UserInterfaceLayer/Containers/Main/"
cp "$HERE/config.example.json" "$STAGE/config.json"
chmod 600 "$STAGE/config.json"
mkdir -p "$STAGE/tiles"
cp "$HERE/fondos/perla.jpg" "$STAGE/fondo.jpg"
cp "$HERE/fondos/perla.jpg" "$STAGE/fondo-perla.jpg"
cp "$HERE/fondos/aurora.jpg" "$STAGE/fondo-aurora.jpg"
mv "$STAGE" "$FULL"
echo 'PREPARADO. No se activo ningun montaje ni script de arranque.'
echo 'No se modificaron compositor, precargas ni particiones de LG.'
'''
activate = '''#!/bin/sh
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
'''
rollback = '''#!/bin/sh
set -eu
APP=com.webos.app.fullhome
for d in /usr/palm/applications/$APP/qml /tmp/checkpoint/$APP /mnt/lg/cmn_data/checkpoint/$APP; do
    if mount | grep -F " $d " >/dev/null; then umount "$d"; fi
done
pid=$(pidof "$APP" || true)
[ -z "$pid" ] || kill -9 $pid
sleep 2
luna-send -n 1 luna://com.webos.applicationManager/launch '{"id":"com.webos.app.fullhome"}'
echo 'Montajes de prueba retirados. No se borraron archivos.'
'''
for name, text in [('preparar.sh', prepare), ('probar.sh', activate), ('volver.sh', rollback)]:
    (pkg / name).write_text(text, encoding='utf-8', newline='\n')
notes = '''Prueba experimental LGlow: LG 43UN7300PSC, webOS 5.6.2-21, firmware 04.64.00.
Parches derivados de tv/patches en la copia local de IrvingGuerra/lglow.
No contiene QML propietario original de LG: se copia desde la propia TV al preparar.
12 parches fullhome y 3 home regenerados y comprobados contra los originales del usuario.
Prueba inicial: solo fullhome. Los parches home y el panel adaptado quedan SIN activar.
preparar.sh verifica ambos juegos de originales antes de crear archivos en /var/lib/webosbrew.
probar.sh monta temporalmente fullhome y oculta sus checkpoints sin borrarlos; relanza el home.
No instala init.d, no reinicia compositor y no cambia precargas ni ajustes de LG.
volver.sh retira montajes temporales y relanza el home original. Un reinicio tambien los retira.
Los archivos preparados en /var/lib permanecen tras reiniciar, pero no se activan solos.
NO ejecutar tv/install.sh del proyecto original con las huellas modificadas.
Todavia no validado en ejecucion. No es una version publicada por el autor de LGlow.
'''
(pkg / 'LEEME.txt').write_text(notes, encoding='utf-8', newline='\n')
shutil.copy2(cwd / 'work/port/verification.json', pkg / 'verification.json')
out = cwd / 'outputs'
out.mkdir(exist_ok=True)
archive = out / 'lglow-prueba-43UN7300PSC-04.64.00.tar.gz'
with tarfile.open(archive, 'w:gz') as tf:
    for f in sorted(pkg.rglob('*')):
        if f.is_file():
            info = tf.gettarinfo(str(f), arcname='lglow-port-test/' + f.relative_to(pkg).as_posix())
            info.uid = info.gid = 0
            info.uname = info.gname = ''
            info.mode = 0o644
            with f.open('rb') as stream: tf.addfile(info, stream)
with tarfile.open(archive) as tf:
    assert all(m.isfile() and '..' not in Path(m.name).parts and not m.name.startswith('/') for m in tf.getmembers())
print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}))
