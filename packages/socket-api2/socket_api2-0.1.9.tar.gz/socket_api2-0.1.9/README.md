# Socket Api 2

**Socket Api 2** creates the best connection between a server and client/clients.

Supported language is python 3. (Package wrote in 3.9-3.10.1)

- Checks if client is still connected.
- If server is not responding more, there is a feature that the client tries to reconnect. ***(optional)***
- Colored Logging in console/file. ***(optional)***

## Installation

Use this command:

    pip install socket-api2

## Change Log

0.1.9 (01/24/2022):

- Recv/Send speed upgrade
- Client connection management upgrade

0.1.8 (01/24/2022):

- Updated OOPClient from Server

0.1.7 (01/24/2022):

- Upgraded README.md
- Reworked response from recv

0.1.6 (01/24/2022):

- Upgraded README.md
- Fixed return issues

0.1.5 (01/24/2022):

- Added ngrok_url property to server

0.1.4 (01/24/2022):

- Fixed return errors
- Added shutdown function to server

0.1.3 (01/24/2022):

- Fixed ngrok usage

0.1.2 (01/07/2022):

- Optimized
- Added KeyboardInterrupt parsing.
- Fixed some bugs

0.1.1 (10/16/2021):

- Fixed bugs

## Examples

Difference between SEND_METHOD.default_send and SEND_METHOD.just_send, with the default send the program send a lenght of the message then send the message to know how many bytes we need to receive, but the just_send is just send the message. 

Example for Server:

    from socket_api2 import *

    server = Server(ip="auto", port=5555, client_timeout=10)

    @server.on_client_connect()
    def handling_client(client):
        while True:
            if client.is_connected:
                resp = client.recv(2048)
                
                if resp.error:
                    print("There is an error: " + resp.error)

                if resp.text == "hi":
                    client.send("hi 2", method=SEND_METHOD.default_send)
                
                elif resp.text == "I love u":
                    client.send("I love u too")

                else:
                    client.send("no hi", method=SEND_METHOD.just_send)
            else:
                break

    server.start()

Example for Client:

    from socket_api2 import *

    client = Client(target_ip="IP", target_port=5555, timeout=10)
    status_code, error = client.connect()
    if status_code == 200:
        client.send("hi")
        resp = client.recv(2048)

        if resp.code == 200:
            print("We successfully received a message. Message: " + resp.text)

        client.send("I love u", method=SEND_METHOD.just_send)
        client.recv(2048)
    else:
        outstr("ERROR", f"Something went wrong... --> {error}")