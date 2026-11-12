from pathlib import Path
import hashlib, io, tarfile, time

root=Path(__file__).resolve().parent.parent
original=(root/'outputs/original-tv20-StarfishViewStateController.qml').read_bytes()
text=original.decode('utf-8')
start=text.index('        onUserActivityExpired: {')
end=text.index('\n    Connections {',start)
section=text[start:end]
old='''            if (views.starfishHome)
                views.starfishHome.close();'''
replacement='''            // [lglow-tv20] Solo omite el cierre por inactividad del home
            // que declara explicitamente su protector local disponible.
            var keepLglowHome = false;
            try {
                var home = views.starfishHome;
                var props = home && home.currentView && home.currentView.windowProperties;
                keepLglowHome = userActivityTimer && home.isOpen
                    && home.currentItem && home.currentItem.appId === "com.webos.app.fullhome"
                    && props && props.lglowLocalSaver === "true";
            } catch (e) {
                keepLglowHome = false;
            }
            if (views.starfishHome && !keepLglowHome)
                views.starfishHome.close();'''
assert section.count(old)==1
modified=text[:start]+section.replace(old,replacement)+text[end:]
assert modified.replace(replacement,old)==text
entries={'StarfishViewStateController.qml':modified.encode()}
with tarfile.open(root/'outputs/lglow-protector-arte-prueba-tv20.tar.gz') as tf:
    component=tf.extractfile('lglow-salva-arte-tv20/LglowSalvapantallas.qml').read()
qml=component.decode()
qml=qml.replace('    onAllowedChanged: {','''    onAllowedChanged: {
        if (windowController)
            windowController.setWindowProperty("lglowLocalSaver", allowed ? "true" : "false");''',1)
qml=qml.replace('    Component.onCompleted: {','    Component.onCompleted: {',1)
# Add destruction hook to root, not to the nested service.
pos=qml.rfind('\n}')
qml=qml[:pos]+'''
    Component.onDestruction: {
        if (windowController)
            windowController.setWindowProperty("lglowLocalSaver", "false");
    }
'''+qml[pos:]
entries['LglowSalvapantallas.qml']=qml.encode()
script='''#!/bin/sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv20
DEST=/usr/palm/applications/com.webos.app.fullhome/qml
CTRL=/usr/lib/qml/WebOSCompositor/controllers/StarfishViewStateController.qml
PART=qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml
[ "$(id -u)" = 0 ]
[ ! -e "$DEST/.lglow-salva-prueba-tv20" ] || { echo 'ERROR: retirar primero la prueba del home'; exit 1; }
[ ! -e "$TEST/$PART.antes-idle" ] || { echo 'ERROR: ya existe esta correccion'; exit 1; }
echo 'ORIGINALHASH  '"$CTRL" | sha256sum -c -
echo 'COMPONENTHASH  '"$TEST/$PART" | sha256sum -c -
(cd "$HERE" && sha256sum -c archivos.sha256)
cp -p "$TEST/$PART" "$TEST/$PART.antes-idle"
cp "$HERE/LglowSalvapantallas.qml" "$TEST/$PART"
cp "$HERE/StarfishViewStateController.qml" "$TEST/StarfishViewStateController.qml"
echo 'CORRECCION PREPARADA. Sin montajes nuevos ni reinicio del compositor.'
'''.replace('ORIGINALHASH',hashlib.sha256(original).hexdigest()).replace('COMPONENTHASH',hashlib.sha256(component).hexdigest())
entries['preparar.sh']=script.encode()
activate='''#!/bin/sh
set -eu
TEST=/var/lib/webosbrew/lglow-salva-prueba-tv20
DEST=/usr/palm/applications/com.webos.app.fullhome/qml
CTRL=/usr/lib/qml/WebOSCompositor/controllers/StarfishViewStateController.qml
[ "$(id -u)" = 0 ]
[ -f "$TEST/StarfishViewStateController.qml" ]
[ ! -e "$DEST/.lglow-salva-prueba-tv20" ]
echo 'ORIGINALHASH  '"$CTRL" | sha256sum -c -
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
'''.replace('ORIGINALHASH',hashlib.sha256(original).hexdigest())
entries['probar.sh']=activate.encode()
entries['archivos.sha256']=''.join(hashlib.sha256(v).hexdigest()+'  '+k+'\n' for k,v in entries.items()).encode()
out=root/'outputs/lglow-tv20-correccion-inactividad.tar.gz'
with tarfile.open(out,'w:gz') as tf:
    for name,data in entries.items():
        info=tarfile.TarInfo('lglow-tv20-idle/'+name)
        info.size,info.mode,info.mtime=len(data),0o644,int(time.time())
        tf.addfile(info,io.BytesIO(data))
print(hashlib.sha256(out.read_bytes()).hexdigest(),out)
