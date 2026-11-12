import subprocess
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Uso: python <script> <IP del televisor>")

host = sys.argv[1]
base='/var/lib/webosbrew/fullhomecustom/qml/UserInterfaceLayer/Containers'
def run(command, data=None, host=host):
    return subprocess.check_output(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',f'root@{host}',command],input=data,timeout=15)
def read(path, host=host):
    return run(f'cat {base}/{path}',host=host).decode()
def replace(s, old, new):
    assert s.count(old)==1, old
    return s.replace(old,new)
para=read('Main/ParaTi.qml')
ref=read('Main/ParaTi.qml',18)
para=replace(para,'import QtQuick 2.6','import QtQuick 2.6\nimport QtQuick.LocalStorage 2.0')
para=replace(para,'    property string weatherText: ""',ref[ref.index('    property string weatherText:'):ref.index('    property var tabs:')].rstrip()+'''
    property var locationOverride: null
    readonly property var weatherConfig: locationOverride || config

    function locationDb() {
        return LocalStorage.openDatabaseSync("lglow", "1.0", "Preferencias de LGlow", 1000);
    }

    function readLocation() {
        try {
            locationDb().transaction(function(tx) {
                tx.executeSql("CREATE TABLE IF NOT EXISTS prefs(k TEXT PRIMARY KEY, v TEXT)");
                var result = tx.executeSql("SELECT v FROM prefs WHERE k = 'weatherLocation'");
                if (result.rows.length)
                    locationOverride = JSON.parse(result.rows.item(0).v);
            });
        } catch (e) {
            console.log("[lglow] No se pudo leer la ubicación");
        }
    }

    function saveLocation(place) {
        var location = {city: place.name, latitude: place.latitude, longitude: place.longitude};
        try {
            locationDb().transaction(function(tx) {
                tx.executeSql("CREATE TABLE IF NOT EXISTS prefs(k TEXT PRIMARY KEY, v TEXT)");
                tx.executeSql("INSERT OR REPLACE INTO prefs(k,v) VALUES(?,?)",
                              ["weatherLocation", JSON.stringify(location)]);
            });
        } catch (e) {
            return false;
        }
        locationOverride = location;
        weatherText = windText = humidityText = uvText = "";
        loadWeather();
        return true;
    }''')
start=para.index('    function loadWeather()')
end=para.index('    function tmdb',start)
weather=ref[ref.index('    function loadWeather()'):ref.index('    function tmdb')]
weather=weather.replace('        if (config.latitude === undefined)','        var place = weatherConfig;\n        if (place.latitude === undefined || place.longitude === undefined)').replace('config.latitude','place.latitude').replace('config.longitude','place.longitude').replace('config.city','place.city').replace('if (!r || !r.current)','if (place !== weatherConfig || !r || !r.current)')
para=para[:start]+weather+para[end:]
para=replace(para,'        tick();\n        get(configPath','        tick();\n        readLocation();\n        get(configPath')
start=para.index('    Text {\n        id: info\n')
end=para.index('    // Títulos',start)
row=ref[ref.rindex('    Row {',0,ref.index('        anchors.right: parent.right\n        anchors.verticalCenter: tabRow.verticalCenter\n        spacing:')):ref.index('    // Títulos')]
row=replace(row,'root.dateText + "   " + root.clock + (root.weatherText ? "     " + root.weatherText : "")','root.weatherText')
para=para[:start]+row+para[end:]
bar=read('Main/LglowBarra.qml')
bar=replace(bar,'    signal abrirIntervalo()','    signal abrirIntervalo()\n    signal abrirUbicacion()')
bar=replace(bar,'        else\n            root.abrirIntervalo();','        else if (i === 2)\n            root.abrirIntervalo();\n        else\n            root.abrirUbicacion();')
bar=replace(bar,'actual < 2','actual < 3')
bar=replace(bar,'model: 3','model: 4')
bar=replace(bar,'visible: index === 2','visible: index >= 2')
bar=replace(bar,'source: "lglow-intervalo.png"','source: index === 2 ? "lglow-intervalo.png" : "lglow-ubicacion.png"')
main=read('MainView.qml')
main=replace(main,'            onAbrirIntervalo: lglowIntervalo.abrir()','''            onAbrirIntervalo: lglowIntervalo.abrir()
            onAbrirUbicacion: lglowUbicacion.abrir()
        }

        Text {
            anchors.right: lglowBarra.left
            anchors.rightMargin: styleSheet.getRValue(24)
            anchors.verticalCenter: lglowBarra.verticalCenter
            z: 2
            visible: lglowBarra.visible
            transform: Translate { y: -root.appsShift }
            opacity: lglowBarra.opacity
            text: paraTi.dateText + "   " + paraTi.clock
            color: paraTi.softColor
            font.family: fontManager.smart_Regular.family
            font.pixelSize: styleSheet.getRValue(26)''')
main=replace(main,'return paraTi.config;','return paraTi.weatherConfig;')
main=replace(main,'    // [fullhome-custom] panel rápido','''    LglowUbicacion {
        id: lglowUbicacion
        anchors.fill: parent
        z: 2060
        weather: paraTi
        onCerrado: lglowBarra.forceActiveFocus()
    }

    // [fullhome-custom] panel rápido''')
main=replace(main,'!lglowIntervalo.open;', '!lglowIntervalo.open && !lglowUbicacion.open;')
cards=read('Main/LglowChile.qml')
cards=replace(cards,'        get("https://api.open-meteo.com','        var place=config;\n        get("https://api.open-meteo.com')
cards=replace(cards,'            function(text) {\n                var data=null;', '            function(text) {\n                if(place!==config) return;\n                var data=null;')
cards=replace(cards,'    onConfigChanged: if(allowed) refresh(false)','''    onConfigChanged: {
        refreshed=0;
        temperature="—";
        condition="Cargando clima…";
        range=sun=updated="";
        forecast=[];
        if(allowed) loadWeather();
    }''')
files={'MainView.qml':main,'Main/ParaTi.qml':para,'Main/LglowBarra.qml':bar,'Main/LglowChile.qml':cards}
backup='/var/lib/webosbrew/lglow-salvapantallas-enmarcadas/respaldo-ubicacion'
run(f'mkdir -p {backup}')
for path in files:
    run(f'test -e {backup}/{Path(path).name} || cp -p {base}/{path} {backup}/{Path(path).name}')
icons = Path(__file__).resolve().parents[2] / 'recursos-locales' / 'iconos-y-marco'
assets = {f'Main/clima-{name}.png': (icons / number).read_bytes()
          for name, number in [('viento', '517287.png'), ('humedad', '219816.png'), ('uv', '3084152.png')]}
assets['Main/lglow-ubicacion.png']=(icons/'google-location-icon-16.png').read_bytes()
files['Main/LglowUbicacion.qml']=Path(__file__).with_name('LglowUbicacion.qml').read_text(encoding='utf-8-sig')
for path,data in {**{p:t.encode() for p,t in files.items()},**assets}.items():
    run(f'cat > {base}/{path}.next',data)
run('set -e; '+'; '.join(f'mv {base}/{p}.next {base}/{p}' for p in [*assets,*files]))

