import QtQuick 2.6

// Protector local del home. No cambia el protector ni el compositor de LG.
FocusScope {
    id: saver
    anchors.fill: parent
    z: 10000

    property var windowController: null
    property bool allowed: false
    property int timeoutMs: 300000
    property var recommendations: []
    property string fallbackImage: ""
    property bool showing: false
    property int slideIndex: 0
    property int clockPosition: 0
    property string clockText: ""
    property string dateText: ""
    readonly property var currentPick: recommendations && recommendations.length
                                       ? recommendations[slideIndex % recommendations.length] : ({})
    signal cerrado()

    visible: showing && allowed
    enabled: visible
    focus: showing && allowed

    function updateClock() {
        var now = new Date();
        clockText = Qt.formatTime(now, "HH:mm");
        dateText = Qt.formatDate(now, "dddd d MMMM yyyy");
    }

    function resetIdle() {
        if (allowed && !showing)
            idle.restart();
    }

    function dismiss(restoreFocus) {
        var wasShowing = showing;
        showing = false;
        resetIdle();
        if (wasShowing && restoreFocus)
            restore.restart();
    }

    function openSaver() {
        if (!allowed || (windowController && windowController.cursorVisible)) {
            resetIdle();
            return;
        }
        slideIndex = 0;
        clockPosition = (clockPosition + 1) % 4;
        updateClock();
        showing = true;
        forceActiveFocus();
        console.log("[lglow-salva] abierto");
    }

    onAllowedChanged: {
        if (!allowed) {
            idle.stop();
            restore.stop();
            dismiss(false);
        } else {
            resetIdle();
        }
    }

    Connections {
        target: saver.windowController
        onFivewayKeyEvent: {
            // El evento de Qt se consume abajo si el protector tiene el foco.
            if (!saver.showing)
                saver.resetIdle();
        }
        onCursorVisibleChanged: {
            if (saver.windowController && saver.windowController.cursorVisible) {
                if (saver.showing)
                    saver.dismiss(true);
                else
                    saver.resetIdle();
            }
        }
    }

    Timer {
        id: idle
        interval: saver.timeoutMs
        running: saver.allowed && !saver.showing
        repeat: false
        onTriggered: saver.openSaver()
    }

    // El puntero nativo se oculta tras la inactividad. Mientras siga visible,
    // posponemos el protector, sin superponer una MouseArea sobre el home normal.
    Timer {
        interval: 1000
        running: saver.allowed && !saver.showing
        repeat: true
        onTriggered: {
            if (saver.windowController && saver.windowController.cursorVisible)
                saver.resetIdle();
        }
    }

    Timer {
        id: restore
        interval: 0
        onTriggered: if (saver.allowed) saver.cerrado()
    }

    Timer {
        interval: 1000
        repeat: true
        running: saver.visible
        onTriggered: saver.updateClock()
    }

    Timer {
        interval: 25000
        repeat: true
        running: saver.visible
        onTriggered: {
            saver.slideIndex++;
            saver.clockPosition = (saver.clockPosition + 1) % 4;
        }
    }

    Keys.priority: Keys.BeforeItem
    Keys.onPressed: {
        // La primera pulsacion solo despierta: no abre apps ni cambia ajustes.
        event.accepted = true;
    }
    Keys.onReleased: {
        event.accepted = true;
        saver.dismiss(true);
    }

    Rectangle { anchors.fill: parent; color: "#080B12" }

    Image {
        anchors.fill: parent
        source: saver.showing ? saver.fallbackImage : ""
        fillMode: Image.PreserveAspectCrop
        sourceSize: Qt.size(1920, 1080)
        asynchronous: true
        cache: false
    }

    Image {
        id: poster
        anchors.fill: parent
        source: saver.showing && saver.currentPick.backdrop ? saver.currentPick.backdrop : ""
        fillMode: Image.PreserveAspectCrop
        sourceSize: Qt.size(1920, 1080)
        asynchronous: true
        cache: false
        visible: status === Image.Ready
        opacity: 0.85
    }

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.48
    }

    Column {
        x: saver.width * (saver.clockPosition % 2 ? 0.55 : 0.07)
        y: saver.height * (saver.clockPosition >= 2 ? 0.57 : 0.10)
        width: saver.width * 0.38
        spacing: saver.height * 0.012

        Text {
            text: saver.clockText
            color: "#FFFFFF"
            font.family: "LG Smart UI"
            font.pixelSize: saver.height * 0.115
            font.weight: Font.Light
        }
        Text {
            width: parent.width
            text: saver.dateText
            color: "#EEEEF2"
            font.family: "LG Smart UI"
            font.pixelSize: saver.height * 0.028
            wrapMode: Text.WordWrap
        }
        Text {
            width: parent.width
            text: saver.currentPick.title || "LGlow"
            color: "#FFFFFF"
            font.family: "LG Smart UI"
            font.pixelSize: saver.height * 0.034
            wrapMode: Text.WordWrap
            maximumLineCount: 2
            elide: Text.ElideRight
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: saver.height * 0.055
        text: "Pulsa una tecla para volver"
        color: "#D5D5DE"
        font.family: "LG Smart UI"
        font.pixelSize: saver.height * 0.023
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.AllButtons
        onPositionChanged: if (saver.showing) saver.dismiss(true)
        onPressed: mouse.accepted = true
        onReleased: saver.dismiss(true)
        onWheel: { wheel.accepted = true; saver.dismiss(true); }
    }

    Component.onCompleted: {
        updateClock();
        resetIdle();
    }
}
