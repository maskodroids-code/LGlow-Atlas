from pathlib import Path
from PIL import Image, ImageOps
import hashlib, io, json, tarfile, time

root = Path(__file__).resolve().parent.parent
source = Path('C:/lglow-main/salvapantallas')
entries = {}
seen = set()
report = []
for file in sorted(source.iterdir()):
    if file.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp'): continue
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    if digest in seen: continue
    seen.add(digest)
    with Image.open(file) as original:
        image = ImageOps.exif_transpose(original).convert('RGB')
        dimensions = image.size
        image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
        data = io.BytesIO()
        image.save(data, format='JPEG', quality=90, optimize=True)
    name = 'arte-%02d.jpg' % (len(report) + 1)
    entries['imagenes/' + name] = data.getvalue()
    report.append({'original': file.name, 'archivo': name, 'dimensiones_originales': dimensions, 'dimensiones_tv': image.size})
assert report
base = root / 'outputs/LglowSalvapantallas-v4.qml'
qml = base.read_text(encoding='utf-8')
picks = [{'title': '', 'backdrop': 'file:///var/lib/webosbrew/lglow-salva-prueba-tv18/imagenes/' + row['archivo']} for row in report]
qml = qml.replace('    property var recommendations: []', '    property var recommendations: []\n    readonly property var localImages: ' + json.dumps(picks))
qml = qml.replace('!recommendations || !recommendations.length', '!localImages || !localImages.length').replace('index % recommendations.length', 'index % localImages.length').replace('pendingPick = recommendations[requestedIndex]', 'pendingPick = localImages[requestedIndex]')
qml = qml.replace('text: saver.currentPick.title || "LGlow"', 'text: ""')
assert 'pendingPick = localImages[' in qml
entries['LglowSalvapantallas.qml'] = qml.encode('utf-8')
hashes = [hashlib.sha256((root / ('outputs/LglowSalvapantallas-v%d.qml' % version)).read_bytes()).hexdigest() for version in (3, 4)]
script = '''#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
FILE=$TEST/qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml
[ "$(id -u)" = 0 ]
[ ! -e "$DEST/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: primero volver al LGlow estable'; exit 1; }
[ -f "$TEST/qml/.lglow-salva-prueba-tv18" ]
HASH=$(sha256sum "$FILE")
case "$HASH" in
    HASH3*|HASH4*) ;;
    *) echo 'ERROR: componente de prueba desconocido; no se cambia nada'; exit 1 ;;
esac
[ ! -e "$FILE.antes-arte" ] || { echo 'ERROR: ya existe respaldo de esta prueba'; exit 1; }
(cd "$HERE" && sha256sum -c archivos.sha256)
mkdir -p "$TEST/imagenes"
cp "$HERE"/imagenes/*.jpg "$TEST/imagenes/"
cp -p "$FILE" "$FILE.antes-arte"
cp "$HERE/LglowSalvapantallas.qml" "$FILE"
echo 'ARTE PREPARADO. No se cambio el LGlow activo ni el arranque.'
'''.replace('HASH3', hashes[0]).replace('HASH4', hashes[1])
entries['actualizar.sh'] = script.encode()
entries['seleccion.json'] = json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8')
entries['archivos.sha256'] = ''.join(hashlib.sha256(data).hexdigest() + '  ' + name + '\n' for name, data in entries.items()).encode()
archive = root / 'outputs/lglow-protector-arte-tv18.tar.gz'
with tarfile.open(archive, 'w:gz') as tf:
    for name, data in entries.items():
        info = tarfile.TarInfo('lglow-salva-arte-tv18/' + name)
        info.size, info.mode, info.mtime = len(data), 0o644, int(time.time())
        tf.addfile(info, io.BytesIO(data))
print(json.dumps({'imagenes': len(report), 'bytes': archive.stat().st_size, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'archive': str(archive)}))
