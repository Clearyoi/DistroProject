import requests


def evaluate(command):
    args = command.split(' ')
    if args[0] == 'login':
        if len(args) != 3:
            print 'login takes 2 arguments\nlogin $username $pword'
        else:
            r = requests.post('http://localhost:5000/login', data={'username': args[1], 'password': args[2]})
            print r.text
    elif args[0] == 'add':
        if len(args) != 2:
            print 'login takes 1 argument\nadd $filename'
        else:
            path = 'files/' + args[1]
            f = open(path)
            r = requests.post('http://localhost:5000/add', data={'filename': args[1], 'file': f.read()})
            # r = requests.post('http://posttestserver.com/post.php', data={'filename': args[1], 'file': f.read()})
            print r.text
    else:
        print 'invalid command ' + args[0]

while True:
    command = raw_input('Enter command: ')
    evaluate(command)
