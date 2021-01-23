import os
import sys
import time
import random
import msvcrt
import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT=6060
SERVING_ADDR=(IP,PORT)
SERVICE=True
HEADER_LENGTH=10
FORMAT='utf-8'
KEYS=''
CONFIG=str(random.randint(1,256))
CONFIG='0'*(3-len(CONFIG))+CONFIG
DISCONNECT='!DISCONNECT!'
SEND_QUEUE=[]
RECIVE_QUEUE=[]
VIEW=[]
SENDVIEW=''
POS=0
KVPOS=0
KEYUPDATE=False
MAX_CON_RETRY=5
TTL=100


def logger(TYPE :int ,MESSAGE) -> None:
    if TYPE == 0 :
        print(MESSAGE)


def SERVICE_DISCOVER():
    global SERVICE,FORMAT,PORT
    NDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    NDP.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
    NDP.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    NDP.settimeout(5)
    NDP.bind(('',PORT+1))
    IP=None
    try:
        logger(0,'[REQUEST] Searching for running Servers')
        while not IP :
            NDP.sendto(bytes('NDP:HI','utf-8'),('<broadcast>',PORT))
            IP=NDP.recv(1024).decode('utf-8')
    except socket.timeout:
        logger(0,'[ERROR] No Services found running')
        sys.exit(0)
    logger(0,f'[SERVICE] Server discovered at {IP}')
    return IP


def CONNECT():
    global CONFIG,SERVICE
    SERVER_IP = SERVICE_DISCOVER()
    ADDR =(SERVER_IP,PORT)
    CLIENT = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        CLIENT.connect(ADDR)
    except Exception as e :
        print(e)
    BANNER=RECIVE_TEXTMSG(CLIENT)
    if BANNER :
        print(BANNER)
        USERNAME=input('\nEnter a User Name : ')
        CONFIG+=USERNAME
        SEND_TEXTMSG(CLIENT,CONFIG)
    else:
        SERVICE = False
    try:
        SENDER_THREAD=threading.Thread(target=SENDER,args=(CLIENT,))
        RECIVER_THREAD=threading.Thread(target=RECIVER,args=(CLIENT,))
        KEYREADER_THREAD=threading.Thread(target=KEYREADER)
        PRINTER_THREAD=threading.Thread(target=PRINTER)
        SENDER_THREAD.start()
        RECIVER_THREAD.start()
        KEYREADER_THREAD.start()
        PRINTER_THREAD.start()
    except Exception as e:
        print(e)
    finally:
        pass


def SENDER(CLIENT : socket.socket):
    global SERVICE,DISCONNECT
    while SERVICE :
        if SEND_QUEUE :
            MESSAGE = SEND_QUEUE.pop(0)
            if MESSAGE == DISCONNECT :
                SEND_TEXTMSG(CLIENT,MESSAGE)
                SERVICE = False
            elif MESSAGE == '!SHUTDOWN!' :
                SEND_TEXTMSG(CLIENT,MESSAGE)
                SERVICE = False
            elif MESSAGE == 'exit' :
                SEND_TEXTMSG(CLIENT,DISCONNECT)
                SERVICE = False
            else:
                SEND_TEXTMSG(CLIENT,MESSAGE)
        else:
            pass


def RECIVER(CLIENT : socket.socket):
    global SERVICE,RECIVE_QUEUE
    CLOCK_START=time.perf_counter()
    while SERVICE :
        CONFIG = RECIVE_TEXTMSG(CLIENT)
        if CONFIG :
            CLOCK_START=time.perf_counter()
            if CONFIG == 'rUaLiVe?' :
                SEND_TEXTMSG(CLIENT,'True')
            else:
                MESSAGE = RECIVE_TEXTMSG(CLIENT)
                RECIVE_QUEUE.append(CONFIG)
                RECIVE_QUEUE.append(MESSAGE)
        else:
            CLOCK_END = time.perf_counter() - CLOCK_START
            if CLOCK_END>TTL :
                CHECK =CHECK_CONNECTION(CLIENT)
                if CHECK :
                    CLOCK_START = time.perf_counter()
                else:
                    SERVICE=False
            else :
                pass


def KEYREADER():
    global KEYS,SERVICE,SEND_QUEUE,KEYUPDATE,POS
    while SERVICE :
        if msvcrt.kbhit() :
            K=msvcrt.getch()
            if K != b'\r':
                if K == b'\x08' :
                    if POS > 0 :
                        KEYS = KEYS[:POS-1]+KEYS[POS:]
                        POS = POS - 1
                        KEYUPDATE=True
                elif K == b'\x1b' :
                    pass
                elif K in [b'\xe0',b'\x00']:
                    K = msvcrt.getch()
                    if K in [b'H',b'P',b'S']:
                        pass
                    elif K == b'K' :
                        if POS > 0 :
                            POS = POS - 1
                        else :
                            pass
                    elif K == b'M' :
                        if POS < len(KEYS) :
                            POS = POS + 1
                        else:
                            pass
                    else:
                        pass
                else:
                    KEYS=KEYS[:POS]+K.decode()+KEYS[POS:]
                    POS=POS+1
            else :
                SEND_QUEUE.append(KEYS)
                KEYS=''
                POS=0
            KEYUPDATE=True


