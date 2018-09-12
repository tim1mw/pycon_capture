import os, sys

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)
import web
import json

from subprocess import Popen, PIPE


urls = (
    '/(.*)', 'index'
)

class index:

    def GET(self, stuff):

        data = web.input(action="none",id=None)
        file = open("recordings/current.txt", "r") 
        pyDict = {"id":data['id'], "name": file.read()}

        if data['action'] == 'start':
            pyDict['start'] = self.readTimeCode()

        if data['action'] == 'end':
            pyDict['end'] = self.readTimeCode()
       
        web.header('Content-Type', 'application/json')
        return json.dumps(pyDict)

    def readTimeCode(self):
        try:
            proc = Popen('./get_recording_time.sh', stdout=PIPE, stderr=PIPE)
            out, err = proc.communicate()
            print("stdout: " + out.decode("utf-8"))
            print("stderr: " + err.decode("utf-8"))
            return out.decode("utf-8")

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