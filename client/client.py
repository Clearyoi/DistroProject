import requests

directoryServerUrl = 'http://localhost:3000/'
authServerUrl = 'http://localhost:4000/'


def evaluate(command):
    args = command.split(' ')
    if args[0] == 'login':
        if len(args) != 3:
            print 'login takes 2 arguments\nlogin $username $pword'
        else:
            r = requests.post((authServerUrl + 'login'), data={'username': args[1], 'password': args[2]})
            print r.text
    elif args[0] == 'add':
        if len(args) != 2:
            print 'add takes 1 argument\nadd $filename'
        else:
            path = 'files/' + args[1]
            f = open(path)
            r = requests.post((directoryServerUrl + 'add'), data={'filename': args[1], 'file': f.read()})
            print r.text
    elif args[0] == 'list':
        if len(args) != 1:
            print 'list takes no arguments'
        else:
            r = requests.get(directoryServerUrl)
            print r.text
    elif args[0] == 'get':
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
    else:
        print 'invalid command ' + args[0]

while True:
    command = raw_input('Enter command: ')
    evaluate(command)
