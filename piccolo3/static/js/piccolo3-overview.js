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

var syncButton = document.getElementById('syncButton');

//set interval to display new time every second
var timer = setInterval(displayTime, 1000);

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

    if (Math.abs(date.getTime() - ldate.getTime()) > 60000) {
	syncButton.style.visibility = "visible";
    }
    else {
	syncButton.style.visibility = "hidden";
    }
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

/* synchronize clock button */
$('#syncButton').on('click', function() {
    ldate=new Date();
    var msg = JSON.stringify(['sync',{ 'time' : ldate.toISOString() }]);
    ws_piccolo.send(msg);
});


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

