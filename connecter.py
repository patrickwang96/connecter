#!/usr/bin/python2.7

import sys
import socket
import getopt
import threading
import subprocess
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import json

# declare and initialize global vars
listen = False
command = False
upload = False
secured = False
execute = ""
target = ""
upload_destination = ""
port = 0

# crypto part variable
# key for server
# default password for server side is '123'
hashed_password = SHA256.new('123').digest()
iv = 'Thisisa16byteslo'
pading = "p" # padding is for padding the string when string length doesnot match with 16x
plaintext_key = ""

def test_password(plaintext_key):
    print "comparing session key"
    return SHA256.new(plaintext_key).digest() == hashed_password


def get_key(plaintext_key):
    return SHA256.new(plaintext_key).digest()


def encrypt(plaintext_key, msg):
    key = get_key(plaintext_key)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    length = len(msg)
    while len(msg)%16!=0:
        msg += pading
    data = {
        'cipher': cipher.encrypt(msg).encode('base64'),
        'length': length
    }
    return json.dumps(data)


def decrypt(d):
    data = json.loads(d)
    ciphertext = data['cipher'].decode('base64')
    length = data['length']
    cipher = AES.new(hashed_password, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext[0:length]

# above is the pycrypto part
# ================


def usage():
    print "Connecter.py"
    print "Please input the flag conrrectly."
    print "If you have any doubt, please infer to https://github.com/patrickwang96/connecter "
    sys.exit(0)


def client_loop():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to our target host
        client.connect((target, port))
        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            print response,

            buffer = raw_input("")

            ciphertext = encrypt(plaintext_key,buffer)
            packet = {
                'key': plaintext_key,
                'text': ciphertext
            }
            # getting json string
            send = json.dumps(packet)
            send += '\n'

            client.send(send)

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

    while True:
        client_socket.send("Remote>")

        cmd_buffer = ""
        while "\n" not in cmd_buffer:
            cmd_buffer += client_socket.recv(1024)

        packet = json.loads(cmd_buffer)
        recv_key = packet['key']
        ciphertext = packet['text']
        if(test_password(recv_key) == True):
            cmd = decrypt(ciphertext)

            response = run_command(cmd)

        else:
            response = 'Wrong key!'

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
    global hashed_password
    global secured
    global plaintext_key

    if not len(sys.argv[1:]):  # if there is more than one element in the array
        usage()

    # read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cus:k:",
                                   ["help", "listen", "execute=", "target=", "port=", "command", "upload","secure=","key="])
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
        elif o in ("-s", "--secure"):
            hashed_password = SHA256.new(str(a)).digest()
            secured = True
        elif o in ("-k", "--key"):
            plaintext_key = a
        else:
            assert False, "Unhandled Option"

    # are we going to listen or just send data from stdin?
    if not listen and len(target) and port > 0:
        print "Press CTRL-C to escape."
        client_loop()

    if listen:
        server_loop()


main()
