// Lectores conservadores: nunca convierten una celda vacia en cero.
var months = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
function clean(s) { return String(s || '').replace(/<[^>]*>/g,' ').replace(/&nbsp;|&#160;/gi,' ').replace(/&[a-z0-9#]+;/gi,' ').replace(/\s+/g,' ').trim(); }
function numberCL(s) {
    s = clean(s);
    if (!/^-?[\d.]+(?:,\d+)?$/.test(s)) return null;
    var n = Number(s.replace(/\./g,'').replace(',','.'));
    return isFinite(n) ? n : null;
}
function rows(html) {
    var out=[], row, cell, re=/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi;
    while ((row=re.exec(html))) {
        var cells=[], cr=/<t[dh]\b[^>]*>([\s\S]*?)<\/t[dh]>/gi;
        while ((cell=cr.exec(row[1]))) cells.push(clean(cell[1]));
        out.push(cells);
    }
    return out;
}
function money(n, decimals) {
    if (n === null || n === undefined || !isFinite(n)) return 'No disponible';
    var parts=Number(n).toFixed(decimals).split('.');
    // Evita reemplazos de ancho cero: Qt/QV4 antiguo puede insertar dos puntos.
    var digits=parts[0], grouped='';
    while(digits.length>3) { grouped='.'+digits.slice(-3)+grouped; digits=digits.slice(0,-3); }
    parts[0]=digits+grouped;
    return '$ '+parts[0]+(parts.length>1 ? ','+parts[1] : '');
}
function stamp(d) { return ('0'+d.getDate()).slice(-2)+'/'+('0'+(d.getMonth()+1)).slice(-2)+'/'+d.getFullYear(); }
function uf(html, date) {
    var month=months[date.getMonth()], section=new RegExp("id=['\"]mes_"+month+"['\"][\\s\\S]*?<table\\b[^>]*>([\\s\\S]*?)</table>",'i').exec(html);
    if (!section || !new RegExp('UF\\s*'+date.getFullYear(),'i').test(clean(html))) return null;
    var rr=rows(section[1]);
    for (var i=0;i<rr.length;i++) for (var j=0;j+1<rr[i].length;j+=2)
        if (Number(rr[i][j])===date.getDate()) {
            var value=numberCL(rr[i][j+1]);
            return value>0 ? {value:value,date:stamp(date)} : null;
        }
    return null;
}
function tax(html,date) {
    if (clean(html).indexOf('UTM - UTA - IPC '+date.getFullYear())<0) return null;
    var rr=rows(html), current=null, ipc=null;
    for(var i=0;i<rr.length;i++) {
        var month=months.indexOf((rr[i][0]||'').toLowerCase());
        if(month<0 || month>date.getMonth() || rr[i].length!==7) continue;
        if(month===date.getMonth()) current={utm:numberCL(rr[i][1]),uta:numberCL(rr[i][2]),date:months[month]+' '+date.getFullYear()};
        if(numberCL(rr[i][3])!==null && numberCL(rr[i][4])!==null)
            ipc={index:numberCL(rr[i][3]),monthly:numberCL(rr[i][4]),annual:numberCL(rr[i][6]),date:months[month]+' '+date.getFullYear()};
    }
    return {current:current,ipc:ipc};
}
function dollar(html) {
    var flat=clean(html), rate=/1 USD\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*CLP/.exec(flat);
    var when=/actualizaci[^:]{0,25}:\s*([A-Za-z]{3}\s+\d{1,2},\s*\d{4}\s+\d\d:\d\d\s+GMT)/i.exec(flat);
    if(!rate || !when) return null;
    // Qt antiguo no siempre reconoce fechas inglesas mediante Date.parse.
    var fields=/([A-Za-z]{3})\s+(\d{1,2}),\s*(\d{4})\s+(\d\d):(\d\d)\s+GMT/.exec(when[1]);
    var monthNames=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'];
    var month=monthNames.indexOf(fields[1].toLowerCase());
    if(month<0 || Number(fields[4])>23 || Number(fields[5])>59) return null;
    var dt=new Date(Date.UTC(Number(fields[3]),month,Number(fields[2]),Number(fields[4]),Number(fields[5])));
    if(dt.getUTCMonth()!==month || dt.getUTCDate()!==Number(fields[2])) return null;
    var n=Number(rate[1]);
    return n>0 ? {value:n,date:when[1]} : null;
}
function euro(html,date) {
    if(!/Euro\s*\(Pesos por Euro\)/i.test(clean(html)) || clean(html).indexOf('Año '+date.getFullYear())<0) return null;
    var rr=rows(html), found=null;
    for(var i=0;i<rr.length;i++) {
        if(rr[i].length!==13 || !/^\d{1,2}$/.test(rr[i][0])) continue;
        var day=Number(rr[i][0]);
        for(var month=0;month<=date.getMonth();month++) {
            var dt=new Date(date.getFullYear(),month,day,12);
            if(dt.getMonth()!==month || month===date.getMonth() && day>date.getDate()) continue;
            var n=numberCL(rr[i][month+1]);
            if(n>0 && (!found || dt>found.when)) found={value:n,date:stamp(dt),when:dt};
        }
    }
    return found;
}
