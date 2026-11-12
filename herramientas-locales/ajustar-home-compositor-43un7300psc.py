import sys

if len(sys.argv) != 2:
    raise SystemExit("Uso: python <script> <IP del televisor>")

import subprocess
ssh=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','root@'+sys.argv[1]]
base='/var/lib/webosbrew/lglow-salvapantallas-enmarcadas'
path=base+'/StarfishViewStateController.qml'
target='/usr/lib/qml/WebOSCompositor/controllers/StarfishViewStateController.qml'
def run(cmd,data=None): return subprocess.check_output(ssh+[cmd],input=data,timeout=20)
src=run('cat '+path).decode()
a='''            } else if (views.starfishHome && !(views.notification && views.notification.modal)) {
                views.starfishHome.toggleHome();
            }'''
b='''            } else if (views.starfishHome && !(views.notification && views.notification.modal)) {
                var home = views.starfishHome;
                var lglowOpen = home.isOpen && home.currentItem &&
                    home.currentItem.appId === "com.webos.app.fullhome";
                if (!lglowOpen)
                    home.toggleHome();
            }'''
assert src.count(a)==1 and 'var keepPhotoSaver' in src
run('cat > '+path+'.next',src.replace(a,b).encode())
cmd=f'''set -e
cp -p {path} {path}.antes-home
mv {path}.next {path}
umount {target}
{base}/mantener-inicio.sh
grep -n lglowOpen {target}
'''
print(run(cmd).decode())

