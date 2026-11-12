import sys

if len(sys.argv) != 2:
    raise SystemExit("Uso: python <script> <IP del televisor>")

import subprocess
from pathlib import Path
s=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','root@'+sys.argv[1]]
base='/var/lib/webosbrew/fullhomecustom/qml/UserInterfaceLayer/Containers'
backup='/var/lib/webosbrew/lglow-salvapantallas-enmarcadas/respaldo-selector'
def call(c,d=None): return subprocess.check_output(s+[c],input=d,timeout=16)
def read(p): return call('cat '+base+'/'+p).decode()
def stage(p,data): call('cat > '+base+'/'+p+'.next',data.encode() if isinstance(data,str) else data)
paths=['Main/LglowBarra.qml','Main/LglowMenu.qml','Main/LglowTema.qml','Main/LglowSalvapantallas.qml','MainView.qml']
bar,menu,tema,saver,main=map(read,paths)
assert 'signal abrirIntervalo()' not in bar and 'interval: 25000' in saver
bar=bar.replace('    signal abrirAjustes()', '    signal abrirAjustes()\n    signal abrirIntervalo()')
bar=bar.replace('        else\n            root.abrirAjustes();','        else if (i === 1)\n            root.abrirAjustes();\n        else\n            root.abrirIntervalo();')
bar=bar.replace('actual < 1','actual < 2').replace('model: 2','model: 3')
bar=bar.replace('                MouseArea {','''                ColorOverlay {
                    anchors.centerIn: parent
                    width: Math.round(root.lado * 0.55)
                    height: width
                    visible: index === 2
                    color: boton.sel ? lglowTema.pastilla : lglowTema.icono
                    source: iconoTiempo

                    Image {
                        id: iconoTiempo
                        anchors.fill: parent
                        source: "lglow-intervalo.png"
                        fillMode: Image.PreserveAspectFit
                        visible: false
                    }
                }

                MouseArea {''')
menu=menu.replace('readonly property var opciones:', 'property string titulo: "Tema"\n    property var valorActual: lglowTema.modo\n    property var opciones:')
menu=menu.replace('    signal cerrado()','    signal cerrado()\n    signal seleccionado(var valor)\n    onSeleccionado: if (titulo === "Tema") lglowTema.elegir(valor)')
menu=menu.replace('opciones[i].modo === lglowTema.modo','opciones[i].modo === valorActual').replace('text: "Tema"','text: root.titulo')
menu=menu.replace('lglowTema.elegir(opciones[actual].modo)','root.seleccionado(opciones[actual].modo)').replace('lglowTema.elegir(modelData.modo)','root.seleccionado(modelData.modo)').replace('lglowTema.modo === modelData.modo','root.valorActual === modelData.modo')
menu=menu.replace('text: modelData.nota','text: modelData.nota || ""\n                            visible: !!modelData.nota')
tema=tema.replace('    property string modo:', '    property int intervaloFotos: 30000\n    property string modo:')
tema=tema.replace('tema.modo = r.rows.item(0).v;','''tema.modo = r.rows.item(0).v;
                var foto = tx.executeSql("SELECT v FROM prefs WHERE k = 'intervaloFotos'");
                if (foto.rows.length) {
                    var guardado = Number(foto.rows.item(0).v);
                    if ([30000, 60000, 180000, 300000].indexOf(guardado) >= 0)
                        tema.intervaloFotos = guardado;
                }''')
tema=tema.replace('    // En automático', '''    function elegirIntervalo(valor) {
        if ([30000, 60000, 180000, 300000].indexOf(valor) < 0)
            return;
        try {
            db().transaction(function(tx) {
                tx.executeSql("CREATE TABLE IF NOT EXISTS prefs(k TEXT PRIMARY KEY, v TEXT)");
                tx.executeSql("INSERT OR REPLACE INTO prefs(k, v) VALUES('intervaloFotos', ?)", [valor]);
            });
            intervaloFotos = valor;
        } catch (e) {
            console.log("[lglow] no se pudo guardar el intervalo: " + e);
        }
    }

    // En automático''')
saver=saver.replace('interval: 25000','interval: lglowTema.intervaloFotos')
main=main.replace('onAbrirAjustes: lglowPanel.abrir()','onAbrirAjustes: lglowPanel.abrir()\n            onAbrirIntervalo: lglowIntervalo.abrir()')
main=main.replace('    // [fullhome-custom] panel rápido', '''    LglowMenu {
        id: lglowIntervalo
        anchors.fill: parent
        z: 2050
        titulo: "Tiempo entre imágenes"
        valorActual: lglowTema.intervaloFotos
        opciones: [
            {modo: 30000, nombre: "30 segundos"},
            {modo: 60000, nombre: "1 minuto"},
            {modo: 180000, nombre: "3 minutos"},
            {modo: 300000, nombre: "5 minutos"}
        ]
        derecha: lglowBarra.x + lglowBarra.width
        arriba: lglowBarra.y + lglowBarra.height + styleSheet.getRValue(20)
        onSeleccionado: lglowTema.elegirIntervalo(valor)
        onCerrado: lglowBarra.forceActiveFocus()
    }

    // [fullhome-custom] panel rápido''')
main=main.replace('&& !lglowPanel.open && !lglowMenu.open;', '&& !lglowPanel.open && !lglowMenu.open && !lglowIntervalo.open;')
for path,new in zip(paths,[bar,menu,tema,saver,main]):
 stage(path,new)
stage('Main/lglow-intervalo.png',Path(r'C:\Users\chris\Pictures\487356-200.png').read_bytes())
call(f'mkdir -p {backup}')
for path in paths:
 call(f'cp -p {base}/{path} {backup}/{path.rsplit("/",1)[-1]}')
call('set -e; '+'; '.join(f'mv {base}/{p}.next {base}/{p}' for p in paths+['Main/lglow-intervalo.png']))
print('Selector instalado en LG 43UN7300PSC')

