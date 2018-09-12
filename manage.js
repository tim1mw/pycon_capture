var data={};

var xmlhttp = new XMLHttpRequest();
xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        data = JSON.parse(this.responseText);
        start();
    }
};
xmlhttp.open("GET", "schedule.json", true);
xmlhttp.send(); 

var currentData={};

function start() {
  var html="";

  currentData = data[currentDate]['matrix'];
  for (index in currentData) {
    for (index2 in currentData[index]) {
      var item = currentData[index][index2];
      if (item == null) {
        continue;
      }
      if (item['room'] == currentRoom && !item['break_event']) {
        console.log(item);
        html+="<p class='title'>Title:"+item['title']+"</p>"+
          "<p>Presenter(s): "+item['name']+"<br />"+
          "Schedule Time: "+item['time']+" to "+item['end_time']+"<br />"+
          "ical_id: "+item['ical_id']+"<br />"+
          "Recording File: <input type='text' name='name_"+item['ical_id']+"' size='20' /><br />"+
          "Start time index:  <input type='text' name='start_"+item['ical_id']+"' size='8' /><br />"+
          "End time index:  <input type='text' name='end_"+item['ical_id']+"' size='8' /><br /><br />"+
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