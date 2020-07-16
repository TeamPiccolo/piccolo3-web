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

// get current temperature
function getCTemp() {
    $.ajax({
    url: "ctemp",
    cache: false,
    dataType: "json",
	success: function(data) {
	    for (const [spec,temp] of Object.entries(data)) {
		var idx = spec + '-current';
		var cell = document.getElementById(idx);
		cell.innerHTML = temp;
	    }
    },
    error: function (request, status, error) { console.log(status + ", " + error); }
    });
}

/*set interval to display new info every second*/
var usageTimer = setInterval(getCTemp, 10000);

//websocket used to control TEC
var wt = new WebSocket('ws://' + document.domain + ':' + location.port + '/tempctrl');
wt.onmessage = function (event) {
    var data = JSON.parse(event.data);
    var spec = data[0];
    var key = data[1].split('/');
    var value = data[2];
    
    if (key[0] == 'status') {
	var idx = '#'+spec.replace('+','\\+') + '-status-icon';
	if (value < 4)
	    var colour = 'red';
	else if (value == 4)
	    var colour = 'black';
	else if (value > 5)
	    var colour = 'orange';
	else
	    var colour = 'green';
	$(idx).css('color', colour);
    }
    else if (key[0] == 'present') {
	
    }
    else {
        var idx = spec + '-' + key[0];
        var cell = document.getElementById(idx);
	if (key[0] == 'target_temperature')
	    cell.value = value;
	else if (key[0] == 'TECenabled')
	    cell.checked = value;
	else if (key[0] == 'current')
            cell.innerHTML = value;
    }
  

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
    }
};



/* Record Table --------------------------------------------------------- */

// initial calls for integration record table
updateTableFooter(status, state);

/* changes record to editable / not editable.

Param:
  editable - boolean, if true will enable the user to editintegration values
*/
function updateEditable(editable){
    edtable = document.getElementById('temperature-table');
    edbody = edtable.getElementsByTagName('tbody')[0]; //body of table
        
  for (var i=0, row; row=edbody.rows[i]; i++){ //iterate through rows
      col=row.cells[1];
      if (!editable) 
	  col.getElementsByTagName('input')[0].setAttribute("readonly",editable);
      else
	  col.getElementsByTagName('input')[0].removeAttribute("readonly");
      col=row.cells[3];
      if (!editable) 
	  col.getElementsByTagName('input')[0].setAttribute("disabled",editable);
      else
	  col.getElementsByTagName('input')[0].removeAttribute("disabled");
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

$(document).ready(function() {
  /* Check if enter is pressed for an integration value.
  Calls submitIngegration if the enter key is pressed
  */
    displayTime();
    var elements = document.getElementsByTagName("input");
    for (let item of elements) {
	item.addEventListener("change",
        function(event) {
	    var [spec,key] = this.id.split('-');
	    if (key == 'TECenabled')
		val = this.checked;
	    else
		val = this.value;
	    var data = JSON.stringify([spec,key,val]);
            wt.send(data);
        }, false);
    }
 })

/* END Record Table --------------------------------------------------------- */
