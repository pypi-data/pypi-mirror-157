import os, sys, keyboard, json, re
from subprocess import Popen, PIPE, run, DEVNULL
from argparse import ArgumentParser

from .shared_functions import Loading, runCmd, promptPyInquirer, defaultCommit

def main():
    args = takeArgs()
    checkSoftware("git", "git --help")
    checkSoftware("heroku", "heroku --help", "https://devcenter.heroku.com/articles/heroku-cli#download-and-install")
    args["path"] = os.path.abspath(args["path"])
    os.chdir(args["path"]) #changing to path
    print("Directory changed to "+os.getcwd()) #informing the user that the directory has changed
    if args["cmd"] == "update":
        update(args)
        return
    elif args["cmd"] == "delete":
        delete(args)
    elif args["cmd"] == "logs":
        herokuLogs()
    elif args["cmd"] == "create-update":
        create_update(args)

def create_update(args):
    if args["framework"] == "flask":
        __Flask__(args["path"])
    elif args["framework"] == "nodejs":
        __Nodejs__(args["path"])
    defaultCommit(args)
    masterToMain()
    if not herokuIsLoggedIn(args["new_login"]):
        herokuLogin()
    herokuAppExistence(args["rename"])
    herokuRemote(args)
    herokuPush()
    print("Done!")
    herokuOpen()

def update(args):
    defaultCommit(args)
    if not herokuIsLoggedIn(args["new_login"]):
        herokuLogin()
    masterToMain()
    herokuRemote(args)
    herokuPush()
    herokuOpen()

def delete(args:dict):
    if not herokuIsLoggedIn(args["new_login"]):
        herokuLogin()
    runCmd("heroku apps:destroy")
    sys.exit(0)

def takeArgs():
    parser = ArgumentParser(prog="heroku-deployer",
    usage="""You basically enter one of the following commands:
        ¤ create-update (which is the default one)
        ¤ update (to update an existing heroku-website)
        ¤ delete (to delete an existing heroku-website)
        ¤ logs (to log if there were any errors)
    then you need to specify the path by using the -p or --path argument.
    then you need to specify the language or framework you're using. e.g: nodejs flask etc...""",
         description="%(prog)s <commands> [options]")
    parser.add_argument("cmd", nargs="?", choices=["create-update", "update", "delete", "logs"], help="", default="create-update")
    parser.add_argument("-p", "--path", help="path of the folder you want to deploy.", required=True)
    parser.add_argument("-lang", "--language", dest="framework", default="flask", choices=["flask","nodejs"], help="language or the framework you're using.")
    parser.add_argument("-new-login", action="store_true", help="Force a new login")
    parser.add_argument("-no-cache", action="store_true", help="Removes the app name if it is cached")
    parser.add_argument("-rename", action="store_true", help="Rename an existing app")
    return vars(parser.parse_args())

def herokuLogin():
    runCmd("heroku login -i" ,error="You have not been authenticated to heroku!")

def herokuIsLoggedIn(new_login):
    if new_login:
        return 
    loading = Loading(startText="Checking if already authenticated", stopText="", timeout=0.4)
    loading.start()
    output = runCmd("heroku whoami", stdout=PIPE, stderr=PIPE, quitOnError=False, loading=loading)
    loading.stop()
    if output:
        print(f"Logged in as {output}")
        return True
    return False
    # process = Popen("heroku whoami", shell=True, stdout=PIPE, stderr=PIPE)
    # output = [i.decode() for i in process.communicate()][0]
    # process.wait()
    # if process.returncode == 0:
    #     print(f"Logged in as {output}")
    #     return True
    # return False
def getAppName(message="Enter your app name :") -> str:
    appName = promptPyInquirer({
        "name": 'appName',
        "message": message,
        "type": "input",
        "validate": lambda val: "Does not match the pattern" if (len(val)==0 or re.search("[^A-Za-z0-9\-]", val)) else True,
    })['appName']
    return appName

def herokuAppExistence(rename):
    """
    Checks if the app exists and checks if the rename option has been added.
    """
    isCreated = input("Have you created the app yet (y/n): ").lower()
    if isCreated == "n":
        appName = input("What do you want to name your app: ")
        region = promptPyInquirer({
            "name": "region",
            "type": "list",
            "message": "Choose a region :",
            "choices": ["eu", "us"],
        })["region"]
        runCmd(f"heroku create {appName} --region {region}")
    elif isCreated == "y":
        if rename:
            appName = getAppName("What do you want to rename your app :")
            runCmd(f"heroku apps:rename {appName} ")
    else:
        print("Invalid answer!")
        sys.exit(3)

def herokuOpen():
    print("Do you want to open the app now? press any key to open it or q to exit the script: ")
    if keyboard.read_key() == "q":
        sys.exit(0)
    opening = Loading(startText="Opening", stopText="Opened")
    opening.start()
    runCmd("heroku open", loading=opening)
    opening.stop()
        

def herokuRemote(args):
    noCache = args["no_cache"]
    if noCache:
        appName = getAppName()
        runCmd(f"heroku git:remote -a {appName}")
    else:
        hasRemote = runCmd("git remote -v", stdout=PIPE, stderr=PIPE)
        if not hasRemote:
            appName = getAppName()
            runCmd(f"heroku git:remote -a {appName}")

