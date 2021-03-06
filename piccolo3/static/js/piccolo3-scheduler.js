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

function suspend(job) {
    var msg = JSON.stringify(['suspend_job',job]);
    ws_piccolo.send(msg);
}
function unsuspend(job) {
    var msg = JSON.stringify(['unsuspend_job',job]);
    ws_piccolo.send(msg);
}
function remove(job) {
    var msg = JSON.stringify(['delete_job',job]);
    ws_piccolo.send(msg);
}

function display_jobs(jobs) {
    var content = '';
    jobs.forEach(function(job) {
	start = new Date(job[2]).toLocaleString();
	if (job[3] == null)
	    end = '';
	else
	    end = new Date(job[3]).toLocaleString();
	if (job[4] == null)
	    interval = '';
	else
	    interval = job[4];
	content += '<tr>';
	content += '<td>' + job[0] + '</td>';
	content += '<td>' + job[1][0] + '</td>';
	content += '<td>' + start + '</td>';
	content += '<td>' + end + '</td>';
	content += '<td>' + interval + '</td>';
	content += '<td>'
	if (job[5] == 'suspended')
	    content += ' <button type="button" id="pauseButton" class="btn btn-success" onclick="unsuspend('+job[0]+');">Unause</button> '
	else
	    content += ' <button type="button" id="pauseButton" class="btn btn-warning" onclick="suspend('+job[0]+');">Pause</button> '
	content += ' <button type="button" id="stopButton" class="btn btn-danger"  onclick="remove('+job[0]+');">Delete</button> </td>';
	content += '</tr>';
    });
    $('#scheduled-jobs-table tbody').html(content);
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
	document.getElementById('enableP').disabled = !data.quietTimeEnabled;
    }
    if ('powerOffEnabled' in data) {
	document.getElementById('enableP').checked = data.powerOffEnabled;
    }
    if ('power_delay' in data) {
	document.getElementById('delayP').value = data.power_delay;
    }
    if ('quietStart' in data) {
	qtStart = date_time(data.quietStart);
	$('#quietStart').data("DateTimePicker").date(qtStart);
    }
    if ('quietEnd' in data) {
	qtEnd = date_time(data.quietEnd);
	$('#quietEnd').data("DateTimePicker").date(qtEnd);
    }
    if ('jobs' in data) {
	display_jobs(data.jobs);
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
    document.getElementById('enableP').checked = poEnabled;
    document.getElementById('enableP').disabled = !qtEnabled;
    
    $('#enableQ').on('change', function() {
	var msg = JSON.stringify(['quietTimeEnabled',this.checked]);
	$('#enableP').disabled = !this.checked;
	ws_piccolo.send(msg);
    });

    $('#enableP').on('change', function() {
	var msg = JSON.stringify(['powerOffEnabled',this.checked]);
	ws_piccolo.send(msg);
    });

    $('#delayP').on('change', function() {
	var msg = JSON.stringify(['powerDelay',this.value]);
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

    $.ajax({
	url: "jobs",
	cache: false,
	dataType: "json",
	success: function(data) {
	    display_jobs(data);
	},
	error: function (request, status, error) { console.log(status + ", " + error); }
    });
    
});
