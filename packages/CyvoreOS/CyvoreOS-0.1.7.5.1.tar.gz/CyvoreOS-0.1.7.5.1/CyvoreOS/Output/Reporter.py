import json 
from pathlib import Path
import pkgutil
from CyvoreOS.checkObject import Check, Case
#from checkObject import Check
#from checkObject import Case

def MakeCaseReportJson(testCase):
    checkDir("")
    with open("Cases\\%s.json"%testCase.caseID, "w") as outfile: 
        json.dump(testCase.getDict(), outfile)
        
def MakeCheckReportJson(chk):
    with open(chk.checkID, "w") as outfile: 
        json.dump(chk.getDict(), outfile)

    
    
    
    
def checkDir(plugin_name):
    Path("Cases\\%s"%plugin_name).mkdir(parents=True, exist_ok=True)