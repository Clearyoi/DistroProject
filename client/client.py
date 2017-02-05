import requests
import json
import Cipher as C

directoryServerUrl = 'http://localhost:3000/'
authServerUrl = 'http://localhost:4000/'


class Client(object):

    def __init__(self):
        self.loggedIn = False
        self.key = 0
        self.token = ''

    def login(self, args):
        if len(args) != 3:
            print 'login takes 2 arguments\nlogin $username $pword'
        else:
            r = requests.post((authServerUrl + 'login'), data={'username': args[1], 'password': args[2]})
            if r.text == 'Invalid username or password':
                print r.text
            else:
                info = json.loads(r.text)
                self.key = info["key"]
                self.token = info["token"]
                self.loggedIn = True
                print 'logged in as \"' + args[1] + '\"'

    def addUser(self, args):
        if len(args) != 4:
            print 'addUser takes 3 arguments\naddUser $username $pword $level'
        else:
            r = requests.post((authServerUrl + 'addUser'), data={'username': args[1], 'password': args[2],
                              'level': args[3]})
            print r.text

    def addFile(self, args):
        if len(args) != 2:
            print 'add takes 1 argument\nadd $filename'
        else:
            path = 'files/' + args[1]
            f = open(path)
            r = requests.post((directoryServerUrl + 'add'), data={'token': self.token,
                              'filename': C.encrypt(args[1], self.key), 'file': C.encrypt(f.read(), self.key)})
            print r.text

    def listFiles(self, args):
        if len(args) != 1:
            print 'list takes no arguments'
        else:
            r = requests.post(directoryServerUrl, data={'token': self.token})
            print r.text

    def listUsers(self, args):
        if len(args) != 1:
            print 'listUsers takes no arguments'
        else:
            r = requests.get(authServerUrl)
            print r.text

    def getFile(self, args):
        if len(args) != 2:
            print 'get takes 1 argument\nget $filename'
        else:
            r = requests.post((directoryServerUrl + 'get'), data={'token': self.token, 'filename': C.encrypt(args[1], self.key)})
            if r.text == 'Invalid name':
                print 'Invalid name'
            else:
                path = 'files/' + args[1]
                f = open(path, 'w')
                f.write(r.text)
                print 'file downloaded'

    def evaluate(self, command):
        args = command.split(' ')
        if args[0] == 'login':
            self.login(args)
        elif not self.loggedIn:
            print 'You must log in to issue commands'
        elif args[0] == 'addUser':
            self.addUser(args)
        elif args[0] == 'add':
            self.addFile(args)
        elif args[0] == 'list':
            self.listFiles(args)
        elif args[0] == 'listUsers':
            self.listUsers(args)
        elif args[0] == 'get':
            self.getFile(args)
        else:
            print 'invalid command ' + args[0]

client = Client()
while True:
    command = raw_input('Enter command: ')
    client.evaluate(command)
