import os
import requests
import json
from .Asset import Asset

class Rally:

    def __init__(self,configFromRallyTools=True,env="UAT",apiUrl=None,apiKey=None):
        self.env = env
        self.apiUrl = apiUrl
        self.apiKey = apiKey
        if configFromRallyTools:
            configPath = os.path.expanduser('~')+"/.rallyconfig"
            rallyConfig = open(configPath)
            rallyConfigJson = json.load(rallyConfig)
            apiConfig = rallyConfigJson["api"]
            rallyConfig.close()
            self.apiUrl = apiConfig[env]["url"]
            self.apiKey = apiConfig[env]["key"]
        elif not apiUrl or not apiKey:
            raise TypeError("Please specify both apiUrl and apiKey parameters")
    
    def apiCall(self,method,endpoint,body={},paginate=False,fullResponse=False,errors=True):
        headers={"Authorization":"Bearer {}".format(self.apiKey),"Content-Type":"application/json"}
        response = requests.request(method,headers=headers,url="{}{}".format(self.apiUrl,endpoint),data=json.dumps(body))
        if errors:
            response.raise_for_status()
        page = 2
        if not fullResponse or paginate:
            response = response.json()
        while paginate:
            if "?" in endpoint:
                url = "{}{}&page={}p10".format(self.apiUrl,endpoint,page)
            else:
                url = "{}{}?page={}p10".format(self.apiUrl,endpoint,page)
            results = requests.request(method,headers=headers,url=url,data=json.dumps(body))
            if errors:
                results.raise_for_status()
            response["data"].extend(results.json()["data"])
            if len(results.json()["data"]) < 10:
                paginate = False
            page+=1
        return response

    def asset(self,id=None,name=None):
        return Asset(self,id=id,name=name)