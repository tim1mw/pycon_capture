var rawdata={};
var currentData={};
var timeData={};
var rendered=[];
var currentDate = "";
var currentRoom = "";

var dcookie = getCookie("date");
if (dcookie != "") {
    currentDate = dcookie;
}

var rcookie = getCookie("room");
if (rcookie != "") {
    currentRoom = rcookie;
}

readJSONURL("code.py/?action=schedule", setCurrentData);


window.addEventListener('DOMContentLoaded', function() {
    var sideblock = document.getElementById("schedule");
    sideblock.style.height = (window.innerHeight-25)+"px";

    var vid = document.getElementById("videojs-player");
    vid.addEventListener("loadedmetadata", startVUMeter);
});




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
        
        if (this.readyState == 4 && this.status == 500) {
            alert("500 error calling "+url+" "+this.responseText);
        }
        
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send(); 
}

function setCurrentData(data) {
    rawdata = data;
    if (currentDate == "") {
        currentDate = data['schedule']['conference']['days'][0]['date'];
    }

    if (currentRoom == "") {
        for (room in data['schedule']['conference']['days'][0]['rooms']) {
            currentRoom = room;
            break;
        }
    }
    updateCurrentData();
    readJSONURL("recordings/timedata.json", readTimeData);
}

function updateCurrentData() {
    for (day in rawdata['schedule']['conference']['days']) {
        if (currentDate == rawdata['schedule']['conference']['days'][day]['date']) {
            currentData = rawdata['schedule']['conference']['days'][day]['rooms'][currentRoom];
        }
    }
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
            console.log(":::"+item['id']);
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
    updateCurrentData();
    rendered=[];
    render();
}

function roomChange() {
    currentRoom = document.getElementById('roomchoice').value;
    setCookie("room", currentRoom, 100);
    updateCurrentData();
    rendered=[];
    render();
}

function render() {
  var html="<div class='headingblock'>"+
      "<p class='heading'>PyCon Capture - Schedule Choice</p>"+
      "<table>"+
      "<tr><td>Date: </td><td><select name='date' id='datechoice' onChange='dateChange()'>";

  var rooms = [];
  for (index in rawdata['schedule']['conference']['days']) {
      var item = rawdata['schedule']['conference']['days'][index];
      if (item['date'] == currentDate) {
          html += "<option value='"+item['date']+"' selected>"+item['date']+"</option>";
          rooms = rawdata['schedule']['conference']['days'][index]['rooms'];
      } else {
          html += "<option value='"+item['date']+"'>"+item['date']+"</option>";
      }
  }
  html += "</select><td></tr>"+
      "<tr><td>Room:</td><td><select name='room' id='roomchoice' onchange='roomChange()'>";

  for (index in rooms) {
      if (index == currentRoom) {
          html += "<option value='"+index+"' selected>"+index+"</option>";
      } else {
          html += "<option value='"+index+"'>"+index+"</option>";
      }
  }

  html += '</select></td></tr></table></div>';

  for (index in currentData) {
      var item = currentData[index];
      if (item == null) {
        continue;
      }

      rendered[item['id']] = item;

      var file = '';
      var startTime = '';
      var endTime = '';

      if (timeData.hasOwnProperty(item['id'])) {
          file = timeData[item['id']]['file'];
          startTime = timeData[item['id']]['start'];
          endTime = timeData[item['id']]['end'];
      }

      var presenters = "";
      for (pres in item['persons']) {
          presenters += item['persons'][pres]['public_name']+", ";
      }
      presenters = presenters.substring(0, presenters.length-2);

      html+= "<div id='pres_"+item['id']+"' class='presblock'>"+
          "<p class='title'><span id='title_"+item['id']+"'>"+item['title']+"</span></p>"+
          "<table>"+
          "<tr><td>Presenter(s):</td><td>"+presenters+"</td></tr>"+
          "<tr><td>Schedule Start:</td><td>"+item['start']+"</td></tr>"+
          "<tr><td>Schedule Duration:</td><td>"+item['duration']+"</td></tr>"+
          "<tr><td>ID:</td><td>"+item['id']+"</td></tr>"+
          "<tr><td>Recording File:</td><td><input type='text' id='name_"+item['id']+"' name='name_"+item['id']+"' size='30' value='"+file+"' readonly /></td></tr>"+
          "<tr><td>Start time index:</td><td><input type='text' id='start_"+item['id']+"' name='start_"+item['id']+"' size='8' value='"+startTime+"' readonly /></td></tr>"+
          "<tr><td>End time index:</td><td><input type='text' id='end_"+item['id']+"' name='end_"+item['id']+"' size='8' value='"+endTime+"' readonly /></td></tr></table><br />"+
          "<input type='hidden' name='seqindexv_"+item['id']+"' id='seqindex_"+item['id']+"' value='"+index+"' />"+
          "<div class='buttonblock'><a href='javascript:setStart(\""+item['id']+"\")' class='markbutton'>Mark Presentation Start</a></div>"+
          "<div class='buttonblock'><a href='javascript:setEnd(\""+item['id']+"\")' class='markbutton'>Mark Presentation End</a></div>"+
          "</p></div>";
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
    var url="code.py/?id="+id+"&action=start&seqindex="+getSeqIndex(id)+"&title="+getTitle(id);
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
    var url="code.py/?id="+id+"&action=end&seqindex="+getSeqIndex(id)+"&title="+getTitle(id);
    readJSONURL(url, setEndCallback);
}

function setEndCallback(data) {
    document.getElementById('end_'+data['id']).value = data['end'];
    document.getElementById('name_'+data['id']).value = data['name'];
}

function getTitle(id) {
    return encodeURIComponent(document.getElementById("title_"+id).innerHTML);
}

function getSeqIndex(id) {
    return document.getElementById("seqindex_"+id).value;
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

function startVUMeter() {
  var ctx = new AudioContext();
  var audio = document.getElementById('videojs-player');
  var audioSrc = ctx.createMediaElementSource(this);
  var analyser = ctx.createAnalyser();
  audioSrc.connect(analyser);
  audioSrc.connect(ctx.destination);

  var frequencyData = new Uint8Array(analyser.frequencyBinCount);
 
  function renderFrame() {
     requestAnimationFrame(renderFrame);

     analyser.getByteFrequencyData(frequencyData);
     var values = 0;

     var length = frequencyData.length;
     for (var i = 0; i < length; i++) {
         values += (frequencyData[i]);
         var average = values / length;
         document.getElementById("vumeter").value = parseInt(average);
     }
  }
  renderFrame();
}
