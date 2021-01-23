import time
import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT=6060
SERVING_ADDR=(IP,PORT)
SERVICE=True
HEADER_LENGTH=10
FORMAT='utf-8'
WELCOME_BANNER='Welcome To the Server'
COMMANDS=['!DISCONNECT!','!SHUTDOWN!','rUaLiVe?']
CLIENTS=[]
CONFIGS={}
STATUS={True : "IDLE" , False : "DISCONNECTED"}
BROADCASTQUEUE_CLIENT=[]
BROADCASTQUEUE_MESSAGE=[]
SERVER_SOCKET=None
MAX_CON_RETRY=5
TTL=100


def logger(TYPE :int ,MESSAGE) -> None:
    if TYPE == 0 :
        print(MESSAGE)


def SERVICE_DISCOVERY():
    global SERVICE,FORMAT,IP,PORT
    logger(0,'[STARTING] Discovery Service has Started ...')
    NDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    NDP.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
    NDP.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    NDP.bind(('',PORT))
    NDP.settimeout(5)
    while SERVICE:
        try:
            MSG , ADDR = NDP.recvfrom(10)
            if MSG and MSG.decode(FORMAT) == 'NDP:HI' :
                logger(0,f'[REQUEST] Discovery Service Request from {ADDR}')
                NDP.sendto(bytes(IP,FORMAT),('<broadcast>',PORT+1))
        except socket.timeout :
            pass
    NDP.close()


def SERVICE_PROVIDER():
    global SERVING_ADDR,SERVICE,CLIENTS,SERVER_SOCKET
    logger(0,'[STARTING] Messaging Service has Started ...')
    SERVER = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    SERVER_SOCKET = SERVER
    CONFIGS[SERVER_SOCKET]='129Server'
    SERVER.bind(SERVING_ADDR)
    SERVER.listen()
    SERVER.settimeout(5)
    while SERVICE:
        try :
            CLIENT , ADDR = SERVER.accept()
            logger(0,f'[CONNECTION] New Connection from {ADDR} ...')
            CLIENTS.append(CLIENT)
            CLIENT_THREAD = threading.Thread(target=CLIENT_HANDLER,args=(CLIENT,ADDR))
            CLIENT_THREAD.start()
        except socket.timeout :
            pass


def CLIENT_HANDLER(CLIENT : socket.socket,ADDR):
    global TTL,SERVICE,WELCOME_BANNER,CONFIGS,COMMANDS,BROADCASTQUEUE_CLIENT,BROADCASTQUEUE_MESSAGE,SERVER_SOCKET
    ALIVE = True
    CONNECTED = True
    SEND_TEXTMSG(CLIENT,WELCOME_BANNER)
    while CONNECTED :
        CONFIG=RECIVE_TEXTMSG(CLIENT)
        if not CONFIG :
            ALIVE = False
            CONNECTED = CHECK_CONNECTION(CLIENT)
        else:
            ALIVE =True
            CONNECTED = False
            CONFIGS[CLIENT]=CONFIG
            BROADCASTQUEUE_CLIENT.append(SERVER_SOCKET)
            BROADCASTQUEUE_MESSAGE.append(f'{WELCOME_BANNER} {CONFIG[3:]}')
    try:
        CLOCK_START=time.perf_counter()
        while ALIVE and SERVICE:
            MESSAGE=RECIVE_TEXTMSG(CLIENT)
            if MESSAGE:
                CLOCK_START=time.perf_counter()
                print(ADDR,MESSAGE)
                if MESSAGE not in COMMANDS :
                    BROADCASTQUEUE_CLIENT.append(CLIENT)
                    BROADCASTQUEUE_MESSAGE.append(MESSAGE)
                elif MESSAGE == '!SHUTDOWN!' :
                    logger(0,f'[SHUTDOWN] Client Side shutdown initated from {ADDR}')
                    BROADCASTQUEUE_CLIENT.append(SERVER_SOCKET)
                    BROADCASTQUEUE_MESSAGE.append(f'Server is being Shutdown by [{CONFIG[3:]}] please do !DISCONNECT! or \'exit\'')
                    SERVICE=False
                    ALIVE=False
                elif MESSAGE == '!DISCONNECT!':
                    BROADCASTQUEUE_CLIENT.append(SERVER_SOCKET)
                    BROADCASTQUEUE_MESSAGE.append(f'{CONFIG[3:]} has left ...')
                    ALIVE=False
                elif MESSAGE == 'rUaLiVe?':
                    SEND_TEXTMSG(CLIENT,'True')
            else:
                CLOCK_END = time.perf_counter()-CLOCK_START
                if CLOCK_END > TTL :
                    CHECK = CHECK_CONNECTION(CLIENT)
                    if not CHECK :
                        ALIVE = False
                    else:
                        CLOCK_START = time.perf_counter()
                else:
                    pass
    except Exception as e :
        print(e)
        _=input()
    finally:
        CLIENTS.remove(CLIENT)
        CLIENT.close()
        logger(0,f'[DISCONNECTION] Client {CONFIG[3:]} Disconnected ...')


