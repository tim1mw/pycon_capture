import os
import sys
import web
import json
import pycurl
import certifi
from StringIO import StringIO
from subprocess import Popen, PIPE


os.environ['http_proxy'] = ''

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

urls = (
    '/(.*)', 'index'
)


class index:

    def GET(self, stuff):
        data = web.input(action="none", id=None)
        if data['action'] == 'start' or data['action'] == 'end':
            return self.saveNewTimeIndex(data)
        if data['action'] == 'ffmpeg':
            return self.makeFFmpegScript(data)
        if data['action'] == 'schedule':
            return self.getScheduleData()

    def saveNewTimeIndex(self, data):
        file = open("recordings/current.txt", "r")
        filename = file.read()
        pyDict = {"id": data['id'], "name": filename}

        timecode = self.readTimeCode()

        datastore = self.readTimecodeJSON()

        if data['date'] not in datastore:
            datastore[data['date']] = {}
            
        if data['room'] not in datastore[data['date']]:
            datastore[data['date']][data['room']] = {}

        if data['id'] not in datastore[data['date']][data['room']]:
            datastore[data['date']][data['room']][data['id']] = {}


        datastore[data['date']][data['room']][data['id']][data['action']] = timecode
        datastore[data['date']][data['room']][data['id']]['file'] = filename
        datastore[data['date']][data['room']][data['id']]['title'] = data['title']
        datastore[data['date']][data['room']][data['id']]['seqindex'] = data['seqindex']
        datastore[data['date']][data['room']][data['id']]['room'] = data['seqindex']

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

        return {}

    def readScheduleJSON(self):
        if os.path.exists("data/schedule.json"):
            jsondatafile = open("data/schedule.json", "r")
            return json.loads(jsondatafile.read())

        return {}

    def makeFFmpegScript(self, data):
        datastore = self.readTimecodeJSON()
        
        if data['date'] not in datastore or data['room'] not in datastore[data['date']]:
            return
        
        roomdata = datastore[data['date']][data['room']]
        basedir = "processed/"+self.makeSafeFilename(data['date'])+"-"+self.makeSafeFilename(data['room'])
        
        script = "#!/bin/bash\n\n"
        script += "mkdir "+basedir+"\n\n"
        
        for item in roomdata:
            # The strip() on the timecode read seems have no effect, but it works when I do it here,
            # so repeat to make sure we have no whitespace junk
            filename = roomdata[item]['seqindex'] + "_" + item + "_" + roomdata[item]['title']
            filename = basedir + "/" + self.makeSafeFilename(filename) + ".mp4"
            
            script += "ffmpeg -i \"raw/" + roomdata[item]['file'].strip() + "\""
            script += " -ss " + roomdata[item]['start']
            script += " -to " + roomdata[item]['end']
            script += " -c copy -async 1"
            script += " \"" + filename + "\""
            script += "\n\n"

        scriptfile = self.makeSafeFilename(data['date']) + "-" + self.makeSafeFilename(data['room'])+"-ffmpeg.sh"
        file = open("recordings/" + scriptfile, 'w')
        file.write(script)
        file.close()

        return json.dumps({"ok": True, "filename": scriptfile})

    def makeSafeFilename(self, s):
        return "".join(self.safeChar(c) for c in s).rstrip("_")

    def safeChar(self, c):
        if c.isalnum():
            return c
        else:
            return "_"

    def getScheduleData(self):
        try:
            buffer = StringIO()
            c = pycurl.Curl()
            c.setopt(c.URL, 'https://pretalx.com/pyconuk-2023/schedule/export/schedule.json')
            c.setopt(c.FOLLOWLOCATION, True)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.CAINFO, certifi.where())
            c.perform()
            c.close()
        
            schedule = buffer.getvalue()
            file = open("data/schedule.json", 'w')
            file.write(schedule)
            file.close()
            return schedule
        except Exception as e:
            print e
            print("Using cached schedule...")
            schedulecache = open("data/schedule.json", 'r')
            return schedulecache.read()


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()
