# rally-test-tools
A set of python classes for running and verifying results for presets/supply chains in SDVI Rally.

## Installation
`pip install rallytt`

## Examples

Running a sandbox preset that returns the dynamic preset data:

    from rallytt import Rally

    RallyInstance = Rally(env="DEV")
    TestAsset = RallyInstance.asset()
    ExamplePreset = TestAsset.preset(name="00 Carson Sandbox rallytt")
    NewJob = ExamplePreset.run(dynamicPresetData={"message":"hello world"})
    print(NewJob.getArtifact("result",parse=True))
    TestAsset.delete()

The result of this would be:

    {"message":"hello world"}

Using the Test class to display test results:

    from rallytt import Test

    TestGroup = Test()
    expected = 1
    actual = 2
    TestGroup.test(expected == actual,"Basic equality test",expected=expected,actual=actual)
    expected = 1
    actual = 1
    TestGroup.test(expected == actual,"Basic equality test 2",expected=expected,actual=actual)
    TestGroup.print()

The result would look something like this:

    ---------------
    Name: Basic equality test
    Result: fail
    expected = 1
    actual = 2
    ---------------
    Name: Basic equality test 2
    Result: pass
    expected = 1
    actual = 1
    ---------------

## Classes

### **Test**  

#### *Properties*  

- **Test.tests** *Dictionary of all collected tests*  
- **Test.githubAction** *Boolean determining if the test is being run as part of a github action, so that the appropriate errors can be thrown if any. It is automatically set using an environment variable.*  

#### *Methods*  

- **Test.__init__()**  

- **Test.test(condition,testName,kwargs)**  
*Any keyword arguments will be displayed in the test results. This is useful for determining why tests might be failing*  

- **Test.print()**  
*Prints the results of the tests*  

---

### **Rally** 

#### *Properties*  

- **Rally.env** *Only necessary if using your rally-tools config.*  
- **Rally.apiUrl**  
- **Rally.apiKey**  

#### *Methods*  

- **Rally.__init__(configFromRallyTools=True,env="UAT",apiUrl=None,apiKey=None)**  
*Leaving configFromRallyTools set to "True" will load in API keys from your rally-tools config file, based on the "env" parameter you specified (default is UAT).*  

- **Rally.apiCall(method,endpoint,body={},paginate=False,fullResponse=False,errors=True)**  
*fullResponse determines if the .json() method (part of the requests package) is applied to the response object.*  
*If errors are true, any non 2-- status code will throw an error.*  

- **Rally.asset(id=None,name=None)**  
*Creates an instance of an Asset class which points to a real asset in Rally. If neither id or name are specified, a new asset will be created in Rally.*  

---

### **Asset**  

#### *Properties*  

- **Asset.Rally** *The Rally class instance associated with the asset.*  
- **Asset.name**  
- **Asset.id**  
- **Asset.metadata** *Not defined until the getMetadata() method is used.*  
- **Asset.workflowMetadata** *Not defined until the getWorkflowMetadata() method is used.*  

#### *Methods*  

- **Asset.__init__(Rally,id=None,name=None)**  
*Rally is an instance of a Rally class.*  
*If neither id or name are specified, a new asset will be created in Rally.*  

- **Asset.getName()**  
*Return the asset's name and store it in the 'name' property of the asset.*  

- **Asset.getMetadata()**  
*Return the asset's METADATA object and store it in the 'metadata' property of the asset.*  

- **Asset.getWorkflowMetadata()**  
*Return the asset's WORKFLOW_METADATA object and store it in the 'workflowMetadata' property of the asset.*  

- **Asset.delete()**  
*Delete the asset in Rally.*  

- **Asset.preset(id=None,name=None)**  
*Create a Preset class instance associated with the current Asset instance.*  
*An id or name must be specified.*  

- **Asset.supplychain(id=None,name=None)**  
*Create a SupplyChain class instance associated with the current Asset instance.*  
*An id or name must be specified.*  

- **Asset.listFiles()**  
*Return a list of File class instances belonging to all files in the Asset's inventory.*  

- **Asset.getFile(id=None,label=None)**  
*Create a File class instance from the label or id of the file.*  

---

### **Preset**  

#### *Properties*  

- **Preset.id**  
- **Preset.name**  
- **Preset.Rally** *The Rally class instance associated with the preset.*  
- **Preset.Asset** *The Asset class instance pointing to the asset that the preset will run on.*  

#### *Methods*  

- **Preset.__init__(Asset,id=None,name=None)**  
*Asset is an instance of an Asset class, and it will be the asset that the preset runs on.*  
*Either an id or name must be specified.*  

- **Preset.getName()**  
*Return the preset's name and store it in the 'name' property of the preset.*  

- **Preset.run(dynamicPresetData=None,timeout=5)**  
*Once the preset has completed (within the timout), an instance of a Job class is returned.*  

- **Preset.job(id=None,attributes=None)**  
*Returns an instance of a Job class based on the id specified.*  
*Attributes are optional, and would be a dicitonary of job attributes based on a response from the Rally API.*  

---

### **SupplyChain**  

#### *Properties*  

- **SupplyChain.id**  
- **SupplyChain.name**  
- **SupplyChain.Rally** *The Rally class instance associated with the supply chain.*  
- **SupplyChain.Asset** *The Asset class instance pointing to the asset that the supply chain will run on.*  

#### *Methods*  

- **SupplyChain.__init__(Asset,id=None,name=None)**  
*Asset is an instance of an Asset class, and it will be the asset that the supply chain runs on.*  
*Either an id or name of a rule must be specified.*  

- **SupplyChain.run(initData={},endingPreset=None,timeout=15)**  
*Returns a list of Job class instances representing all jobs that were completed in the suppy chain run.*  
*endingPreset is an instance of a Preset class that identifies a preset in the supply chain to end on. Once it is reached, all subsequent jobs in the supply chain will be cancelled*  

---

### **Job**  

#### *Properties*  

- **Job.id**  
- **Job.Rally** *The Rally class instance associated with the job.*  
- **Job.Asset** *The Asset class instance pointing to the asset that the job was run on.*  
- **Job.Preset** *The Preset class instance pointing to the preset that created the job.*  
- **Job.presetName** *The name of the preset that created the job.*  
- **Job.result** *The result of the job, could be pass, fail, cancelled, etc.*  
- **Job.dynamicPresetData**  

#### *Methods*  

- **Job.__init__(Preset,id=None,attributes=None)**  
*Asset is an instance of an Preset class, and it is the preset that produced the job.*  
*Attributes are optional, and would be a dicitonary of job attributes based on a response from the Rally API.*  

- **Job.getArtifact(name,parse=False)**  
*The name of the job artifact must be specified. Examples could be "result", "trace", "error", or "preset".*  
*If parse is set to True, the artifact will be parsed into a dictionary. If this is not possible, an error will be thrown.*  

---

### **File**  

#### *Properties*  

- **File.id**  
- **File.label**  
- **File.Rally** *The Rally class instance associated with the file.*  
- **File.Asset** *The Asset class instance pointing to the asset that the file belongs to.*  

#### *Methods*  

- **File.__init__(Asset,id=None,label=None)**  
*Asset is an instance of an Asset class, and it will be the asset that the file belongs to.*  
*An id or label must be specified.*  

- **File.getLabel()**  
*Return the file's label and store it in the 'label' property of the file.*  

- **File.getAnalyzeInfo()**  
*Return the analyze info of the file*  