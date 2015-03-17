import os
import uuid
import psycopg2
import psycopg2.extras
from flask import Flask, session, render_template, request, redirect, url_for
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)


messages = [{'text':'test', 'name':'testName'}]
users = {}

def connectToDB():
    connectionString = 'dbname=session user=postgres password=postgres host=localhost' # sorry Elias,
                                                                        # it was already on the change
                                                                        # password function, so I had to
                                                                        # change it to "postgres" for now.
    try:
        return psycopg2.connect(connectionString)
    except:
        print("cant connect to Database")

def updateRoster():
    names = []
    for user_id in  users:
        print users[user_id]['username']
        if len(users[user_id]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[user_id]['username'])
    print 'broadcasting names'
    emit('roster', names, broadcast=True)
    

@socketio.on('connect', namespace='/chat')
def test_connect():
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    session['uuid']=uuid.uuid1()
    session['username']='starter name'
    print 'connected'
    
    users[session['uuid']]={'username':'New User'}
    updateRoster()

    query2 = "SELECT username, message FROM messages;"
    print cur.mogrify(query2); 
    cur.execute(query2); 
    results = cur.fetchall()
    tmp = {}
    if len(results) != 0: 
        print "it found it!"
        for r in results:
            print r
            tmp['name'] = r[0];
            tmp['text'] = r[1]; 
            emit('message', tmp)
    
    for message in messages:
        print 'This is my print in the for loop for message'
        #emit('message', message)

@socketio.on('message', namespace='/chat')
def new_message(message):
    #tmp = {'text':message, 'name':'testName'}
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   # tmp = {'text':message, 'name':users[session['uuid']]['username']}
    tmp = {'name':users[session['uuid']]['username'], 'text':message}
    messages.append(tmp)
    emit('message', tmp, broadcast=True)

    query = "INSERT INTO messages (username, message) VALUES (%s, %s);" 
    print cur.mogrify(query, (tmp['name'], tmp['text']));
    cur.execute(query, (tmp['name'], tmp['text']));
   
    
    
    # query2 = "SELECT username, message FROM messages;"
    # print cur.mogrify(query2); 
    # cur.execute(query2); 
    # results = cur.fetchall()
    
    # if len(results) != 0: 
    #     print "it found it!"
    #     for r in results:
    #         print r
    #         tmp['name'] = r[0];
    #         tmp['text'] = r[1]; 
    #         emit('message', tmp)
            
    cur.close();
    conn.commit();
    
    #connect to db?
    #pull user and message itself
    #use $scope.text - it is already emmited?
    #we should be able to just get it. - like login myDict
    
    #cur.execute insert messages
    #cur.close stuff
    #cur.commit
    #ugh
    
@socketio.on('identify', namespace='/chat')
def on_identify(message):
    print 'identify' + message
    users[session['uuid']]={'username':message}
    updateRoster()


@socketio.on('login', namespace='/chat')
def on_login(myDict):
    print 'login' + myDict['username'] # kris commented this out on 3/16, no idea what that weird junk is
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "SELECT username, password FROM users WHERE username = %s AND password = crypt(%s, password);" 
    cur.execute(query, (myDict['username'], myDict['password'])); 
    print 'login as: ' + myDict['username']
    result = cur.fetchall() 

    if len(result) == 0:
        log = False
        
        print 'its not working'
    else:
        log = True
        emit('loggedin', log) 
        #on_login('hide');  # Kris stuck this here based on raz email **********************************
        
        
    #users[session['uuid']]={'username':message}
    #updateRoster()
    
#oskcet stuff maybe?

@socketio.on('search', namespace='/chat')
def search(messageSearch):
    print 'hello we are in search' 
    print 'this is the search term' + messageSearch
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   # tmp = {'name':users[session['uuid']]['username'], 'text':message}
    #query = "select username, message FROM messages WHERE message LIKE %s AND username = %s;"
    #cur.mogrify(query, (tmp['name'], tmp['text']));
    #cur.execute(query, (tmp['name'], tmp['text'])); 
    name = users[session['uuid']]['username']
    #text = socketio.messageSearch
    query = "select username, message FROM messages WHERE message LIKE %s AND username = %s;" 
    print cur.mogrify(query, (messageSearch, name)); 
    cur.execute(query, (messageSearch, name)); 

    result = cur.fetchall()
    if len(result) != 0:
        print 'it found it!' 
        for r in result:
            print r
            tmp = {}
            tmp['name'] = r[0]
            tmp['text'] = r[1]
            emit('searchBox', tmp)
        
    else: 
        print 'it did not find anything'


@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print 'disconnect'
    if session['uuid'] in users:
        del users[session['uuid']]
        updateRoster()

@app.route('/')
def hello_world():
    print 'in hello world'
    return app.send_static_file('index.html')
    return 'Hello World!'

@app.route('/js/<path:path>')
def static_proxy_js(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('js', path))
    
@app.route('/css/<path:path>')
def static_proxy_css(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('css', path))
    
@app.route('/img/<path:path>')
def static_proxy_img(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('img', path))
    
if __name__ == '__main__':
    print "A"

    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))