import requests
import Cipher as C

directoryServerUrl = 'http://localhost:3000/'
authServerUrl = 'http://localhost:4000/'


def login(args):
    if len(args) != 3:
        print 'login takes 2 arguments\nlogin $username $pword'
    else:
        r = requests.post((authServerUrl + 'login'), data={'username': args[1], 'password': args[2]})
        print r.text


def addUser(args):
    if len(args) != 4:
        print 'addUser takes 3 arguments\naddUser $username $pword $level'
    else:
        r = requests.post((authServerUrl + 'addUser'), data={'username': args[1], 'password': args[2],
                          'level': args[3]})
        print r.text


def addFile(args):
    if len(args) != 2:
        print 'add takes 1 argument\nadd $filename'
    else:
        path = 'files/' + args[1]
        f = open(path)
        r = requests.post((directoryServerUrl + 'add'), data={'filename': args[1], 'file': f.read()})
        print r.text


def listFiles(args):
    if len(args) != 1:
        print 'list takes no arguments'
    else:
        r = requests.get(directoryServerUrl)
        print r.text


def listUsers(args):
    if len(args) != 1:
        print 'listUsers takes no arguments'
    else:
        r = requests.get(authServerUrl)
        print r.text


def getFile(args):
    if len(args) != 2:
        print 'get takes 1 argument\nget $filename'
    else:
        r = requests.post((directoryServerUrl + 'get'), data={'filename': args[1]})
        if r.text == 'Invalid name':
            print 'Invalid name'
        else:
            path = 'files/' + args[1]
            f = open(path, 'w')
            f.write(r.text)
            print 'file downloaded'


def test(args):
    token = C.encrypt(args[1], 3)
    print token
    r = requests.post((authServerUrl + 'test'), data={'test': token})
    print r.text


def evaluate(command):
    args = command.split(' ')
    if args[0] == 'login':
        login(args)
    elif args[0] == 'addUser':
        addUser(args)
    elif args[0] == 'add':
        addFile(args)
    elif args[0] == 'list':
        listFiles(args)
    elif args[0] == 'listUsers':
        listUsers(args)
    elif args[0] == 'get':
        getFile(args)
    elif args[0] == 'test':
        test(args)
    else:
        print 'invalid command ' + args[0]

while True:
    command = raw_input('Enter command: ')
    evaluate(command)
