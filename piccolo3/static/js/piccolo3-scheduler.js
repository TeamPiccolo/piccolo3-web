/*
# Copyright 2019 The Piccolo Team
#
# This file is part of piccolo3-web.
#
# piccolo3-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo3-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with piccolo3-web.  If not, see <http://www.gnu.org/licenses/>.
*////////////////////////////////////////////////////////////////////////

// construct date_time object from time str by using today's date
function date_time(tstr) {
    var date = new Date();

    var hrs = tstr.substring(0,2);
    var min = tstr.substring(3,5);
    var sec = tstr.substring(6,8);
    var offset = tstr.substring(8,13);

    date.setUTCHours(hrs,min,sec);
    return date;
}

var ws_piccolo = new WebSocket('ws://' + document.domain + ':' + location.port + '/piccolo');
ws_piccolo.onmessage = function (event) {
    var data = JSON.parse(event.data);
    if ('status' in data) {
	if (data.status == 'idle')
	    state = 'green';
	else
	    state = 'orange';
	updateStatus(data.status, state);
    }
    if ('timeChanged' in data) {
	updateClocks(data.timeChanged);
    }
    if ('quietTimeEnabled' in data) {
	document.getElementById('enableQ').checked = data.quietTimeEnabled;
    }
    if ('quietStart' in data) {
	qtStart = date_time(data.quietStart);
	$('#quietStart').data("DateTimePicker").date(qtStart);
    }
    if ('quietEnd' in data) {
	qtEnd = date_time(data.quietEnd);
	$('#quietEnd').data("DateTimePicker").date(qtEnd);
    }
};



$('#quietStart').datetimepicker({
    format: 'HH:mm',
    defaultDate: qtStart
});

$('#quietEnd').datetimepicker({
    format: 'HH:mm',
    defaultDate: qtEnd
});


$('#scheduleStart').datetimepicker({
    defaultDate: new Date(),
    format: 'YY/MM/DD HH:mm',
});

$('#scheduleEnd').datetimepicker({
    format: 'YY/MM/DD HH:mm',
    useCurrent: false
});

$('#scheduleButton').on('click', function() {
    //var msg = JSON.stringify(['delay',document.getElementById('delay').value]);
    //ws_piccolo.send(msg);
    var data = {};
    data.run = document.getElementById('run').value;
    data.nsequence = document.getElementById('nseq').value;
    data.auto = document.getElementById('auto').value;
    data.delay = document.getElementById('delay').value;
    data.target = document.getElementById('target').value;
    data.at_time = $('#scheduleStart').data("DateTimePicker").date();
    var interval = document.getElementById('scheduleInterval').value;
    if (interval != "") {
	data.interval= interval;
    }
    var end = $('#scheduleEnd').data("DateTimePicker").date();
    if (end) {
	data.end_time= end;
    }
    var msg = JSON.stringify(['record',data]);
    ws_piccolo.send(msg);
});



$(document).ready(function() {

    document.getElementById('enableQ').checked = qtEnabled;
    
    $('#enableQ').on('change', function() {
	var msg = JSON.stringify(['quietTimeEnabled',this.checked]);
	ws_piccolo.send(msg);
    });

    $('#quietStart').datetimepicker(
	{ format: 'HH:MM' }).on('dp.change', function (e) {
	    var msg = JSON.stringify(['quietTimeStart',
				      [e.date._d.getUTCHours(),
				       e.date._d.getUTCMinutes()]]);
	    ws_piccolo.send(msg);
	}); 
    $('#quietEnd').datetimepicker(
	{ format: 'HH:MM' }).on('dp.change', function (e) {
	    var msg = JSON.stringify(['quietTimeEnd',
				      [e.date._d.getUTCHours(),
				       e.date._d.getUTCMinutes()]]);
	    ws_piccolo.send(msg);
	}); 
    $("#scheduleStart").on("dp.change", function (e) {
        $('#scheduleEnd').data("DateTimePicker").minDate(e.date);
    });
    $("#scheduleEnd").on("dp.change", function (e) {
        $('#scheduleStart').data("DateTimePicker").maxDate(e.date);
    });
    
});
