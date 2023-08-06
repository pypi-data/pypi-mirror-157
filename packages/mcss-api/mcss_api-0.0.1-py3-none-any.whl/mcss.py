import requests
import json

def convertServer(serverJson, mcss):
    tmp_server = server(mcss)
    tmp_server.guid = serverJson["Guid"]
    tmp_server.status = serverJson["Status"]
    tmp_server.name = serverJson["Name"]
    tmp_server.description = serverJson["Description"]
    tmp_server.pathToFolder = serverJson["PathToFolder"]
    tmp_server.folderName = serverJson["FolderName"]
    tmp_server.creationDate = serverJson["CreationDate"]
    tmp_server.isSetToAutoStart = serverJson["IsSetToAutoStart"]
    tmp_server.keepOnline = serverJson["KeepOnline"]
    tmp_server.javaAllocatedMemory = serverJson["JavaAllocatedMemory"]
    tmp_server.javaStartupLine = serverJson["JavaStartupLine"]
    tmp_server.statistic = serverJson["Statistic"]

    return tmp_server


class MCSS():
    online = 1

    con_open = False
    host = None

    def __init__(self, host, quit) -> None:
        try:
            r = requests.get(host + "/")
        except:
            if quit == True:
                raise Exception("Invalid host")
            else:
                print("Invalid host")
                return None
        if r.status_code != 200:
            if quit == True:
                raise Exception("Invalid host")
            else:
                print("Invalid host")
                return None
        
        self.con_open = True
        self.host = host

    def auth(self, username, password) -> None:
        url = self.host + "/api/token"
        data = {
            "username": username,
            "password": password
        }
        r = requests.post(url, data=data)
        if r.status_code != 200:
            raise Exception("Authentication failed")
        return r.json()["access_token"]

    def getServers(self, token):
        url = self.host + "/api/servers"
        r = requests.get(url, headers={"Authorization": "Bearer " + token})
        if r.status_code != 200:
            raise Exception("Failed to get servers")

        servers = []
        for server in r.json():
            servers.append(convertServer(server, self))
        return servers

    def getServer(self, token, guid): 
        url = self.host + "/api/server"
        r = requests.get(url, headers={"Authorization": "Bearer " + token}, body={"guid": guid})
        if r.status_code != 200:
            raise Exception("Failed to get server")
        return convertServer(r.json(), self)

    def serverCount(self, token):
        url = self.host + "/api/servers/count"
        r = requests.get(url, headers={"Authorization": "Bearer " + token})
        if r.status_code != 200:
            raise Exception("Failed to get server count")
        return int(r.content.decode("utf-8"))

    def onlineServerCount(self, token):
        url = self.mcss_instance.host + "/api/servers/count/online"
        r = requests.get(url, headers={"Authorization": "Bearer " + token})
        if r.status_code != 200:
            raise Exception("Failed to get online server count")
        return int(r.content.decode("utf-8"))
    def serverCountOnline(self, token):
        return self.onlineServerCount(token)

class server():
    mcss_instance = None

    def __init__(self, mcss) -> None:
        self.mcss_instance = mcss

    guid = None
    status = 0
    name = None
    description = None
    pathToFolder = None
    folderName = None
    creationDate = None
    isSetToAutoStart = False
    keepOnline = 0
    javaAllocatedMemory = None
    javaStartupLine = None
    statistic = None
    
    def getStatus(self):
        switch = {
            0: "Offline",
            1: "Online",
            2: "Unknown",
            3: "Starting",
            4: "Stopping"
        }
        return switch.get(self.status, "Unknown")

    #
    # Server Actions
    #
    def action(self, action, token):
        url = self.mcss_instance.host + "/api/server/execute/action"
        r = requests.post(url, headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, json={"Guid": self.guid, "Action": action})
        if r.status_code != 200:
            raise Exception("Failed to " + action)

    def start(self, token):
        self.action("1", token)

    def stop(self, token):
        self.action("2", token)

    def restart(self, token):
        self.action("3", token)

    def kill(self, token):
        self.action("4", token)

    def command(self, command, token):
        url = self.mcss_instance.host + "/api/server/execute/command"
        r = requests.post(url, headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, json={"Command": command, "Guid": self.guid})
        if r.status_code != 200:
            raise Exception("Failed to execute command")

    def runCommand(self, command, token):
        self.command(command, token)
    def sendCommand(self, command, token):
        self.command(command, token)

    def massCommand(self, commands, token):
        url = self.mcss_instance.host + "/api/server/execute/commands"
        r = requests.post(url, headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, json={"Commands": commands, "Guid": self.guid})
        if r.status_code != 200:
            raise Exception("Failed to execute commands")
        return r.json()

    def commands(self, commands, token):
        self.massCommand(commands, token)


    #
    # Console
    #
    def getConsole(self, guid, lines, reversed, token):
        url = self.mcss_instance.host + "/api/server/console"
        r = requests.get(url, headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, json={"Guid": guid, "AmountOfLines": lines, "Reversed": reversed})
        if r.status_code != 200:
            raise Exception("Failed to get console")
        return r.json()

    def console(self, lines, reversed, token):
        return self.getConsole(self.guid, lines, reversed, token)

    def getConsoleOutdated(self, secondLastLine, lastLine, token):
        url = self.mcss_instance.host + "/api/server/console/outdated"
        r = requests.get(url, headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, json={"Guid": self.guid, "SecondLastLine": secondLastLine, "LastLine": lastLine})
        if r.status_code != 200:
            raise Exception("Failed to get console outdated")
        if r.content.decode("utf-8") == "true":
            return True
        else:
            return False

    