def PRINTER():
    global KEYS,RECIVE_QUEUE,KEYUPDATE,VIEW,POS,KVPOS
    os.system('cls')
    os.system('mode con cols=120 lines=30')
    sys.stdout.write(u'\033[30B')
    sys.stdout.flush()
    sys.stdout.write(f'SEND > {KEYS}'+u'\033[118D')
    sys.stdout.flush()
    while SERVICE :
        if RECIVE_QUEUE:
            CONF=RECIVE_QUEUE.pop(0)
            MESSAGE = RECIVE_QUEUE.pop(0)
            if len(VIEW)>57:
                _=VIEW.pop(0)
                _=VIEW.pop(0)
                if len(MESSAGE)>(119-len(CONF)):
                    SPLITLEN=119-len(CONF)
                    SPLITS=[MESSAGE[i:i+SPLITLEN] for i in range(0,len(MESSAGE),SPLITLEN)]
                    ONE=True
                    for SPLIT in SPLITS:
                        if ONE :
                            VIEW.append(CONF)
                            ONE = False
                        else:
                            VIEW.append(' '*(len(CONF)-1))
                        VIEW.append(SPLIT)
                else :
                    VIEW.append(CONF)
                    VIEW.append(MESSAGE)
            else:
                if len(MESSAGE)>(110-len(CONF)):
                    SPLITLEN=110-len(CONF)
                    SPLITS=[MESSAGE[i:i+SPLITLEN] for i in range(0,len(MESSAGE),SPLITLEN)]
                    ONE=True
                    for SPLIT in SPLITS:
                        if ONE :
                            VIEW.append(CONF)
                            ONE = False
                        else:
                            VIEW.append(' '*(len(CONF)-1))
                        VIEW.append(SPLIT)
                else :
                    VIEW.append(CONF)
                    VIEW.append(MESSAGE)
            for ind in range(len(VIEW)-1,0,-2):
                sys.stdout.write(u'\033[1A')
                sys.stdout.write(u'\033[118D')
                sys.stdout.write(' '*118)
                sys.stdout.write(u'\033[118D')
                CON=VIEW[ind-1]
                USERNAME=CON[3:]
                COL=CON[:3]
                MSG=VIEW[ind]
                if USERNAME[0] != ' ':
                    sys.stdout.write(u'\033[38;5;'+COL+u'm'+f'[{USERNAME}]'+u'\033[0m'+f' : {MSG}')
                else:
                    sys.stdout.write(f'{CON}'+f'   {MSG}')
            sys.stdout.write(u'\033['+str(len(VIEW)//2)+'B')
            sys.stdout.write(u'\033[118D')
            sys.stdout.write(' '*118)
            sys.stdout.write(u'\033[118D')
            if POS<110:
                sys.stdout.write(f'SEND > {KEYS[:110]}')
                sys.stdout.write(u'\033[118D')
                sys.stdout.write(u'\033['+str(7+POS)+'C')
            else:
                KVPOS=POS-110
                sys.stdout.write(f'SEND > {KEYS[KVPOS:POS]}')
                sys.stdout.write(u'\033[118D')
                sys.stdout.write(u'\033['+str(7+POS-KVPOS)+'C')
            sys.stdout.flush()
        elif KEYUPDATE:
            sys.stdout.write(u'\033[118D')
            sys.stdout.write(' '*118)
            sys.stdout.write(u'\033[118D')
            if POS<110:
                sys.stdout.write(f'SEND > {KEYS[:110]}')
                sys.stdout.write(u'\033[118D')
                sys.stdout.write(u'\033['+str(7+POS)+'C')
            else:
                KVPOS=POS-110
                sys.stdout.write(f'SEND > {KEYS[KVPOS:POS]}')
                sys.stdout.write(u'\033[118D')
                sys.stdout.write(u'\033['+str(7+POS-KVPOS)+'C')
            sys.stdout.flush()
            KEYUPDATE=False


def CHECK_CONNECTION(CLIENT : socket.socket):
    SEND_TEXTMSG(CLIENT,'rUaLiVe?')
    OUT=bool(RECIVE_TEXTMSG(CLIENT))
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
            CLIENT.settimeout(5)
            if not SERVICE :
                MESSAGE_CONFIRM = True
            if CONN_RETRY>MAX_CON_RETRY:
                MESSAGE_CONFIRM = True
    CLIENT.settimeout(None)
    return FINAL


if __name__ == "__main__":
    CONNECT()