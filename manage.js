var data={};
var currentData={};
var timeData={};

readJSONURL("code.py/?action=schedule", setCurrentData);


// Methods

function readJSONURL(url, callBack) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            callBack(JSON.parse(this.responseText));
        }

        if (this.readyState == 4 && this.status == 404) {
            callBack({});
        }
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send(); 
}

function setCurrentData(data) {
    currentData = data[currentDate]['matrix'];
    readJSONURL("recordings/timedata.json", readTimeData);
}

function readTimeData(data) {
    timeData = data;
    render();
}

function render() {
  var html="";

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
          "Recording File: <input type='text' id='name_"+item['ical_id']+"' name='name_"+item['ical_id']+"' size='20' value='"+file+"' readonly /><br />"+
          "Start time index:  <input type='text' id='start_"+item['ical_id']+"' name='start_"+item['ical_id']+"' size='8' value='"+startTime+"' readonly /><br />"+
          "End time index:  <input type='text' id='end_"+item['ical_id']+"' name='end_"+item['ical_id']+"' size='8' value='"+endTime+"' readonly /><br /><br />"+
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
    if (document.getElementById('start_'+id).value != "") {
       var r = confirm("Start time already set, are you sure you want to do this?");
       if (!r) {
           return;
       }
    }
    var url="code.py/?id="+id+"&action=start";
    readJSONURL(url, setStartCallback);
}

function setStartCallback(data) {
    document.getElementById('start_'+data['id']).value = data['start'];
    document.getElementById('name_'+data['id']).value = data['name'];
}

function setEnd(id) {
    if (document.getElementById('end_'+id).value != "") {
       var r = confirm("End time already set, are you sure you want to do this?");
       if (!r) {
           return;
       }
    }
    var url="code.py/?id="+id+"&action=end";
    readJSONURL(url, setEndCallback);
}

function setEndCallback(data) {
    document.getElementById('end_'+data['id']).value = data['end'];
    document.getElementById('name_'+data['id']).value = data['name'];
}

function makeFFmpegScript() {
    var url="code.py/?action=ffmpeg";
    readJSONURL(url, ffmpegCallback);
}

function ffmpegCallback(data) {
    if (data['ok']) {
        alert("FFMPEG Script created");
    } else {
        alert("Error creating FFMPEG Script");
    }
}