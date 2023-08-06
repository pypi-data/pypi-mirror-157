import uuid
import urllib.parse
from .File import File
from .Preset import Preset
from .SupplyChain import SupplyChain

class Asset:

    def __init__(self,Rally,id=None,name=None):
        self.Rally = Rally
        if not id and not name:
            self.name = "Int_Test_Asset_{}".format(str(uuid.uuid4()))
            self.id = Rally.apiCall("POST","/assets",body={"data": {"attributes": {"name": self.name }, "type": "assets" }})["data"]["id"]
        elif not id:
            self.name = name
            try:
                self.id = Rally.apiCall("GET","/assets?search=name={}".format(urllib.parse.quote_plus(name)))["data"][0]["id"]
            except IndexError:
                raise ValueError("Could not find asset with name '{}'".format(name)) from None
        else:
            self.id = id
            self.name = name

    def getName(self):
        if not self.name:
            self.name = self.Rally.apiCall("GET","/assets/{}".format(self.id))["data"]["attributes"]["name"]
        return self.name

    def getMetadata(self):
        self.metadata = self.Rally.apiCall("GET","/movies/{}/metadata/Metadata".format(self.id))["data"]["attributes"]["metadata"]
        return self.metadata

    def getWorkflowMetadata(self):
        self.workflowMetadata = self.Rally.apiCall("GET","/movies/{}/metadata/Workflow".format(self.id))["data"]["attributes"]["metadata"]
        return self.workflowMetadata
    
    def delete(self):
        return self.Rally.apiCall("DELETE","/assets/{}".format(self.id),fullResponse=True)

    def preset(self,id=None,name=None):
        return Preset(self,id=id,name=name)

    def supplychain(self,id=None,name=None):
        return SupplyChain(self,id=id,name=name)

    def listFiles(self):
        fileData = self.Rally.apiCall("GET","/assets/{}/files".format(self.id),paginate=True)["data"]
        return [File(self,id=item["id"],label=item["attributes"]["label"]) for item in fileData]

    def getFile(self,id=None,label=None):
        return File(self,id=id,label=label)