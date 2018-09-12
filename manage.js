var data={};
var currentData={};
var timeData={};

var xmlhttp = new XMLHttpRequest();
xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        data = JSON.parse(this.responseText);
        readData(render);
    }
};
xmlhttp.open("GET", "schedule.json", true);
xmlhttp.send(); 



// Methods

function readData(callMethod) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            timeData = JSON.parse(this.responseText);
            callMethod();
        }

        if (this.readyState == 4 && this.status == 404) {
            callMethod();
        }
    };
    xmlhttp.open("GET", "timedata.json", true);
    xmlhttp.send(); 
}

function render() {
  var html="";

  currentData = data[currentDate]['matrix'];
  for (index in currentData) {
    for (index2 in currentData[index]) {
      var item = currentData[index][index2];
      if (item == null) {
        continue;
      }
      if (item['room'] == currentRoom && !item['break_event']) {

        var file = '';
        var startTime = '';
        var endTime = '';

        if (timeData.hasOwnProperty(item['ical_id'])) {
            file = timeData[item['ical_id']]['file'];
            startTime = timeData[item['ical_id']]['start'];
            endTime = timeData[item['ical_id']]['end'];
        }

        html+="<p class='title'>Title:"+item['title']+"</p>"+
          "<p>Presenter(s): "+item['name']+"<br />"+
          "Schedule Time: "+item['time']+" to "+item['end_time']+"<br />"+
          "ical_id: "+item['ical_id']+"<br />"+
          "Recording File: <input type='text' name='name_"+item['ical_id']+"' size='20' value='"+file+"'/><br />"+
          "Start time index:  <input type='text' name='start_"+item['ical_id']+"' size='8' value='"+startTime+"' /><br />"+
          "End time index:  <input type='text' name='end_"+item['ical_id']+"' size='8' value='"+endTime+"' /><br /><br />"+
          "<a href='javascript:setStart(\""+item['ical_id']+"\")' class='markbutton'>Mark Presenation Start</a>&nbsp;&nbsp;&nbsp;"+
          "<a href='javascript:setEnd(\""+item['ical_id']+"\")' class='markbutton'>Mark Presenation End</a>"+
          "<hr /></p>";
      }
    }
  }

  setElementHTML("schedule", html);
}


function setElementHTML(id, text) {
  document.getElementById(id).innerHTML=text;
}

function setStart(id) {

}

function setEnd(id) {

}