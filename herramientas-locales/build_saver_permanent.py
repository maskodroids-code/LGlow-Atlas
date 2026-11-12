from pathlib import Path
import hashlib, tarfile

root = Path(__file__).resolve().parent.parent
with tarfile.open(root / 'outputs/lglow-protector-arte-tv18.tar.gz') as archive:
    component = archive.extractfile('lglow-salva-arte-tv18/LglowSalvapantallas.qml').read()
digest = hashlib.sha256(component).hexdigest()
script = '''#!/bin/sh
set -eu
BASE=/var/lib/webosbrew
TEST=$BASE/lglow-salva-prueba-tv18
LIVE=$BASE/fullhomecustom
BACK=$BASE/lglow-respaldo-antes-protector-tv18
DEST=/usr/palm/applications/com.webos.app.home/qml
VIEW=qml/UserInterfaceLayer/Containers/MainView.qml
PART=qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml
[ "$(id -u)" = 0 ]
[ ! -e "$DEST/.lglow-salva-prueba-tv18" ] || { echo 'ERROR: retirar primero el montaje de prueba'; exit 1; }
[ -f "$BASE/homecustom/apply.sh" ]
[ ! -e "$BACK" ] || { echo 'ERROR: ya existe un respaldo; detenerse'; exit 1; }
echo '328468759921b55c450db9c848857447  '"$LIVE/$VIEW" | md5sum -c -
echo 'COMPONENTHASH  '"$TEST/$PART" | sha256sum -c -
[ "$(grep -c 'item.timeoutMs = 30000;' "$TEST/$VIEW")" = 1 ]
[ "$(find "$TEST/imagenes" -type f -name 'arte-*.jpg' | wc -l)" = 16 ]
mkdir "$BACK"
cp -p "$LIVE/$VIEW" "$BACK/MainView.qml"
if [ -e "$LIVE/$PART" ]; then
    cp -p "$LIVE/$PART" "$BACK/LglowSalvapantallas.qml"
fi
mkdir -p "$LIVE/imagenes"
cp "$TEST"/imagenes/arte-*.jpg "$LIVE/imagenes/"
sed 's@file:///var/lib/webosbrew/lglow-salva-prueba-tv18/imagenes/@file:///var/lib/webosbrew/fullhomecustom/imagenes/@g' "$TEST/$PART" > "$BACK/nuevo-protector.qml"
sed 's/item.timeoutMs = 30000;.*/item.timeoutMs = 300000; \/\/ cinco minutos/' "$TEST/$VIEW" > "$BACK/nuevo-MainView.qml"
grep -q 'item.timeoutMs = 300000;' "$BACK/nuevo-MainView.qml"
! grep -q 'file:///var/lib/webosbrew/lglow-salva-prueba-tv18/' "$BACK/nuevo-protector.qml"
cp "$BACK/nuevo-protector.qml" "$LIVE/$PART"
cp "$BACK/nuevo-MainView.qml" "$LIVE/$VIEW"
cat > "$BACK/quitar-protector.sh" <<'RECUPERAR'
#!/bin/sh
set -eu
BACK=/var/lib/webosbrew/lglow-respaldo-antes-protector-tv18
LIVE=/var/lib/webosbrew/fullhomecustom
cp -p "$BACK/MainView.qml" "$LIVE/qml/UserInterfaceLayer/Containers/MainView.qml"
if [ -e "$BACK/LglowSalvapantallas.qml" ]; then
    cp -p "$BACK/LglowSalvapantallas.qml" "$LIVE/qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml"
fi
echo 'Protector retirado del inicio. Reiniciar la TV para aplicar.'
RECUPERAR
echo 'PROTECTOR INSTALADO: espera de cinco minutos. Reiniciar para comprobar.'
echo 'Para revertir: sh /var/lib/webosbrew/lglow-respaldo-antes-protector-tv18/quitar-protector.sh y reiniciar.'
'''.replace('COMPONENTHASH', digest)
out = root / 'outputs/lglow-instalar-protector-arte-tv18.sh'
out.write_text(script, encoding='utf-8', newline='\n')
assert b'\r' not in out.read_bytes()
print(hashlib.sha256(out.read_bytes()).hexdigest(), out)
