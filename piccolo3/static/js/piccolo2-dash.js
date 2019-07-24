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
  cpu - boolean, CPU will be updated
  memory - boolean, memory will be updated
  status - boolean, status will be updated
  clock - boolean, clock will be updated
*/
function getInfo(cpu, memory){
    $.ajax({
    url: "info",
    cache: false,
    dataType: "json",
    success: function(data) {
      if(cpu){
        updateCPU(data.cpu);
      }
      if(memory){
        updateMemory(data.mem);
      }
    },
    error: function (request, status, error) { console.log(status + ", " + error); }
  });
}


/* Usage (CPU/Memory) --------------------------------------------------------- */

/*set interval to display new info every second*/
var usageTimer = setInterval(updateInfo, 2000);

/*get new info*/
function updateInfo(){
  getInfo(true, true);
}

/*update cpu width and displayed value

param:
  value - value of cpu used
*/
function updateCPU(value){
  $('#cpu').attr('aria-valuenow', value).css('width', value+'%');
  $('#cpu').html(value+'%')
}

/*update memory width and displayed value

param:
  value - value of memory used
*/
function updateMemory(value){
  $('#memory').attr('aria-valuenow', value).css('width', value+'%');
  $('#memory').html(value+'%')
}


/* use websocket to update status */
var ws_piccolo = new WebSocket('ws://' + document.domain + ':' + location.port + '/piccolo');
ws_piccolo.onmessage = function (evenet) {
    var data = JSON.parse(event.data);
    if ('status' in data) {
	if (data.status == 'idle')
	    state = 'green';
	else
	    state = 'orange';
	updateStatus(data.status,state);
    }
    if ('timeChanged' in data) {
	updateClocks(data.timeChanged);
    }
};


/* END Usage (CPU/Memory) ------------------------------------------------------ */

$(document).ready(function() {
    displayTime();
})
