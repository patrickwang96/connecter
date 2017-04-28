# connecter
_A light weight ssh-like connecting script_

connecter.py is a python script i wrote. It enables a ssh-like function and also you can do file uploading. However, you can specify whether you want to authenticate client side or not. It can also require password for authentication and encrypt messages using a 256bit AES.  
This script can help you quickly control a remote host or upload file in a local area network (for example, control a raspberry pi within your home router), whether encrypted or not.

## Requirment
connecter.py is writen in python2.7 and requires module 'Pycrypto' for all the cryptography utilities.  
Remote host (raspberry pi) is required for running this script's listener mode (and command mode) in background.

## Function
Right now, the command shell function is roughly completed. However, the encryption utilities are still under construction. After complete the encryption utilities, a file upload (whether encrypted or not) will be further implemented.

## Demo
Just for demonstration purpose. Let's start two terminal at your Laptop. Let the first terminal runn connecter.py in listener mode (run as server) and the other terminal run in client mode.

```
# cmd for the first terminal.
./connecter.py -l -t localhost -p 1234 -c

# cmd for the second terminal.
./connecter.py -t localhost -p 1234
```

## Documentation
* **-l or --listen** connecter.py is running as a TCP server, waiting for client to conenct. Once a client is connected, connecter.py will start a new thread to handle the command.
* **-t or --target** connecter.py will accept -t as the standard IPv4 address or domain name.
* **-p or --port** connecter.py will accept -p as the port number.
* **-c or --commandshell**  connecter.py is waiting for a client to connect and iterate as a shell
