import sys
import subprocess, concurrent.futures
base='/var/lib/webosbrew/lglow-salvapantallas-enmarcadas'
target='/usr/palm/applications/com.webos.app.screensaver/qml/Containers/MainView.qml'
def update(ip):
 s=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','root@'+ip]
 def call(cmd, data=None):
  return subprocess.check_output(s+[cmd],input=data,timeout=20)
 path=base+'/MainView.qml'
 src=call('cat '+path).decode('utf-8')
 start=src.index('    Image {\n        id: lglowFramedArt')
 photos=next(line.strip() for line in src[start:].splitlines() if 'readonly property var photos:' in line)
 art='''    Item {
        id: lglowFramedArt
        anchors.fill: parent
        z: 10000
        visible: active && (front >= 0 || fade.running)
        property bool active: root.state === "Mode_ScreenSaver"
        property int front: -1
        property int next: -1
        property int photoIndex: 0
        PHOTOS

        function loadPhoto(index) {
            if (!active || next >= 0 || fade.running) return;
            next = front === 0 ? 1 : 0;
            var image = layers.itemAt(next);
            if (!image) { next = -1; return; }
            image.opacity = 0;
            image.z = 2;
            if (front >= 0) layers.itemAt(front).z = 1;
            image.source = photos[index];
            ready(image, next);
        }

        function ready(image, slot) {
            if (!active || slot !== next || fade.running) return;
            if (image.status === Image.Error) { next = -1; return; }
            if (image.status !== Image.Ready) return;
            if (front < 0) {
                image.opacity = 1;
                front = slot;
                next = -1;
                return;
            }
            fade.target = image;
            fade.start();
        }

        onActiveChanged: {
            if (active) {
                firstPhoto.restart();
            } else {
                fade.stop();
                front = -1;
                next = -1;
                photoIndex = 0;
                for (var i = 0; i < layers.count; i++) {
                    var image = layers.itemAt(i);
                    if (image) { image.opacity = 0; image.source = ""; }
                }
            }
        }

        Repeater {
            id: layers
            model: 2
            Image {
                id: framedImage
                anchors.fill: parent
                opacity: 0
                fillMode: Image.PreserveAspectFit
                asynchronous: true
                cache: false
                sourceSize.width: 1920
                sourceSize.height: 1080
                onStatusChanged: lglowFramedArt.ready(framedImage, index)
            }
        }

        NumberAnimation {
            id: fade
            property: "opacity"
            from: 0
            to: 1
            duration: 1800
            easing.type: Easing.InOutSine
            onStopped: {
                if (!lglowFramedArt.active || lglowFramedArt.next < 0 ||
                        !target || target.opacity < 0.999) return;
                var previous = layers.itemAt(lglowFramedArt.front);
                lglowFramedArt.front = lglowFramedArt.next;
                lglowFramedArt.next = -1;
                if (previous) { previous.opacity = 0; previous.source = ""; }
            }
        }

        Timer {
            id: firstPhoto
            interval: 0
            onTriggered: lglowFramedArt.loadPhoto(0)
        }

        Component.onCompleted: if (active) firstPhoto.restart()

        Timer {
            interval: 25000
            repeat: true
            running: lglowFramedArt.active
            onTriggered: {
                lglowFramedArt.photoIndex =
                    (lglowFramedArt.photoIndex + 1) % lglowFramedArt.photos.length;
                lglowFramedArt.loadPhoto(lglowFramedArt.photoIndex);
            }
        }
    }
'''.replace('PHOTOS',photos)
 call('cat > '+path+'.next',(src[:start]+art+'}\n').encode())
 call(f'set -e; cp -p {path} {path}.antes-fundido; mv {path}.next {path}; umount {target}; {base}/apply.sh; grep -n "duration: 1800" {target}')
 print(ip,'fundido aplicado',flush=True)
if len(sys.argv) < 2:
 raise SystemExit('Uso: python aplicar-fundido.py <IP del televisor> [otra IP]')
with concurrent.futures.ThreadPoolExecutor() as e: list(e.map(update,sys.argv[1:]))

