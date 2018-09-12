import os, sys
import web
import json
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
        file = open("recordings/current.txt", "r")
        filename = file.read()
        pyDict = {"id":data['id'], "name": filename}

        timecode = self.readTimeCode()

        datastore = {}
        if os.path.exists("recordings/timedata.json"):
            jsondatafile = open("recordings/timedata.json", "r")
            datastore = json.loads(jsondatafile.read())

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
            return out.decode("utf-8").strip(' \t\n\r')

        except Exception as inst:
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           # __str__ allows args to be printed directly

        return "--:--:--"


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()