def SERVICE_BROADCASTER():
    global SERVICE,BROADCASTQUEUE_CLIENT,BROADCASTQUEUE_MESSAGE,CONFIGS
    logger(0,'[STARTING] Broadcast Service has Started ...')
    while SERVICE :
        if BROADCASTQUEUE_CLIENT :
            CLIENT = BROADCASTQUEUE_CLIENT.pop(0)
            MESSAGE = BROADCASTQUEUE_MESSAGE.pop(0)
            CONFIG = CONFIGS[CLIENT]
            for CL in CLIENTS :
                SEND_TEXTMSG(CL,CONFIG)
                SEND_TEXTMSG(CL,MESSAGE)


def CHECK_CONNECTION(CLIENT : socket.socket):
    global CONFIGS,STATUS
    logger(0,f'Checking Connection for {CONFIGS[CLIENT][3:]} ...')
    SEND_TEXTMSG(CLIENT,'rUaLiVe?')
    OUT=bool(RECIVE_TEXTMSG(CLIENT))
    logger(0,f'{CONFIGS[CLIENT][3:]}  is {STATUS[OUT]}')
    return OUT


def SEND_TEXTMSG(CLIENT:socket.socket, MESSAGE : str):
    global FORMAT,HEADER_LENGTH
    FINAL_MESSAGE=MESSAGE.encode(FORMAT)
    HEADER_MESSAGE=str(len(FINAL_MESSAGE)).encode(FORMAT)
    HEADER_MESSAGE+=(b' '*(HEADER_LENGTH-len(HEADER_MESSAGE)))
    try:
        CLIENT.send(HEADER_MESSAGE)
        CLIENT.send(FINAL_MESSAGE)
    except:
        pass


def RECIVE_TEXTMSG(CLIENT:socket.socket) -> str:
    global SERVICE,FORMAT,HEADER_LENGTH,MAX_CON_RETRY
    FINAL = None
    MESSAGE_CONFIRM = False
    CONN_RETRY=0
    CLIENT.settimeout(5)
    while not MESSAGE_CONFIRM and SERVICE:
        try:
            MESSAGE_LEN = CLIENT.recv(HEADER_LENGTH)
            if MESSAGE_LEN:
                CAPTURE_LEN = int(MESSAGE_LEN.decode(FORMAT))
                MESSAGE = CLIENT.recv(CAPTURE_LEN)
                FINAL = MESSAGE.decode(FORMAT)
                MESSAGE_CONFIRM = True
        except ConnectionResetError:
            MESSAGE_CONFIRM = True
        except ConnectionAbortedError:
            MESSAGE_CONFIRM = True    
        except socket.timeout:
            CONN_RETRY+=1
            if not SERVICE :
                MESSAGE_CONFIRM = True
            if CONN_RETRY>MAX_CON_RETRY:
                MESSAGE_CONFIRM = True
    CLIENT.settimeout(None)
    return FINAL


def SERVE():
    DISCOVERY_THREAD = threading.Thread(target=SERVICE_DISCOVERY)
    PROVIDER_THREAD = threading.Thread(target=SERVICE_PROVIDER)
    BROADCASTER_THREAD = threading.Thread(target=SERVICE_BROADCASTER)
    DISCOVERY_THREAD.start()
    PROVIDER_THREAD.start()
    BROADCASTER_THREAD.start()


if __name__ == "__main__":
    try:
        SERVE()
    except Exception as e :
        print(e)