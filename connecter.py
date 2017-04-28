#!/usr/bin/python2.7

import sys
import socket
import getopt
import threading
import subprocess

# declare and initialize global vars
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    print "BHP Net Tool"
    print "Please choose whether listener mode or client mode."
    sys.exit(0)


def client_loop():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to our target host
        client.connect((target, port))

        while True:
            # now wait for data back
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            print response,

            # wait for more input
            buffer = raw_input("")
            buffer += "\n"
            #print "sent packet"
            # send it off
            client.send(buffer)

    except:
        print "[*] Exception! Exiting."

        # tear down the connection
        client.close()


def server_loop():
    global target
    global port

    # if no target is defined, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # spin off a new thread to handle the client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    # trim the newline
    #command = command.rstrip()

    # run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "[-] Failed to execute command\r\n"

    # send the output back to the client
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    if command:
        while True:
            # show a simple prompt
            client_socket.send("Remote server>")

            # now we revieve until we see a linefeed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # we have a valid command so execute it and send back the results
            response = run_command(cmd_buffer)

            # send the response back to the client
            client_socket.send(response)


def main():
    # needed to modify global copies of variables
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):  # if there is more than one element in the array
        usage()

    # read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        #elif o in ("-u", "--upload"):
        #    upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    # are we going to listen or just send data from stdin?
    if not listen and len(target) and port > 0:
        print "Press CTRL-C to escape."
        client_loop()

    if listen:
        server_loop()


main()
