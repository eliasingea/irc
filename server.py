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
    connectionString = 'dbname=room_session user=postgres password=postgres host=localhost' # sorry Elias,
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
    # conn = connectToDB()
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    session['uuid']=uuid.uuid1()
    session['username']='starter name'
    print 'connected'
    
    users[session['uuid']]={'username':'New User'}
    updateRoster()
    
    # query2 = "SELECT username, message FROM messages WHERE room = %s;"
    # print cur.mogrify(query2, room); 
    # cur.execute(query2, room); 
    # results = cur.fetchall()
    # tmp = {}
    # if len(results) != 0: 
    #     print "it found it!"
    #     for r in results:
    #         print r
    #         tmp['name'] = r[0];
    #         tmp['text'] = r[1]; 
    #         emit('message', tmp)
    
    for message in messages:
        print 'This is my print in the for loop for message'
        #emit('message', message) # why did we comment this out??  Wouldn't this fix the blank text in the chat rooms issue? -kmh 3/23

@socketio.on('message', namespace='/chat')
def new_message(myTemp):
    #tmp = {'text':message, 'name':'testName'}
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    tmp = {'name':users[session['uuid']]['username'], 'text': myTemp['text']}
    #tmp = [myTemp['username'], myTemp['text'], myTemp['room']]; 
    messages.append(tmp)
    emit('message', tmp, broadcast=True)

    query = "INSERT INTO messages (username, message, room) VALUES (%s, %s, %s);" 
    print cur.mogrify(query, (myTemp['username'], myTemp['text'], myTemp['room']));
    cur.execute(query, (myTemp['username'], myTemp['text'], myTemp['room']));
   
    # query2 = "SELECT username, message FROM messages where room = %s;"
    # print cur.mogrify(query2, myTemp['room']); 
    # cur.execute(query2, myTemp['room']); 
    # results = cur.fetchall()
    
    # tmp2 = {}; 
    # if len(results) != 0: 
    #     print "it found it!"
    #     for r in results:
    #         print r
    #         tmp2['name'] = r[0];
    #         tmp2['text'] = r[1]; 
    #         emit('message', tmp2)
            
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
    query = "select users.username, users.password, room_info.room from users join users_room ON users.id = users_room.user_id join room_info ON users_room.room_id = room_info.id WHERE users.username= %s AND users.password = crypt(%s, password) AND room_info.room = %s; " 
    cur.execute(query, (myDict['username'], myDict['password'], myDict['room'])); 
    print cur.mogrify(query, (myDict['username'], myDict['password'], myDict['room'])); 
    print 'login as: ' + myDict['username']
    print 'the room is: ' + myDict['room'] # I never see this line get printed -kmh 3/23 Okay, I'm a dork.  It's printing and I'm dorking.
    result = cur.fetchall() 
    user = myDict['username']
    tmp = {}
    if len(result) == 0:
        log = False
        print 'its not working, we will create a user now'# should this be where we allow a pop-up for registration?-kmh
        usernameQuery = 'select username from users where username = %s;'
        print cur.mogrify(usernameQuery, (myDict['username'],)); 
        cur.execute(usernameQuery, (myDict['username'],)); 
        result2 = cur.fetchall()
        if len(result2) == 0:
           print 'we did not find the user: ' + myDict['username']
           insertQuery = "INSERT INTO users (username, password) VALUES (%s, crypt(%s, gen_salt('bf')));"
           cur.execute(insertQuery, (myDict['username'], myDict['password']));
           print cur.mogrify(insertQuery, (myDict['username'], myDict['password']));
           idNum = int; 
           selectQuery = 'SELECT id FROM users WHERE username = %s;'
           print cur.mogrify(selectQuery, (myDict['username'],));
           cur.execute(selectQuery, (myDict['username'],));
           idResult = cur.fetchall() 
           if len(idResult) != 0:
                
                for r in idResult:
                 idNum = r[0] 
           insertRoom = 'INSERT INTO users_room (user_id, room_id) VALUES (%s, 1);'
           print cur.mogrify(insertRoom, (idNum,)); 
           cur.execute(insertRoom, (idNum,)); 
           
           finalQuery = "select users.username, users.password, room_info.room from users join users_room ON users.id = users_room.user_id join room_info ON users_room.room_id = room_info.id WHERE users.username= %s AND users.password = crypt(%s, password) AND room_info.room = %s; " 
           cur.execute(query, (myDict['username'], myDict['password'], myDict['room'])); 
           print cur.mogrify(query, (myDict['username'], myDict['password'], myDict['room']));
           finalResult = cur.fetchall()
           if len(finalResult) != 0: 
               log = True
               emit('loggedin', log)
               emit('roomUpdate', 1)
           conn.commit(); 
            
        else:
            print 'you have entered the wrong password brah'
    else:
        log = True
        for r in result:
            print r; 
            tmp['room'] = r[2]; 
        emit('loggedin', log) 
        emit('roomUpdate', tmp)
        #on_login('hide');  # Kris stuck this here based on raz email **********************************
        
    query2 = "SELECT username, message FROM messages where room = %s;"
    print cur.mogrify(query2, myDict['room']); 
    cur.execute(query2, myDict['room']); 
    results = cur.fetchall()
    
    tmp2 = {}; 
    if len(results) != 0: 
        print "it found it!"
        for r in results:
            print r
            tmp2['name'] = r[0];
            tmp2['text'] = r[1]; 
            emit('message', tmp2)
    #users[session['uuid']]={'username':message}
    #updateRoster()
    
#oskcet stuff maybe?

@socketio.on('search', namespace='/chat')
def search(myDict):
    print 'hello we are in search' 
    print 'this is the search term' + myDict['search']
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   # tmp = {'name':users[session['uuid']]['username'], 'text':message}
    #query = "select username, message FROM messages WHERE message LIKE %s AND username = %s;"
    #cur.mogrify(query, (tmp['name'], tmp['text']));
    #cur.execute(query, (tmp['name'], tmp['text'])); 
    name = users[session['uuid']]['username']
    #text = socketio.messageSearch
    
    #go bacccccckkkkkk young Padawan to the old ways of key/pair beauty.
    #query = "select username, message FROM messages WHERE message LIKE %s AND username = %s AND room = %s;" 
    query = "select username, message FROM messages WHERE message LIKE %s AND room = %s;" 
    print cur.mogrify(query, (myDict['search'], myDict['room'])); 
    cur.execute(query, (myDict['search'], myDict['room'])); 

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