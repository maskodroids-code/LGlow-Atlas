from pathlib import Path
import hashlib, io, json, re, shlex, subprocess, tarfile

source = Path(__file__).resolve().parents[1] / 'salvapantallas' / 'Con marco'
files = sorted(source.glob('*.jpg'))
assert len(files) == 17
archive = io.BytesIO()
with tarfile.open(fileobj=archive, mode='w') as tar:
    for i, file in enumerate(files, 1):
        tar.add(file, arcname=f'arte-{i:02}.jpg')
body = archive.getvalue()
digest = hashlib.sha256(body).hexdigest()
target = '/usr/palm/applications/com.webos.app.screensaver/qml/Containers/MainView.qml'
home = '/var/lib/webosbrew/fullhomecustom/qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml'

def update(ip, name, previous, previous_hook=None):
    ssh = ['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=5','root@'+ip]
    base = '/var/lib/webosbrew/lglow-salvapantallas-enmarcadas'
    images = '/media/developer/lglow-salvapantallas-enmarcadas'
    def call(command, data=None, seconds=20):
        return subprocess.run(ssh+[command],input=data,capture_output=True,check=True,timeout=seconds).stdout
    def write(path, text):
        call('umask 022; cat > '+shlex.quote(path),text.encode())
    native = call('cat '+(previous+'/MainView.original.qml' if previous else target)).decode('utf-8-sig')
    qml = call('cat '+home).decode('utf-8-sig')
    assert 'Mode_ScreenSaver' in native and 'id: lglowFramedArt' not in native
    assert 'id: saver' in qml and 'opacity: 0.48' in qml and '    MouseArea {' in qml
    urls = ['file://'+images+f'/arte-{i:02}.jpg' for i in range(1,len(files)+1)]
    photos = [{'backdrop':url,'title':''} for url in urls]
    qml, count = re.subn(r'(?m)^\s*readonly property var localImages: [^\n]+',
                        lambda _: '\n    readonly property var localImages: '+json.dumps(photos),qml)
    assert count == 1
    shade = re.search(r'(?m)^    Rectangle \{\n        anchors.fill: parent\n        z: 3\n',qml)
    assert shade
    qml = qml[:shade.start()]+qml[qml.index('    MouseArea {',shade.start()):]
    qml = qml.replace('Image.PreserveAspectCrop','Image.PreserveAspectFit')
    overlay = '''
    Image {
        id: lglowFramedArt
        anchors.fill: parent
        z: 10000
        visible: root.state === "Mode_ScreenSaver" && status === Image.Ready
        fillMode: Image.PreserveAspectFit
        asynchronous: true
        cache: false
        sourceSize.width: 1920
        sourceSize.height: 1080
        property int currentPhoto: 0
        readonly property var photos: PHOTO_LIST
        source: root.state === "Mode_ScreenSaver" ? photos[currentPhoto] : ""

        Timer {
            interval: 25000
            repeat: true
            running: root.state === "Mode_ScreenSaver"
            onTriggered: lglowFramedArt.currentPhoto =
                (lglowFramedArt.currentPhoto + 1) % lglowFramedArt.photos.length
        }
    }
'''.replace('PHOTO_LIST',json.dumps(urls))
    native = native[:native.rindex('}')]+overlay+'}\n'
    call(f'mkdir -p {base} {images}; chmod 755 {images}')
    call(f'umask 022; cat > {images}/art.tar',body,140)
    assert call(f'sha256sum {images}/art.tar').decode().split()[0] == digest
    call(f'tar -xf {images}/art.tar -C {images} && rm {images}/art.tar')
    call(f'cp -p {home} {base}/HomeSalvapantallas.original.qml')
    write(base+'/MainView.qml',native)
    write(home+'.framed-next',qml)
    write(base+'/apply.sh',f'''#!/bin/sh
set -eu
target={target}
source={base}/MainView.qml
if grep -q 'id: lglowFramedArt' "$target"; then exit 0; fi
mount --bind "$source" "$target"
''')
    hook='/var/lib/webosbrew/init.d/20-lglow-salvapantallas-enmarcadas'
    actions=[f'chmod 755 {base}/apply.sh']
    if previous:
        actions.append(f'if grep -q "id: lglowPhotos" {target}; then umount {target}; fi')
    actions += [f'{base}/apply.sh',f'mv {home}.framed-next {home}',f'ln -s {base}/apply.sh {hook}']
    if previous_hook: actions += ['rm ' + shlex.quote(previous_hook)]
    call(' && '.join(actions))
    print(f'{name}: 17 imágenes copiadas y QML actualizado',flush=True)
    app='com.webos.app.fullhome' if previous else 'com.webos.app.home'
    cmd=f"""luna-send -n 1 luna://com.webos.settingsservice/setSystemSettings '{{"category":"general","settings":{{"screenSaverEnabled":"on","screenSaverAd":"off"}}}}'; luna-send -n 1 luna://com.webos.service.tvpower/power/turnOnScreen '{{}}'; luna-send -n 1 luna://com.webos.applicationManager/closeByAppId '{{"id":"com.webos.app.screensaver"}}'; pid=$(pidof {app} || true); [ -z "$pid" ] || kill -TERM $pid; sleep 1; luna-send -n 1 luna://com.webos.applicationManager/launch '{{"id":"{app}"}}'"""
    print(call(cmd).decode(),flush=True)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('ip')
    parser.add_argument('model', choices=['43UN7300PSC', '50UP7500PSF'])
    parser.add_argument('--previous-dir')
    parser.add_argument('--previous-hook')
    args = parser.parse_args()
    if args.model == '43UN7300PSC' and not args.previous_dir:
        parser.error('43UN7300PSC requiere --previous-dir con el respaldo de la version anterior')
    if args.model == '50UP7500PSF' and args.previous_dir:
        parser.error('50UP7500PSF utiliza la variante sin respaldo anterior')
    update(args.ip, args.model, args.previous_dir, args.previous_hook)
