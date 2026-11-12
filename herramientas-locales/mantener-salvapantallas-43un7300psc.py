import sys

if len(sys.argv) != 2:
    raise SystemExit("Uso: python <script> <IP del televisor>")

import subprocess
s=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','root@'+sys.argv[1]]
base='/var/lib/webosbrew/lglow-salvapantallas-enmarcadas'
comp='/usr/lib/qml/WebOSCompositor/controllers/StarfishViewStateController.qml'
home='/var/lib/webosbrew/fullhomecustom/qml/UserInterfaceLayer/Containers/Main/LglowSalvapantallas.qml'
def call(cmd,data=None):
 return subprocess.check_output(s+[cmd],input=data,timeout=16)
def put(path,body):
 call('umask 022; cat > '+path,body.encode())
raw=call('cat '+comp).decode()
start=raw.index('        onUserActivityExpired: {')
needle='            if (views.starfishHome)\n                views.starfishHome.close();'
pos=raw.index(needle,start)
assert pos- start < 1300
guard='''            var keepPhotoSaver = false;
            var home = views.starfishHome;
            if (userActivityTimer && home && home.isOpen && home.currentItem &&
                    home.currentItem.appId === "com.webos.app.fullhome" &&
                    home.currentView && home.currentView.windowProperties) {
                var flag = home.currentView.windowProperties.lglowLocalSaver;
                keepPhotoSaver = flag === true || flag === "true";
            }
            if (home && !keepPhotoSaver)
                home.close();'''
qml=call('cat '+home).decode()
needle2='    onAllowedChanged: {'
assert qml.count(needle2)==1
qml=qml.replace(needle2,'''    onShowingChanged: {
        if (windowController)
            windowController.setWindowProperty("lglowLocalSaver", showing && allowed ? "true" : "false");
    }

'''+needle2)
call(f'cp -p {home} {base}/HomeSalvapantallas.antes-cierre.qml')
put(base+'/StarfishViewStateController.qml',raw[:pos]+guard+raw[pos+len(needle):])
put(home+'.next',qml)
hook='/var/lib/webosbrew/init.d/21-lglow-salvapantallas-fullhome'
put(base+'/mantener-inicio.sh',f'''#!/bin/sh
set -eu
target={comp}
source={base}/StarfishViewStateController.qml
if grep -q 'var keepPhotoSaver' "$target"; then exit 0; fi
mount --bind "$source" "$target"
''')
call(f'set -e; chmod 755 {base}/mantener-inicio.sh; {base}/mantener-inicio.sh; mv {home}.next {home}; ln -s {base}/mantener-inicio.sh {hook}; grep -n keepPhotoSaver {comp}')
print('Protector y regla de inactividad instalados.')

