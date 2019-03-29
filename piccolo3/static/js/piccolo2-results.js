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



//onload display graph of first element in list
$(document).ready(function() {

  //get first element in List
  tbody=document.getElementById('spectraList');
  ele = tbody.getElementsByTagName('th')[0];
  getSpectrum(ele);

});


/* spectra List  ------------------------------------------------------ */

/*gets spectraList, if it fails the function calls itself once more(icrementing tryNumber)

params:
  run - optional, the run of the list, e.g. 2018/11/30
  tryNumber - optional, default 1
*/
function getSpectraList(run, tryNumber){
  if(!tryNumber){
    tryNumber=1; //first try
  }
  url="data/"
  if (run != null){ // add run to URL if given
    url = url +run.value;
  }
  $.ajax({
  url: url,
  cache: false,
  dataType: "json",
      success: function(data) {
      createSpectraListHtml(run.value,data);
  },
  error: function (request, status, error) { //fail
    console.log(status + ", " + error);
    //try again
    if(!(tryNumber>1)){
      console.log('trying again...')
      getSpectrum(run, tryNumber+1) //try again

    }
  }
});
}


/*function to create list HTML for getSpectraList

param:
  spectraList - a list with spectra names
*/
function createSpectraListHtml(run,spectraList){
    ele = document.getElementById('spectraList');
  html=''
  spectraList.forEach(function(file) {
html = html + '<tr><th data-run="'+run+'" onclick="getSpectrum(this)" style="cursor: pointer;">'+file+'</th></tr>'
  });
  ele.innerHTML=html;
}

/* Query results  -------------------------------------------------- */

/*gets the data of a spectrum, if it fails the function calls itself once more(icrementing tryNumber)

params:
  ele - either TH element from spectraList or SELECT element from direction selector underneath graph
  tryNumber - optional, default 1
*/
function getSpectrum(ele, tryNumber){
    run = ele.getAttribute('data-run');
  if(!tryNumber){
    tryNumber=1; //first try
  }
    var spectra;
  if(ele.tagName==='TH'){
    spectra = ele.innerHTML;
    url="data/"+run+"/"+spectra+"?data=plot_all";
  }else if (ele.tagName==='SELECT'){
    spectra=$(ele).find(':selected').data('spectra');
    direction = $(ele).find(':selected').data('direction');
      url="data/"+run+"/"+spectra+"?data=plot_"+direction;
  }
  $.ajax({
  url: url,
  cache: false,
  dataType: "json",
  success: function(data) {
      document.getElementById('result-file').innerHTML = spectra;
    createChart(data);
      generateSelect(data, spectra, run);
  },
  error: function (request, status, error) { //fail
    console.log(status + ", " + error);
    //try again
    if(!(tryNumber>1)){
      console.log('trying again...')
      getSpectrum(ele, tryNumber+1) //try again

    }
  }
});
}



/* Display graph and direction select  -------------------------------------------------- */


//colours for the dataset lines
var colours =["indianred", "#57889c", "#26c281", "#97d3c5"];
var chart; //global var to delete charts
/*Generates a select HTML element to choose between directions underneath graph

param:
  data - a list with different datasets in JSON format, returned by the Api
  spectraName - the spectra name of the displayed chart
*/
function generateSelect(data, spectraName, run){
  ele = document.getElementById('select-direction');
    directions=data[0].Directions;
  html='<select data-run="'+run+'" onchange="getSpectrum(this)" class="form-control" style="width: 50%; margin-left: 50px;">'
  for(i=0; i<directions.length; i++){
    html=html+'<option data-spectra="'+spectraName+'" data-direction="'+directions[i]+'"';
    if(directions[i]===data[0].Metadata.Direction){
      html = html+' selected="true" disabled="disabled"';
    }
    html=html+'>'+directions[i]+'</option>';
  }
  html=html+'</select>';
  ele.innerHTML = html;
}


/*Returns the datasets in chartJS form*/
function getChartDatasets(data){
  datasets=[data.length];
  for(var i=0; i<data.length; i++){
    //modulo, in case there are not enough colours some will be used twice
    mod = i%colours.length;
    datasets[i]={
      data: data[i].plotList,
      label: data[i].Metadata.SerialNumber,
      borderColor: colours[mod],
      borderWidth: 2,
      showLine: true,
      fill: false
    }
  }
  return datasets;
}

/*Returns the highest saturation amongst the different datasets

param:
  data - a list with different datasets in JSON format, returned by the Api
*/
function highestSaturation(data){
  var saturation=0;
  for(var i=0; i<data.length; i++){
    if(data[i].Metadata.SaturationLevel>saturation){
      saturation = data[i].Metadata.SaturationLevel;
    }
  }
  return saturation;
}


/*Function to create chart from data

param:
  data - a list with different datasets in JSON format, returned by the Api
*/
function createChart(data){

  //destroy old chart
  if(chart){
    chart.destroy();
  }
  datasets=getChartDatasets(data); // get the dataset code prepared for chart.js
  saturation = highestSaturation(data); // get saturation

  // set chart title to time and Dark/Light
    var title;
  if(data[0].Metadata.Dark){
    title=data[data.length-1].Metadata.Datetime + ': Dark'
  }else{
    title=data[data.length-1].Metadata.Datetime + ': Light'
  }

//create chart.js chart
chart = Chart.Scatter(document.getElementById("line").getContext("2d"), {
  type: 'scatter',
  data: {
    datasets: datasets
  },
  options: {
    elements: {
      point: {
        radius: 0
      }
    },
    title: {
      display: true,
      text: title
    },
    scales: {
         yAxes: [{
            ticks: {
               min: 0,
               max: saturation
            }
         }]
      }
  }
  });

} //end createChart()
