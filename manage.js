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
        html+="<p>Title:"+item['title']+"<br />"+
          "Presenters: "+item['name']+"<br />"+
          "Start: "+item['time']+"<br />"+
          "End: "+item['end_time']+"<br />"+
          
          "</p>";
      }
    }
  }

  setElementHTML("schedule", html);
}


function setElementHTML(id, text) {
  document.getElementById(id).innerHTML=text;
}