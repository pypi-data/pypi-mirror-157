import ast
import json

class Job:

    def __init__(self,Preset,id=None,attributes=None):
        if not id:
            raise TypeError("Please specify the job id")
        self.id = id
        self.Rally = Preset.Asset.Rally
        self.Asset = Preset.Asset
        self.Preset = Preset
        self.presetName = Preset.name
        if not attributes:
            attributes = self.Rally.apiCall("GET","/jobs/{}".format(self.id))["data"]["attributes"]
        self.result = attributes["result"]
        self.dynamicPresetData = attributes["dynamicPresetData"]
        
    def getArtifact(self,name,parse=False):
        artifact = self.Rally.apiCall("GET","/artifacts/{}_{}/content".format(self.id,name),fullResponse=True).text
        if parse:
            oneLine = artifact.replace("'\n '","").replace("\n('","").replace("')\n","").replace('"\n "','').replace('"\n("','').replace('")\n','').replace("\n","")
            firstCurly = oneLine.find("{")
            firstSquare = oneLine.find("[")
            if firstCurly < firstSquare:
                lastCurly = oneLine.rfind("}")
                try:
                    return json.loads(oneLine[firstCurly-1:lastCurly])
                except:
                    try:
                        return ast.literal_eval(oneLine[firstCurly-1:lastCurly])
                    except:
                        raise ValueError("Could not parse output to a dictionary")
            else:
                lastSquare = oneLine.rfind("]")
                try:
                    return json.loads(oneLine[firstSquare:lastSquare+1])
                except:
                    try:
                        return ast.literal_eval(oneLine[firstSquare:lastSquare+1])
                    except:
                        raise ValueError("Could not parse output to a dictionary")
        return artifact