def herokuPush():
    runCmd("git push heroku main")

def herokuLogs():
    runCmd("heroku logs")

def checkModule(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False

def handleGitInit(path):
    files_dirs = os.listdir(path)
    if ".git" not in files_dirs:
        runCmd("git init")

def checkSoftware(name, cmd, url=""):
    err = f"It seems that {name} is not in your machine, please make sure to download it first"
    err += f"\n you can find it at {url}" if url else ""
    runCmd(cmd, stdout=DEVNULL,
        error= err
    )

def masterToMain():
    out = runCmd("git branch", stdout=PIPE, stderr=PIPE)
    if "main" in out:
        return
    runCmd("git branch -m master main", stdout=PIPE, stderr=PIPE)
    runCmd("git checkout main", stdout=DEVNULL, stderr=PIPE)

def checkCommit():
    out = runCmd("git status", stdout=PIPE, stderr=PIPE)
    if "nothing to commit, working tree clean" in out:
        print(out)
        return False
    return True

class __Flask__:
    def __init__(self, path):
        self.path = path
        if self.checkFiles() is None:
            sys.exit(1)

    def checkFiles(self):
        files = [file.lower() for file in os.listdir(self.path)]
        required = ["runtime.txt", "requirements.txt", "Procfile"]
        for require in required:
            if require.lower() not in files:
                stop = self.missingFile(require)
                if stop:
                    print("script has been stopped, needs", require)
                    return None
        return True

    def missingFile(self, fileName):
        if fileName == "requirements.txt":
            print("requirements.txt is missing in your directory.\nplease run in your commandline/terminal type:'py freeze > requirements.txt'")
            return True
        if fileName == "runtime.txt":
            version = self._getRunTime()
            self.writeFile(fileName, "python-"+version)
        elif fileName == "Procfile":
            app = self._getProcfile()
            self.writeFile(fileName, f"web: gunicorn {app}:app")
        return False
            
    def _getRunTime(self):
        prompt = """
        Choose a python version:
        1. 3.9.4
        2. 3.8.9
        3. 3.7.10
        4. 3.6.13
        """
        print(prompt)
        choice = input("=> ")
        options = {
            "1": "3.9.4",
            "2": "3.8.9",
            "3": "3.7.10",
            "4": "3.6.13"
        }
        return options[choice]

    def _getProcfile():
        fileName = input("What is your main file name: ")
        return fileName.rsplit(".")[0]

    def writeFile(fileName, content):
        with open(fileName, "w") as f:
            f.write(content)

class __Nodejs__:
    def __init__(self,path):
        self.path = path
        checkSoftware("nodejs", "node -v")
        self.checkFiles()

    def checkFiles(self):
        files = [file for file in os.listdir(self.path)]
        required = ["Procfile","package.json", ".gitignore"]
        for r in required:
            if r not in files:
                self.missingFile(r)
        
        self.npmStart(self.path+os.sep+"package.json")
        self.gitignoreNodeModules(self.path+os.sep+".gitignore")

    def missingFile(self, filename):
        if filename == "package.json":
            loading = Loading(startText="Creating package.json", stopText="")
            loading.start()
            runCmd("npm init -y", loading=loading)
            loading.stop()
        elif filename == ".gitignore":
            f = open(self.path+os.sep+".gitignore", "w")
            f.close()
        elif filename == "Procfile":
            with open(self.path+os.sep+"Procfile", "w") as f:
                f.write("web: npm start")

    def gitignoreNodeModules(self, gitignorePath):
        with open(gitignorePath) as f:
            content = f.read()
            if not re.search("^(/node_modules|node_modules/|[\\\]node_modules|node_modules[\\\])$", content,re.M):
                content = content + "/node_modules" if len(content)==0 or (content[-1] == "\n") else content + "\n/node_modules"
        with open(gitignorePath, "w") as f:
            f.write(content)



    def npmStart(self, packagePath):
        with open(packagePath) as f:
            # print(f.read())
            packageDict = json.load(f)
            if "engines" not in packageDict:
                packageDict["engines"] = {}
            if "node" not in packageDict["engines"]:
                nodeVersion = re.findall("^v(\d+)",runCmd("node -v", stdout=PIPE, stderr=PIPE))
                packageDict["engines"]["node"] = nodeVersion[0] if len(nodeVersion) > 0 else ""
            if "scripts" not in packageDict:
                packageDict["scripts"] = {}
                self.mainFile = input("Main file name that's gonna run: ")
                packageDict["scripts"]["start"] = "node "+self.mainFile
            elif "scripts" in packageDict and type(packageDict["scripts"] is dict):
                if not "start" in packageDict["scripts"]:
                    self.mainFile = input("Main file name that's gonna run: ")
                    packageDict["scripts"]["start"] = "node "+self.mainFile

        with open(packagePath, "w") as f:
            f.write(json.dumps(packageDict, indent=4))
        
                
if __name__ == "__main__":
    main()