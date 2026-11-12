import QtQuick 2.6
import "Indicadores.js" as Indicators

FocusScope {
    id: root
    property var config: ({})
    property bool allowed: false
    property int selectedCard: 0
    property string temperature: "—"
    property string condition: "Cargando clima…"
    property string range: ""
    property string sun: ""
    property var forecast: []
    property var values: ({})
    property var pending: []
    property double refreshed: 0
    property string updated: ""
    signal volverApps()
    height: styleSheet.getRValue(360)

    function icon(code) { return code===0 ? "☀" : code<=3 ? "☁" : code<=48 ? "≋" : code<=67 ? "☂" : code<=77 ? "❄" : "☂"; }
    function weatherName(code) {
        if(code===0) return "Despejado";
        if(code<=2) return "Parcialmente nublado";
        if(code===3) return "Nublado";
        if(code<=48) return "Neblina";
        if(code<=57) return "Llovizna";
        if(code<=67) return "Lluvia";
        if(code<=77) return "Nieve";
        if(code<=82) return "Chubascos";
        return "Tormenta";
    }
    function get(url, callback) {
        var request=new XMLHttpRequest();
        pending.push({request:request,start:Date.now()});
        request.onreadystatechange=function() {
            if(request.readyState!==XMLHttpRequest.DONE) return;
            for(var i=pending.length-1;i>=0;i--) if(pending[i].request===request) pending.splice(i,1);
            if(request.status!==200 || request.responseText.length>2000000) { callback(null); return; }
            callback(request.responseText);
        };
        request.open("GET",url);
        request.send();
    }
    function put(key,value,date) {
        var next={};
        for(var k in values) next[k]=values[k];
        next[key]={value:value,date:date};
        values=next;
    }
    function unavailable(key) { put(key,"No disponible","Consulta sin datos"); }
    function loadWeather() {
        if(config.latitude===undefined || config.longitude===undefined) { condition="Falta ubicacion en config.json"; return; }
        get("https://api.open-meteo.com/v1/forecast?latitude="+encodeURIComponent(config.latitude)+"&longitude="+encodeURIComponent(config.longitude)
            +"&current=temperature_2m,weather_code&hourly=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset&timezone=auto&forecast_days=2",
            function(text) {
                var data=null;
                try { data=JSON.parse(text); } catch(e) {}
                if(!data || !data.current || !data.daily || !data.hourly) { condition="Clima no disponible"; return; }
                temperature=Math.round(data.current.temperature_2m)+"°C";
                condition=weatherName(data.current.weather_code);
                range="Max. "+Math.round(data.daily.temperature_2m_max[0])+"°  /  Min. "+Math.round(data.daily.temperature_2m_min[0])+"°";
                sun="Amanecer "+data.daily.sunrise[0].slice(11,16)+"   ·   Atardecer "+data.daily.sunset[0].slice(11,16);
                var upcoming=[];
                for(var i=0;i<data.hourly.time.length && upcoming.length<6;i++)
                    if(data.hourly.time[i]>=data.current.time.slice(0,13)+":00") upcoming.push({hour:data.hourly.time[i].slice(11,16),icon:icon(data.hourly.weather_code[i]),temp:Math.round(data.hourly.temperature_2m[i])+"°"});
                forecast=upcoming;
                updated=data.current.time.slice(0,10)+" "+data.current.time.slice(11,16);
            });
    }
    function loadIndicators() {
        var now=new Date(), year=now.getFullYear();
        get("https://www.sii.cl/valores_y_fechas/uf/uf"+year+".htm",function(text) {
            var d=text ? Indicators.uf(text,now) : null;
            if(d) put("uf",Indicators.money(d.value,2),d.date); else unavailable("uf");
        });
        get("https://www.sii.cl/valores_y_fechas/utm/utm"+year+".htm",function(text) {
            var d=text ? Indicators.tax(text,now) : null;
            if(d && d.current && d.current.utm>0) put("utm",Indicators.money(d.current.utm,0),d.current.date); else unavailable("utm");
            if(d && d.current && d.current.uta>0) put("uta",Indicators.money(d.current.uta,0),d.current.date); else unavailable("uta");
            if(d && d.ipc) put("ipc",d.ipc.monthly.toFixed(1).replace('.',',')+" % mensual",d.ipc.date+" · "+d.ipc.annual.toFixed(1).replace('.',',')+" % anual"); else unavailable("ipc");
        });
        get("https://currencylive.com/es/exchange-rate/usd-to-clp-exchange-rate-today/",function(text) {
            var d=text ? Indicators.dollar(text) : null;
            if(d) put("usd",Indicators.money(d.value,2),d.date); else unavailable("usd");
        });
        get("https://si3.bcentral.cl/indicadoressiete/secure/Serie.aspx?gcode=PRE_EUR&param=cgBnAE8AOQBlAGcAIwBiAFUALQBsAEcAYgBOAEkASQBCAEcAegBFAFkAeABkADgASAA2AG8AdgB2AFMAUgBYADIAQwBzAEEARQBMAG8ASgBWADQATABrAGQAZAB1ADIAeQBBAFAAZwBhADIAbABWAHcAXwBXAGgATAAkAFIAVAB1AEIAbAB3AFoAdQBRAFgAZwA5AHgAdgAwACQATwBZADcAMwAuAGIARwBFAFIASwAuAHQA",function(text) {
            var d=text ? Indicators.euro(text,now) : null;
            if(d) put("eur",Indicators.money(d.value,2),d.date); else unavailable("eur");
        });
    }
    function refresh(force) {
        if(!allowed || pending.length || config.latitude===undefined) return;
        if(force || Date.now()-refreshed>1800000) {
            refreshed=Date.now(); loadWeather(); loadIndicators();
        }
    }
    onAllowedChanged: if(allowed) refresh(false)
    onConfigChanged: if(allowed) refresh(false)
    Timer { interval: 60000; running: root.allowed; repeat:true; onTriggered: root.refresh(false) }
    Timer {
        interval: 1000; running: root.allowed; repeat:true
        onTriggered: {
            // Un array JS no notifica cambios de length: este temporizador se
            // mantiene activo mientras el componente esta permitido.
            for(var i=root.pending.length-1;i>=0;i--)
                if(Date.now()-root.pending[i].start>20000) root.pending[i].request.abort();
        }
    }
    Keys.onPressed: {
        if(event.key===Qt.Key_Left || event.key===Qt.Key_Right) { selectedCard=1-selectedCard; event.accepted=true; }
        else if(event.key===Qt.Key_Up) { root.volverApps(); event.accepted=true; }
        else if(event.key===Qt.Key_Return || event.key===Qt.Key_Enter) { refresh(true); event.accepted=true; }
        else if(event.key===Qt.Key_Down || event.key===Qt.Key_Back || event.key===Qt.Key_Escape || event.key===18874371) event.accepted=true;
    }
    Keys.onReleased: {
        if(event.key===Qt.Key_Back || event.key===Qt.Key_Escape || event.key===18874371) { event.accepted=true; root.volverApps(); }
    }
    Row {
        anchors.fill: parent
        spacing: styleSheet.getRValue(32)
        Rectangle {
            width:(root.width-parent.spacing)/2; height:root.height
            radius:styleSheet.getRValue(28)
            color:lglowTema.repisa
            border.color:root.activeFocus && selectedCard===0 ? lglowTema.texto : lglowTema.repisaBorde
            border.width:styleSheet.getRValue(root.activeFocus && selectedCard===0 ? 3 : 1)
            Column {
                anchors.fill:parent; anchors.margins:styleSheet.getRValue(24)
                spacing:styleSheet.getRValue(10)
                Text { text:"Clima · "+(root.config.city || "Ubicacion configurada"); color:lglowTema.textoSuave; font.pixelSize:styleSheet.getRValue(25) }
                Row {
                    spacing:styleSheet.getRValue(22)
                    Text { text:root.temperature; color:lglowTema.texto; font.pixelSize:styleSheet.getRValue(60) }
                    Column {
                        anchors.verticalCenter:parent.verticalCenter; spacing:styleSheet.getRValue(6)
                        Text { text:root.condition; color:lglowTema.texto; font.pixelSize:styleSheet.getRValue(22) }
                        Text { text:root.range; color:lglowTema.textoSuave; font.pixelSize:styleSheet.getRValue(20) }
                    }
                }
                Row {
                    spacing:styleSheet.getRValue(23)
                    Repeater {
                        model:root.forecast
                        Column {
                            width:styleSheet.getRValue(98); spacing:styleSheet.getRValue(3)
                            Text { text:modelData.hour; color:lglowTema.textoSuave; font.pixelSize:styleSheet.getRValue(18) }
                            Text { text:modelData.icon; color:lglowTema.texto; font.pixelSize:styleSheet.getRValue(28) }
                            Text { text:modelData.temp; color:lglowTema.texto; font.pixelSize:styleSheet.getRValue(23) }
                        }
                    }
                }
                Text { text:root.sun; color:lglowTema.textoSuave; font.pixelSize:styleSheet.getRValue(19) }
                Text { text:"Open-Meteo · "+root.updated; color:lglowTema.textoSuave; font.pixelSize:styleSheet.getRValue(16) }
            }
            MouseArea { anchors.fill:parent; onClicked:{ root.selectedCard=0; root.forceActiveFocus(); } }
        }
        Rectangle {
            width:(root.width-parent.spacing)/2; height:root.height
            radius:styleSheet.getRValue(28); color:lglowTema.repisa
            border.color:root.activeFocus && selectedCard===1 ? lglowTema.texto : lglowTema.repisaBorde
            border.width:styleSheet.getRValue(root.activeFocus && selectedCard===1 ? 3 : 1)
            Column {
                anchors.fill:parent; anchors.margins:styleSheet.getRValue(24)
                spacing:styleSheet.getRValue(12)
                Text { text:"Indicadores de Chile"; color:lglowTema.texto; font.pixelSize:styleSheet.getRValue(27) }
                Grid {
                    columns:2; columnSpacing:styleSheet.getRValue(20); rowSpacing:styleSheet.getRValue(12)
                    Repeater {
                        model:[{id:"usd",label:"Dolar · CLP por USD"},{id:"eur",label:"Euro · CLP por EUR"},{id:"uf",label:"UF diaria"},{id:"utm",label:"UTM"},{id:"uta",label:"UTA"},{id:"ipc",label:"IPC · ultimo publicado"}]
                        Column {
                            width:styleSheet.getRValue(360); spacing:styleSheet.getRValue(3)
                            property var datum: root.values[modelData.id] || ({value:"Cargando…",date:""})
                            Text { text:modelData.label; color:lglowTema.textoSuave; font.pixelSize:styleSheet.getRValue(18) }
                            Text { text:parent.datum.value; color:lglowTema.texto; font.pixelSize:styleSheet.getRValue(26) }
                            Text { text:parent.datum.date; color:lglowTema.textoSuave; font.pixelSize:styleSheet.getRValue(15); width:parent.width; elide:Text.ElideRight }
                        }
                    }
                }
                Text { text:"Fuentes: CurrencyLive · Banco Central · SII"; color:lglowTema.textoSuave; font.pixelSize:styleSheet.getRValue(16) }
            }
            MouseArea { anchors.fill:parent; onClicked:{ root.selectedCard=1; root.forceActiveFocus(); } }
        }
    }
    Component.onDestruction: { for(var i=pending.length-1;i>=0;i--) pending[i].request.abort(); }
}
