import requests


def evaluate(command):
    args = command.split(' ')
    if args[0] == 'login':
        if len(args) != 3:
            print 'login takes 2 arguments\nlogin $username $pword'
        else:
            r = requests.post('http://localhost:5000/login', data={'username': args[1], 'password': args[2]})
            print r.text
    else:
        print 'invalid command ' + args[0]

while True:
    command = raw_input('Enter command: ')
    evaluate(command)
