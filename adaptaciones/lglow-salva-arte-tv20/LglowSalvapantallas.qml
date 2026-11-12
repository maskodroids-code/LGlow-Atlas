import QtQuick 2.6
import WebOSServices 1.0

// Protector local: coordina la solicitud de LG solo mientras esta visible.
FocusScope {
    id: saver
    anchors.fill: parent
    z: 10000

    property var windowController: null
    property bool allowed: false
    property int timeoutMs: 300000
    property var recommendations: []
    readonly property var localImages: [{"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-01.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-02.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-03.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-04.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-05.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-06.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-07.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-08.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-09.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-10.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-11.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-12.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-13.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-14.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-15.jpg"}, {"title": "", "backdrop": "file:///var/lib/webosbrew/lglow-salva-prueba-tv20/imagenes/arte-16.jpg"}]
    property string fallbackImage: ""
    property bool showing: false
    property int slideIndex: 0
    property int clockPosition: 0
    property string clockText: ""
    property string dateText: ""
    property var displayedPick: ({})
    property var pendingPick: ({})
    property int frontLayer: -1
    property int waitingForLayer: -1
    property int requestedIndex: 0
    readonly property var currentPick: displayedPick
    signal cerrado()

    visible: showing && allowed
    enabled: visible
    focus: showing && allowed

    // La suscripcion desaparece al cerrar el protector o salir del home.
    // No modifica ajustes persistentes ni simula pulsaciones del control.
    Loader {
        id: powerGuard
        active: saver.showing && saver.allowed
        sourceComponent: Component {
            Service {
                appId: rootWindow.appId
                Component.onCompleted: call("luna://com.webos.service.tvpower/",
                    "power/registerScreenSaverRequest",
                    JSON.stringify({clientName: "lglow.home.saver", subscribe: true}))
                Component.onDestruction: cancel()
                onCallSuccess: {
                    var r = response;
                    if (typeof r === "string") {
                        try { r = JSON.parse(r); } catch (e) { return; }
                    }
                    if (!r || r.timestamp === undefined) return;
                    var reply = powerReply.createObject(saver);
                    reply.call("luna://com.webos.service.tvpower/",
                        "power/responseScreenSaverRequest", JSON.stringify({
                            clientName: "lglow.home.saver",
                            ack: !(saver.showing && saver.allowed),
                            timestamp: r.timestamp
                        }));
                }
                onCallFailure: console.log("[lglow-salva] LG no acepto la suscripcion")
                onError: console.log("[lglow-salva] error de suscripcion a LG")
            }
        }
    }

    Component {
        id: powerReply
        Service {
            appId: rootWindow.appId
            onCallSuccess: destroy()
            onCallFailure: { console.log("[lglow-salva] LG rechazo la respuesta"); destroy(); }
            onError: { console.log("[lglow-salva] error al responder a LG"); destroy(); }
        }
    }

    function updateClock() {
        var now = new Date();
        clockText = Qt.formatTime(now, "HH:mm");
        var days = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
        var months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
        dateText = days[now.getDay()] + ", " + now.getDate() + " de "
                 + months[now.getMonth()] + " de " + now.getFullYear();
    }

    function clearSlides() {
        dissolve.stop();
        waitingForLayer = -1;
        frontLayer = -1;
        layerA.opacity = 0;
        layerB.opacity = 0;
        layerA.source = "";
        layerB.source = "";
        displayedPick = ({});
        pendingPick = ({});
    }

    function requestSlide(index) {
        if (!showing || dissolve.running || waitingForLayer >= 0
                || !localImages || !localImages.length)
            return;
        requestedIndex = index % localImages.length;
        pendingPick = localImages[requestedIndex];
        if (!pendingPick || !pendingPick.backdrop)
            return;
        waitingForLayer = frontLayer === 0 ? 1 : 0;
        var image = waitingForLayer === 0 ? layerA : layerB;
        image.opacity = 0;
        image.source = pendingPick.backdrop;
        // Una imagen ya decodificada puede no emitir un cambio de estado.
        slideReady(waitingForLayer);
    }

    function slideReady(slot) {
        if (!showing || waitingForLayer !== slot || dissolve.running)
            return;
        var image = slot === 0 ? layerA : layerB;
        if (image.status === Image.Error) {
            waitingForLayer = -1;
            console.log("[lglow-salva] imagen no disponible; se conserva el fondo anterior");
            return;
        }
        if (image.status !== Image.Ready)
            return;
        // La imagen anterior permanece opaca debajo de la nueva durante la
        // disolucion. No se cambia su source ni se pasa por negro entre fotos.
        layerA.z = slot === 0 ? 2 : 1;
        layerB.z = slot === 1 ? 2 : 1;
        image.opacity = 0;
        displayedPick = pendingPick;
        slideIndex = requestedIndex;
        dissolve.target = image;
        dissolve.restart();
    }

    function resetIdle() {
        if (allowed && !showing)
            idle.restart();
    }

    function dismiss(restoreFocus) {
        var wasShowing = showing;
        showing = false;
        clearSlides();
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
        clearSlides();
        clockPosition = (clockPosition + 1) % 4;
        updateClock();
        showing = true;
        requestSlide(0);
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
            saver.requestSlide(saver.slideIndex + 1);
            saver.clockPosition = (saver.clockPosition + 1) % 4;
        }
    }

    NumberAnimation {
        id: dissolve
        property: "opacity"
        from: 0
        to: 1
        duration: 1800
        easing.type: Easing.InOutSine
        onStopped: {
            // stopped existe en QtQuick 2.6; finished requiere la revision 2.12.
            // Una cancelacion al cerrar no debe completar el cambio de imagen.
            if (!saver.showing || saver.waitingForLayer < 0
                    || !target || target.opacity < 0.999)
                return;
            var previous = saver.frontLayer;
            saver.frontLayer = saver.waitingForLayer;
            saver.waitingForLayer = -1;
            if (previous === 0) layerA.opacity = 0;
            if (previous === 1) layerB.opacity = 0;
        }
    }

    Timer {
        interval: 15000
        running: saver.waitingForLayer >= 0 && !dissolve.running && saver.showing
        repeat: false
        onTriggered: {
            saver.waitingForLayer = -1;
            console.log("[lglow-salva] tiempo de carga agotado; se conserva el fondo anterior");
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
        id: layerA
        anchors.fill: parent
        source: ""
        fillMode: Image.PreserveAspectCrop
        sourceSize: Qt.size(1920, 1080)
        asynchronous: true
        cache: false
        opacity: 0
        onStatusChanged: saver.slideReady(0)
    }

    Image {
        id: layerB
        anchors.fill: parent
        source: ""
        fillMode: Image.PreserveAspectCrop
        sourceSize: Qt.size(1920, 1080)
        asynchronous: true
        cache: false
        opacity: 0
        onStatusChanged: saver.slideReady(1)
    }

    Rectangle {
        anchors.fill: parent
        z: 3
        color: "#000000"
        opacity: 0.48
    }

    Column {
        z: 4
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
            text: ""
            color: "#FFFFFF"
            font.family: "LG Smart UI"
            font.pixelSize: saver.height * 0.034
            wrapMode: Text.WordWrap
            maximumLineCount: 2
            elide: Text.ElideRight
        }
    }

    Text {
        z: 4
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: saver.height * 0.055
        text: "Pulsa una tecla para volver"
        color: "#D5D5DE"
        font.family: "LG Smart UI"
        font.pixelSize: saver.height * 0.023
    }

    MouseArea {
        z: 5
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
