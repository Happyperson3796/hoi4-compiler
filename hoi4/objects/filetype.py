
class fileType():
    def __init__(self, path: str):
        self.path = path
        self.tmp = path.endswith("_temp")
    def run(self): #Fires on Scan
        pass
    def clean(self):
        pass

    #Build-Only Functionality
    def prebuild(self): #Before scanning
        pass
    def build(self): #After Scanning, before collecting
        pass
    def postbuild(self): #After scanning & collecting
        pass

    def required_dir(self):
        return []
    def required_dir_error(self):
        print("File not in required directory! "+str(self.required_dir())+" "+self.path)

    def blocked_dir(self):
        return []
    def blocked_dir_error(self):
        print("File in a blocked directory! "+str(self.blocked_dir())+" "+self.path)
