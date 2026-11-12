import sys

if len(sys.argv) != 2:
    raise SystemExit("Uso: python <script> <IP del televisor>")

import subprocess
from pathlib import Path
ssh=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','root@'+sys.argv[1]]
base='/var/lib/webosbrew/fullhomecustom/qml/UserInterfaceLayer/Containers/Main'
def run(cmd, data=None):
    return subprocess.check_output(ssh+[cmd],input=data,timeout=15)
qml=run(f'cat {base}/ParaTi.qml').decode()
def replace(old,new):
    global qml
    assert qml.count(old)==1, old
    qml=qml.replace(old,new)
replace('    property string weatherText: ""','''    property string weatherText: ""
    property string windText: ""
    property string humidityText: ""
    property string uvText: ""''')
replace('current=temperature_2m,weather_code&','current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m,uv_index&')
replace('                root.weatherText = t;','''                root.weatherText = t;
                var current = r.current;
                root.windText = typeof current.wind_speed_10m === "number"
                    ? Math.round(current.wind_speed_10m) + " km/h" : "";
                root.humidityText = typeof current.relative_humidity_2m === "number"
                    ? Math.round(current.relative_humidity_2m) + "%" : "";
                root.uvText = typeof current.uv_index === "number"
                    ? current.uv_index.toFixed(1).replace(".", ",") : "";''')
start=qml.index('    Text {\n        id: info\n')
end=qml.index('    // Títulos',start)
qml=qml[:start]+'''    Row {
        anchors.right: parent.right
        anchors.verticalCenter: tabRow.verticalCenter
        spacing: styleSheet.getRValue(18)

        Text {
            id: info
            anchors.verticalCenter: parent.verticalCenter
            width: Math.min(implicitWidth, Math.max(0,
                root.width - tabRow.x - tabRow.width - metrics.width - 2 * parent.spacing))
            elide: Text.ElideRight
            text: root.dateText + "   " + root.clock + (root.weatherText ? "     " + root.weatherText : "")
            color: root.softColor
            font.family: fontManager.smart_Regular.family
            font.pixelSize: styleSheet.getRValue(26)
        }

        Row {
            id: metrics
            anchors.verticalCenter: parent.verticalCenter
            spacing: styleSheet.getRValue(18)

            Repeater {
                model: [
                    {icon: "clima-viento.png", value: root.windText},
                    {icon: "clima-humedad.png", value: root.humidityText},
                    {icon: "clima-uv.png", value: root.uvText}
                ]

                Row {
                    visible: modelData.value !== ""
                    spacing: styleSheet.getRValue(7)

                    Item {
                        anchors.verticalCenter: parent.verticalCenter
                        width: styleSheet.getRValue(26)
                        height: width

                        Image {
                            id: weatherIcon
                            anchors.fill: parent
                            source: modelData.icon
                            fillMode: Image.PreserveAspectFit
                            visible: false
                        }

                        ColorOverlay {
                            anchors.fill: parent
                            source: weatherIcon
                            color: root.softColor
                        }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: modelData.value
                        color: root.softColor
                        font: info.font
                    }
                }
            }
        }
    }

'''+qml[end:]
assets=dict(zip(('viento','humedad','uv'),('517287','219816','4005899')))
run(f'cp -p {base}/ParaTi.qml {base}/ParaTi.qml.antes-metricas-clima')
for name,number in assets.items():
    run(f'cat > {base}/clima-{name}.png',(Path.home()/'Pictures'/f'{number}.png').read_bytes())
run(f'cat > {base}/ParaTi.qml.next',qml.encode())
run(f'mv {base}/ParaTi.qml.next {base}/ParaTi.qml')
