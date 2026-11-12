import sys

if len(sys.argv) != 2:
    raise SystemExit("Uso: python <script> <IP del televisor>")

import subprocess
s=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','root@'+sys.argv[1]]
b='/var/lib/webosbrew/lglow-salvapantallas-enmarcadas'
target='/usr/lib/qt5/qml/KeyFilters/systemUi.js'
def call(c,d=None):return subprocess.check_output(s+[c],input=d,timeout=20)
src=call('cat '+target).decode()
n='    if (pressed && key === Qt.Key_Super_L)\n        global.prepareToGoHome();'
assert src.count(n)==1
patch='''    // Keep LGlow open after a short second press of Home.
    if (!pressed && key === Qt.Key_Super_L && homeView.visible &&
            homeView.appId === "com.webos.app.fullhome")
        return KeyPolicy.Accepted;

'''
call('cat > '+b+'/systemUi.js',(src.replace(n,patch+n)).encode())
hook=b+'/mantener-inicio.sh'
sh=call('cat '+hook).decode()
n2='systemctl --no-block try-restart surface-manager-daemon.service'
assert sh.count(n2)==1
# Keep the compositor and remote filter loaded together on each boot.
sh=sh.replace('if grep -q \'var keepPhotoSaver\' "$target"; then exit 0; fi\nmount --bind "$source" "$target"','''if ! grep -q 'var keepPhotoSaver' "$target"; then
    mount --bind "$source" "$target"
    changed=1
fi
if ! grep -q 'Keep LGlow open after a short second press' FILTER; then
    mount --bind BASE/systemUi.js FILTER
    changed=1
fi
[ "\${changed:-0}" = 1 ] || exit 0'''.replace('FILTER',target).replace('BASE',b))
assert 'systemUi.js' in sh
call('cat > '+hook+'.next',sh.encode())
call(f'set -e; sh -n {hook}.next; cp -p {hook} {hook}.antes-home; chmod 755 {hook}.next; mv {hook}.next {hook}; {hook}')
print('Filtro Home actualizado')

