import QtQuick 2.7

FocusScope {
    id: dialog
    property bool open: false
    property var weather
    property string message: ""
    property int searchId: 0
    signal cerrado()
    visible: open

    function abrir() {
        input.text = weather.weatherConfig.city || "";
        results.model = [];
        message = "";
        open = true;
        input.forceActiveFocus();
        input.selectAll();
        Qt.inputMethod.show();
    }

    function cerrar() {
        if (!open) return;
        searchId++;
        Qt.inputMethod.hide();
        open = false;
        cerrado();
    }

    function buscar() {
        var query = input.text.trim();
        var id = ++searchId;
        results.model = [];
        if (query.length < 2) {
            message = "Escribe el nombre de una ciudad.";
            return;
        }
        message = "Buscando…";
        Qt.inputMethod.hide();
        weather.get("https://geocoding-api.open-meteo.com/v1/search?count=5&language=es&name=" +
                    encodeURIComponent(query), function(data) {
            if (!open || id !== searchId) return;
            var matches = data && data.results || [];
            results.model = matches;
            message = matches.length ? "" : data ? "No se encontraron ciudades." : "No se pudo buscar. Intenta de nuevo.";
            if (matches.length) {
                results.currentIndex = 0;
                results.forceActiveFocus();
            }
        });
    }

    function elegir(place) {
        if (weather.saveLocation(place)) cerrar();
        else message = "No se pudo guardar la ubicación.";
    }

    function esAtras(key) {
        return key === Qt.Key_Back || key === Qt.Key_Escape || key === 18874371
            || key === uiController.webOS.Key_webOS_Back;
    }

    Keys.onPressed: if (esAtras(event.key)) event.accepted = true
    Keys.onReleased: if (esAtras(event.key)) {
        event.accepted = true;
        cerrar();
    }

    Connections {
        target: uiController
        onHomeShownChanged: if (!uiController.homeShown) dialog.cerrar()
    }
    Connections {
        target: systemProperties
        onIsAppForegroundChanged: if (!systemProperties.isAppForeground) dialog.cerrar()
    }

    Rectangle {
        anchors.fill: parent
        color: lglowTema.velo
        MouseArea { anchors.fill: parent; onClicked: dialog.cerrar() }
    }

    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: styleSheet.getRValue(95)
        width: Math.min(parent.width * 0.9, styleSheet.getRValue(820))
        height: content.height + styleSheet.getRValue(56)
        radius: styleSheet.getRValue(22)
        color: lglowTema.tarjeta
        MouseArea { anchors.fill: parent }

        Column {
            id: content
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: styleSheet.getRValue(28)
            width: parent.width - styleSheet.getRValue(56)
            spacing: styleSheet.getRValue(14)

            Text {
                text: "Ubicación del clima"
                color: lglowTema.texto
                font.pixelSize: styleSheet.getRValue(36)
            }
            Text {
                text: "Escribe una ciudad y pulsa OK para buscar."
                color: lglowTema.textoSuave
                font.pixelSize: styleSheet.getRValue(25)
            }
            Rectangle {
                width: parent.width
                height: styleSheet.getRValue(60)
                radius: styleSheet.getRValue(8)
                color: lglowTema.pastilla
                border.color: input.activeFocus ? lglowTema.texto : lglowTema.repisaBorde

                TextInput {
                    id: input
                    property bool screenKeyboardVisible: Qt.inputMethod.visible
                    anchors.fill: parent
                    anchors.margins: styleSheet.getRValue(10)
                    verticalAlignment: TextInput.AlignVCenter
                    color: lglowTema.texto
                    selectionColor: lglowTema.texto
                    selectedTextColor: lglowTema.tarjeta
                    font.pixelSize: styleSheet.getRValue(30)
                    maximumLength: 100
                    clip: true
                    EnterKey.type: Qt.EnterKeySearch
                    onAccepted: dialog.buscar()
                    KeyNavigation.down: searchButton
                    Keys.onPressed: {
                        if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter)
                                && !Qt.inputMethod.visible) {
                            dialog.buscar();
                            event.accepted = true;
                        }
                    }
                }
            }

            Rectangle {
                id: searchButton
                width: styleSheet.getRValue(180)
                height: styleSheet.getRValue(52)
                radius: styleSheet.getRValue(8)
                color: activeFocus ? lglowTema.texto : lglowTema.pastilla
                KeyNavigation.up: input
                KeyNavigation.down: results.count ? results : input
                Keys.onReturnPressed: dialog.buscar()
                Keys.onEnterPressed: dialog.buscar()
                Text {
                    anchors.centerIn: parent
                    text: "Buscar"
                    color: searchButton.activeFocus ? lglowTema.tarjeta : lglowTema.texto
                    font.pixelSize: styleSheet.getRValue(26)
                }
                MouseArea { anchors.fill: parent; onClicked: dialog.buscar() }
            }

            Text {
                visible: !!dialog.message
                text: dialog.message
                color: lglowTema.textoSuave
                font.pixelSize: styleSheet.getRValue(24)
            }

            ListView {
                id: results
                width: parent.width
                height: count * styleSheet.getRValue(54)
                clip: true
                interactive: false
                model: []
                Keys.onUpPressed: {
                    if (currentIndex <= 0) searchButton.forceActiveFocus();
                    else decrementCurrentIndex();
                }
                Keys.onDownPressed: if (currentIndex < count - 1) incrementCurrentIndex()
                Keys.onReturnPressed: if (currentIndex >= 0) dialog.elegir(model[currentIndex])
                Keys.onEnterPressed: if (currentIndex >= 0) dialog.elegir(model[currentIndex])

                delegate: Rectangle {
                    width: results.width
                    height: styleSheet.getRValue(54)
                    radius: styleSheet.getRValue(8)
                    property bool selected: ListView.isCurrentItem && results.activeFocus
                    color: selected ? lglowTema.texto : "transparent"
                    Text {
                        anchors.fill: parent
                        anchors.leftMargin: styleSheet.getRValue(12)
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        text: [modelData.name, modelData.admin1, modelData.country].filter(function(s) {
                            return !!s;
                        }).join(", ")
                        color: parent.selected ? lglowTema.tarjeta : lglowTema.texto
                        font.pixelSize: styleSheet.getRValue(26)
                    }
                    MouseArea { anchors.fill: parent; onClicked: dialog.elegir(modelData) }
                }
            }
        }
    }
}
