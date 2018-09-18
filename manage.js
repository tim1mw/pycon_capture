var rawdata={};
var currentData={};
var timeData={};
var rendered=[];

var dcookie = getCookie("date");
if (dcookie != "") {
    currentDate = dcookie;
}

var rcookie = getCookie("room");
if (rcookie != "") {
    currentRoom = rcookie;
}

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
    rawdata = data;
    currentData = data[currentDate]['matrix'];
    readJSONURL("recordings/timedata.json", readTimeData);
}

function readTimeData(data) {
    timeData = data;
    render();
    setInterval(activePres, 30000);
}

function activePres() {
    var datenow = new Date();
    var timenow = datenow.getTime();

    for (index in rendered) {
        var item = rendered[index];
        var startTime = Date.parse(datenow.toDateString()+" "+item['time']);
        var endTime = Date.parse(datenow.toDateString()+" "+item['end_time']);
        var ele=document.getElementById("pres_"+index);
        if (timenow > startTime && timenow < endTime) {
            console.log(":::"+item['ical_id']);
            ele.style.background='#ffffff';
            ele.style.border='4px solid red';
        } else {
            ele.style.background='#eeeeee';
            ele.style.border='2px solid black';
        }
    }
}

function dateChange() {
    currentDate = document.getElementById('datechoice').value;
    setCookie("date", currentDate, 100);
    currentData = rawdata[currentDate]['matrix'];
    rendered=[];
    render();
}

function roomChange() {
    currentRoom = document.getElementById('roomchoice').value;
    setCookie("room", currentRoom, 100);
    rendered=[];
    render();
}

function render() {
  var html="<div style='padding-top:2px;padding-bottom:6px;margin-top:10px;margin-left:2px;margin-right:2px;margin-bottom:10px;border:2px solid black;'>"+
      "<p style='font-weight:bold;font-size:large;'>PyCon Capture - Schedule Choice</p>"+
      "Date: <select name='date' id='datechoice' onChange='dateChange()'>";

  for (index in rawdata) {
      if (index == currentDate) {
          html += "<option value='"+index+"' selected>"+index+"</option>";
      } else {
          html += "<option value='"+index+"'>"+index+"</option>";
      }
  }
  html += "</select><br />"+
      "Room: <select name='room' id='roomchoice' onchange='roomChange()'>";

  for (index in rawdata[currentDate]['rooms']) {
      var item = rawdata[currentDate]['rooms'][index];
      if (item == currentRoom) {
          html += "<option value='"+item+"' selected>"+item+"</option>";
      } else {
          html += "<option value='"+item+"'>"+item+"</option>";
      }
  }

  html += '</select><br /></div>';

  for (index in currentData) {
    for (index2 in currentData[index]) {
      var item = currentData[index][index2];
      if (item == null) {
        continue;
      }
      if (item['room'] == currentRoom && !item['break_event']) {

        rendered[item['ical_id']] = item;

        var file = '';
        var startTime = '';
        var endTime = '';

        if (timeData.hasOwnProperty(item['ical_id'])) {
            file = timeData[item['ical_id']]['file'];
            startTime = timeData[item['ical_id']]['start'];
            endTime = timeData[item['ical_id']]['end'];
        }

        html+= "<div id='pres_"+item['ical_id']+"' style='background:#eeeeee;border:2px solid black;margin:2px;'>"+
          "<p class='title'>Title:<div id='title_"+item['ical_id']+"'>"+item['title']+"</div></p>"+
          "<p>Presenter(s): "+item['name']+"<br />"+
          "Schedule Time: <span style='font-weight:bold'>"+item['time']+" to "+item['end_time']+"</span><br />"+
          "ical_id: "+item['ical_id']+"<br />"+
          "Recording File: <input type='text' id='name_"+item['ical_id']+"' name='name_"+item['ical_id']+"' size='20' value='"+file+"' readonly /><br />"+
          "Start time index:  <input type='text' id='start_"+item['ical_id']+"' name='start_"+item['ical_id']+"' size='8' value='"+startTime+"' readonly /><br />"+
          "End time index:  <input type='text' id='end_"+item['ical_id']+"' name='end_"+item['ical_id']+"' size='8' value='"+endTime+"' readonly /><br /><br />"+
          "<a href='javascript:setStart(\""+item['ical_id']+"\")' class='markbutton'>Mark Presentation Start</a>&nbsp;&nbsp;&nbsp;"+
          "<a href='javascript:setEnd(\""+item['ical_id']+"\")' class='markbutton'>Mark Presentation End</a>"+
          "</p></div>";
      }
    }
  }

  setElementHTML("schedule", html);
  activePres();
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
    var url="code.py/?id="+id+"&action=start&title="+getTitle(id);
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
    var url="code.py/?id="+id+"&action=end&title="+getTitle(id);
    readJSONURL(url, setEndCallback);
}

function setEndCallback(data) {
    document.getElementById('end_'+data['id']).value = data['end'];
    document.getElementById('name_'+data['id']).value = data['name'];
}

function getTitle(id) {
    return encodeURIComponent(document.getElementById("title_"+id).innerHTML);
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

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}