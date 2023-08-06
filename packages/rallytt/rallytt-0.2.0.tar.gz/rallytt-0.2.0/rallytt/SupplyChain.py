from time import sleep,time
import urllib.parse
import json

class SupplyChain:

    def __init__(self,Asset,id=None,name=None):
        if not id and not name:
            raise TypeError("Please specify either the name or id of the rule that starts the supply chain")
        self.Rally = Asset.Rally
        self.Asset = Asset
        self.id = id
        self.name = name
        if not id:
            try:
                self.id = self.Rally.apiCall("GET","/workflowRules?filter=name={}".format(urllib.parse.quote_plus(name)))["data"][0]["id"]
            except IndexError:
                raise ValueError("Could not find rule with name '{}'".format(name)) from None

    def run(self,initData={},endingPreset=None,timeout=15):
        baseWorkflow = self.Rally.apiCall("POST","/workflows",body={"data":{"type":"workflows", "attributes":{"initData":json.dumps(initData)}, "relationships": {"movie":{"data":{"id": self.Asset.id,"type": "movies",}},"workflowRule":{"data": {"id": self.id, "type": "workflowRules",}}}}})["data"]
        jobs = []
        processedJobs = []
        processedWorkflows = []
        delay = 5
        cancelAll = False
        start_time = time()
        while (start_time-time() < timeout) and not cancelAll:
            sleep(delay)
            baseWorkflow = self.Rally.apiCall("GET","/workflows/{}".format(baseWorkflow["id"]))["data"]
            workflows = [baseWorkflow]
            childWorkflows = [item for item in self.Rally.apiCall("GET","/workflows?filter=assetId={}".format(self.Asset.id),paginate=True)["data"] if item["relationships"]["baseWorkflow"]["data"]["id"] == baseWorkflow["id"] and item["id"] != baseWorkflow["id"]]
            workflows.extend(childWorkflows)
            if set([item["id"] for item in workflows]).issubset(set(processedWorkflows)):
                return jobs
            for workflow in workflows:
                if workflow["id"] not in processedWorkflows:
                    jobIds = [item["id"] for item in workflow["relationships"]["jobs"]["data"]]
                    for jobId in jobIds:
                        if jobId not in processedJobs:
                            job = self.Rally.apiCall("GET","/jobs/{}".format(jobId))
                            if job["data"]["attributes"]["status"] == "Complete":
                                processedJobs.append(jobId)
                                presetId = job["data"]["relationships"]["preset"]["data"]["id"]
                                jobPreset = self.Asset.preset(id=presetId)
                                jobPreset.getName()
                                newJob = jobPreset.job(id=jobId,attributes=job["data"]["attributes"])
                                jobs.append(newJob)
                                if endingPreset:
                                    if jobPreset.id == endingPreset.id:
                                        cancelAll = True
                    if workflow["attributes"]["state"] == "Complete":
                        processedWorkflows.append(workflow["id"])
        if cancelAll:
            baseWorkflow = self.Rally.apiCall("GET","/workflows/{}".format(baseWorkflow["id"]))["data"]
            workflows = [baseWorkflow]
            childWorkflows = [item for item in self.Rally.apiCall("GET","/workflows?filter=assetId={}".format(self.Asset.id),paginate=True)["data"] if item["relationships"]["baseWorkflow"]["data"]["id"] == baseWorkflow["id"] and item["id"] != baseWorkflow["id"]]
            workflows.extend(childWorkflows)
            for workflow in workflows:
                if workflow["id"] not in processedWorkflows:
                    jobIds = [item["id"] for item in workflow["relationships"]["jobs"]["data"]]
                    for jobId in jobIds:
                        if jobId not in processedJobs:
                            self.Rally.apiCall("PATCH","/jobs/{}".format(jobId),body={"data":{"type":"jobs", "attributes":{"state":"Cancelled"}}},fullResponse=True)
        return jobs