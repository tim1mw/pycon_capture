import os, sys
import web
import json
import urllib2
from subprocess import Popen, PIPE


abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)



urls = (
    '/(.*)', 'index'
)

class index:

    def GET(self, stuff):
        data = web.input(action="none",id=None)
        if data['action'] == 'start' or data['action'] == 'end':
            return self.saveNewTimeIndex(data)
        if data['action'] == 'ffmpeg':
            return self.makeFFmpegScript();
        if data['action'] == 'schedule':
            return self.getScheduleData()

    def saveNewTimeIndex(self, data):
        file = open("recordings/current.txt", "r")
        filename = file.read()
        pyDict = {"id":data['id'], "name": filename}

        timecode = self.readTimeCode()

        datastore = self.readTimecodeJSON()

        if data['id'] not in datastore:
            datastore[data['id']] = {}
            
        datastore[data['id']][data['action']] = timecode
        datastore[data['id']]['file'] = filename
        
        with open("recordings/timedata.json", 'w') as f:
            json.dump(datastore, f, indent=4, sort_keys=True)

        pyDict[data['action']] = timecode

        web.header('Content-Type', 'application/json')
        return json.dumps(pyDict)

    def readTimeCode(self):
        try:
            proc = Popen('./get_recording_time.sh', stdout=PIPE, stderr=PIPE)
            out, err = proc.communicate()
            return out.decode("utf-8").strip()

        except Exception as inst:
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           # __str__ allows args to be printed directly

        return "--:--:--"

    def readTimecodeJSON(self):
        if os.path.exists("recordings/timedata.json"):
            jsondatafile = open("recordings/timedata.json", "r")
            return json.loads(jsondatafile.read())

        return {};


    def makeFFmpegScript(self):
        datastore = self.readTimecodeJSON()
        script = ""
        for item in datastore:
            # The strip() on the timecode read seems have no effect, but it works when I do it here,
            # so repeat to make sure we have no whitespace junk
            script += "ffmpeg -i \""+datastore[item]['file'].strip()+"\""
            script += " -ss "+datastore[item]['start']
            script += " -to "+datastore[item]['end']
            script += " -c copy -async 1"
            script += " "+item+".mp4"
            script += "\n\n"
            
        file = open("recordings/ffmpeg-script.sh", 'w')
        file.write(script)
        file.close()

        return json.dumps({"ok":True})
        
    def getScheduleData(self):
        try:
            response = urllib2.urlopen('https://2018.hq.pyconuk.org/schedule/json/', timeout=5)
            schedule = response.read()
            file = open("recordings/schedule.json", 'w')
            file.write(schedule)
            file.close()
            return schedule
        except urllib2.URLError as err: 
            schedulecache = open("recordings/schedule.json", 'r')
            return schedulecache.read()

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()