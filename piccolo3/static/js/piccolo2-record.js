/*
# Copyright 2018 The Piccolo Team
#
# This file is part of piccolo2-web.
#
# piccolo2-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo2-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with piccolo2-web.  If not, see <http://www.gnu.org/licenses/>.
*////////////////////////////////////////////////////////////////////////



/* Queries piccolo info, the params determine which info will be updated

params:
status - boolean, status will be updated
clock - boolean, clock will be updated
record - boolean, integration values will be updated

*/
function getInfo(status, clock){
    $.ajax({
    url: "info?sysinfo=0",
    cache: false,
    dataType: "json",
    success: function(data) {
      if(status){
        updateStatus(data.status, data.state);
        updateTableFooter(data.status, data.state);
        updateEditable(data.state=='green');
      }
      if(clock){
        updateClocks(data.clock);
      }
    },
    error: function (request, status, error) { console.log(status + ", " + error); }
  });
}



/* Times ------------------------------------------------------------------ */
var date = new Date(piccoloTime)
date.setSeconds(date.getSeconds()+1) // add one to sychronise

//piccolo time html elements
var phours = document.getElementById('phours');
var pmins = document.getElementById('pmin');
var psecs = document.getElementById('psec');
//local time html elements
var lhours = document.getElementById('lhours');
var lmins = document.getElementById('lmin');
var lsecs = document.getElementById('lsec');

//set interval to display new time every second
var timer = setInterval(displayTime, 1000);

//websocket used to exchange integration times
var ws = new WebSocket('ws://' + document.domain + ':' + location.port + '/spectrometers');
ws.onmessage = function (evenet) {
    var data = JSON.parse(event.data);
    var spec = data[0];
    var key = data[1];
    var value = data[2];
    var idx = spec + '-' + key
    var cell = document.getElementById(idx);
    cell.innerHTML = value;
};

var ws_piccolo = new WebSocket('ws://' + document.domain + ':' + location.port + '/piccolo');
ws_piccolo.onmessage = function (event) {
    var data = JSON.parse(event.data);
    if ('status' in data) {
	if (data.status == 'idle')
	    state = 'green';
	else
	    state = 'orange';
	updateStatus(data.status, state);
        updateTableFooter(data.status, state);
        updateEditable(state=='green');
	updateButtons(state=='green');
    }
};

/*Function to display time with one second increment
*/
function displayTime(){
  date.setSeconds(date.getSeconds()+1);
  phours.innerHTML=('0'+date.getHours()).slice(-2); //0 and slice is to format 1 to 01
  pmins.innerHTML=('0'+date.getMinutes()).slice(-2);
  psecs.innerHTML=('0'+date.getSeconds()).slice(-2);
  //local time
  ldate=new Date();
  lhours.innerHTML=('0'+ldate.getHours()).slice(-2);
  lmins.innerHTML=('0'+ldate.getMinutes()).slice(-2);
  lsecs.innerHTML=('0'+ldate.getSeconds()).slice(-2);

}

/*updates/ synchronises the piccolo time

param:
  ptime - piccolo time, data string
*/
function updateClocks(ptime){
  date = new Date(ptime);
  date.setSeconds(date.getSeconds()+1); // add one to sychronise
  displayTime();
}


/* End times ------------------------------------------------------------------ */

/* Status --------------------------------------------------------- */

/* Function to update status in status widget

params:
  status - written status (e.g. busy recording)
  state - colour of status (e.g. green)
  */
function updateStatus(status, state){
  $('#status').html(status)
  $('#status-icon').css('color', state)
}




/* Record Table --------------------------------------------------------- */

// initial calls for integration record table
updateTableFooter(status, state);
updateEditable(state=='green');

/* changes record to editable / not editable.

Param:
  editable - boolean, if true will enable the user to editintegration values
*/
function updateEditable(editable){
  edtable = document.getElementById('record-table');
  edbody = edtable.getElementsByTagName('tbody')[0]; //body of table
  if(editable){
    edbody.className = 'table-editable'
  } else {
    edbody.className = 'table-editable-disabled'
  }
  for (var i=0, row; row=edbody.rows[i]; i++){ //iterate through rows
    for(var j=1, col; col=row.cells[j]; j++){
      col.getElementsByTagName('span')[0].contentEditable=editable;
    }
  }

}

/*updates the status table of the record-table footer

params:
  status - written status (e.g. busy recording)
  state - colour of status (e.g. green)

*/
function updateTableFooter(status, state){
  $('#record-table-statusinfo').css('color', state);
  $('#record-table-statusicon').css('color', state);
  if (state=='green'){
      var msg = 'you can edit the table parameters'
  } else {
      var msg = 'you can not edit the table parameters'
  }
  statusinfo = '<strong>Status: </strong>' + status+ '; ' + msg;
  $('#record-table-statusinfo').html(statusinfo);
}

/* deal with buttons */
function updateButtons(idle){
    if (idle) {
	$('#runButton').prop('disabled', false);
	$('#pauseButton').prop('disabled', true);
	$('#stopButton').prop('disabled', true);
	$('#autoButton').prop('disabled', false);
    }
    else {
	$('#runButton').prop('disabled', true);
	$('#pauseButton').prop('disabled', false);
	$('#stopButton').prop('disabled', false);
	$('#autoButton').prop('disabled', true);
    }
}


$('#runButton').on('click', function() {
    var msg = JSON.stringify(['record',{'run':document.getElementById('run').value,
					'nsequence':parseInt(document.getElementById('nseq').value),
					'auto':parseInt(document.getElementById('auto').value),
					'delay': parseFloat(document.getElementById('delay').value),
				       }]);
    ws_piccolo.send(msg);
});

$('#darkButton').on('click', function() {
    var msg = JSON.stringify(['dark',{'run':document.getElementById('run').value}]);
    ws_piccolo.send(msg);
});

$(document).ready(function() {
  /* Check if enter is pressed for an integration value.
  Calls submitIngegration if the enter key is pressed
  */
 $('.table-editable span').keydown(function(e) {
     if(e.which == 13) { //enter key is 13
        $(this).blur().next().focus();
         val= $(this).text();
	 id = $(this).attr('id').split('-'); //get spectrometer and key from id
	 var data = JSON.stringify([id[0],id[1],val]);
	 ws.send(data);
      }
 });
 })

/* END Record Table --------------------------------------------------------- */
