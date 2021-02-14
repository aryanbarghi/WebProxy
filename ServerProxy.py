import socket

# CE 4390.501 Web Proxy Project
# Aryan Barghi axb172530
# Arjun Bakhshi axb175430

# Create a server socket welcomeSocket, bind to a port p
# This is the welcoming socket used to listen to requests coming from a client

IP_ADDR = "127.0.0.1"
PORT = 1234

welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcomeSocket.bind((IP_ADDR, PORT))
# created list for cache
cache = []
while True:
    full_msg = ''
    destAddr = ''

    # Receive user input to determine whether to continue
    print('********************************************************************************')
    userIn = input('\nDo you want to continue? Y/N: ')
    if userIn == 'N' or userIn == 'n':
        break

    # Listen on welcomeSocket
    welcomeSocket.listen()
    print("WEB PROXY SERVER IS LISTENING")
    # Wait on welcomeSocket to accept a client connection

    # When a connection is accepted, a new client connection socket is created. Call that socket clientSocket
    clientSocket, address = welcomeSocket.accept()
    print('accepted')

    print("\nSTART OF MESSAGE RECEIVED FROM CLIENT\n")
    # Read the client request from clientSocket
    msg = clientSocket.recv(4096)
    full_msg += msg.decode("utf-8")



    # Split the message to extract the header
    msgArr = full_msg.splitlines()

    try:
        header = msgArr[0]
    except IndexError:
        continue


    # Parse the header to extract the method, dest address, HTTP version
    headerArr = header.split()  # splits at spaces; 0 = method, 1 = dest address, 2 = HTTP version

    method, destAddr, httpVer = headerArr

    full_msg_parsed = full_msg.split("\n")
    first_line_parsed = full_msg.split(' ')

    getRidOfHost = first_line_parsed[2].split('\n')

    first_line_parsed[1] = destAddr
    full_msg_parsed[0] = first_line_parsed[0] + " " + first_line_parsed[1] + " " + getRidOfHost[0]  # reset

    for i in range(len(full_msg_parsed)):
        print(full_msg_parsed[i])

    # Print the message received from the client
    print("END OF MESSAGE RECEIVED FROM CLIENT\n")

    # Process the request
    while True:
        # Print the extracted method, dest address and HTTP version
        print(f"[PARSED MESSAGE HEADER]:\nMETHOD = {method}, DESTADDRESS = {destAddr}, HTTPVersion = {httpVer}")

        inCache = False
        if method == 'GET':
            print('\nInside if method == GET\n')
            # Look up the cache to determine if requested object is in the cache
            print('Checking if object is in the cache')
            print('Length of cache: ' + str(len(cache)))
            for i in range(len(cache)):
                print('cache[' + str(i) + ']: ' + cache[i]
                      + '\ndestAddr: ' + destAddr)
                if cache[i] == destAddr:
                    inCache = True
                    break

            # if object is not in the cache, need to request object from the original server
            if not inCache:
                print("Object not found in the cache\n")

                # Create a serverSocket to send request to the original server
                serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Takes out www.
                destAddr = destAddr.replace("www.", "", 1)
                destAddrArr = destAddr.split('/')
                url = destAddrArr[1]
                newHeader = "GET http:/" + destAddr + " " + "HTTP/1.0" + "\n\n"

                # Print the request sent to the original server
                print("\n[PARSE REQUEST HEADER] URL is " + url +
                      "\n[PARSE REQUEST HEADER] FILENAME IS " + destAddr)

                serverSocket.connect((url, 80))
                print("Connected to original server")
                print("\nSend new header to original server: " + newHeader)

                fileobj = serverSocket.makefile('rw', 8)
                fileobj.write(newHeader)

                buffer = ""
                for block in fileobj.readlines():
                    buffer += block

                serverSocket.close()
                destAddrWithout = destAddr.replace('/','')
                tmpFile = open("./" + destAddrWithout,"wb")
                tmpFile.write(bytes(buffer,"utf-8"))
                tmpFile.close()

                print("Response RECEIVED FROM Original Server\n")
                # Print the message received from the Original Server
                print(buffer)

                print("End of Header from Original Server\n")

                responseArr = buffer.split(' ')
                if responseArr[1] == '200':
                    cache.append(destAddr)

                print('[Write file into Cache]: cache' + destAddr + "\n")
                serverSocket.close()

                print('Beginning of Cache')
                for i in range(len(cache)):
                    print(cache[i])
                print('End of Cache\n')

                print('Send message from Proxy to Client')

                clientSocket.send(bytes(buffer,"utf-8"))
                print(buffer.split('\n', 1)[0])

                print('End of Header')

            elif inCache:
                print("Object found in the cache")
                print("Found in Cache: cache" + destAddr)

            else:
                print("Something is wrong! probably with cache")
        elif method != 'GET':
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            destAddrArr = destAddr.split('/')

            url = destAddrArr[1]
            newHeader = method + ' ' + url + ' ' + httpVer

            # Print the request sent to the original server
            print("[PARSE REQUEST HEADER] Method is " + method +
                  "\n[PARSE REQUEST HEADER] URL is " + url +
                  "\n[PARSE REQUEST HEADER] FILENAME IS " + destAddr)

            print("\nREQUEST MESSAGE SENT TO ORIGINAL SERVER: \n" + full_msg)
            print("END OF MESSAGE SENT TO ORIGINAL SERVER\n")

            serverSocket.connect((url, 80))
            serverSocket.send(bytes(full_msg, "utf-8"))  # send request to webserver

            print("RESPONSE HEADER FROM ORIGINAL SERVER:\n")
            # Read response from the original server
            full_msg = ''
            msg = serverSocket.recv(4096)
            full_msg += msg.decode("utf-8")

            # Print the response header from the original server
            print(full_msg)

            print("END OF MESSAGE FROM SERVER TO PROXY")

            # Parse it to extract relevant components
            msgArr = full_msg.splitlines()
            header = msgArr[0]
            body = msgArr[1]
            headerAndBody = header + "\n" + body

            headerArr = header.split()
            errorCode = headerArr[1]

            # Print the response header from the proxy to the client
            print("\nRESPONSE HEADER FROM PROXY TO CLIENT:")

            print(headerAndBody)

            print("\nEND OF RESPONSE HEADER FROM PROXY TO CLIENT\n")

            # Compose response to the client and send on clientSocket
            clientSocket.send(bytes(headerAndBody, "utf-8"))  # send request to webserver

        break
    # Close the client socket
    clientSocket.close()
    # End of while true

# Close the welcome socket
welcomeSocket.close()