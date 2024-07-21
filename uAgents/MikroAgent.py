# AP: procedura poprzedzajaca uruchomienie:
# pip install paho-mqtt
# pip install getmac
# pip install psutil
# pip install requests

# testowanie:
# mosquitto_sub -h test.mosquitto.org -t "uAgentMqtts/informations/#" -v

import paho.mqtt.client as mqtt
import time
from datetime import datetime
import pythoncom
from getmac import get_mac_address
import psutil
import wmi
import socket
from requests import get
import json
import threading
import ssl
import getpass

macAddress = get_mac_address().replace(":", "")
threadCancel = 0

maxCpuUsageGlobal = 0
maxCpuTempGlobal = 0
maxRamUsageGlobal = 0
maxDiskUsageGlobal = 0
periodGlobal = 0
ipWanGlobal = ""
ipLanGlobal = ""
# logOutGlobal = ""
logInGlobal = ""
ipWanCount = 1


# Obsluga wiadomosci wysylanych i przychodzacych
def on_log(client, userdata, level, buf):
    print("log: " + buf)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK, rc: " + str(rc))
    else:
        print("Bad connection, rc: " + str(rc))
    # publishConnectOnMacAddress(client)


def on_disconnect(client, userdata, rc):
    # publishDisconnectOnMacAddress(client)
    if rc != 0:
        print("Unexpected disconnection, rc: " + str(rc))
    else:
        print("Disconnected, rc: " + str(rc))


def on_message(client, userdata, message):
    msg = str(message.payload)[2:-1]
    print("Received message: " + msg + " on topic: " + message.topic + " with QoS: " + str(message.qos))
    handleMessage(msg, message.topic)


def on_subscribe(client, userdata, mid, granted_ops):
    print("Subscribed to topic, mid = " + str(mid))


def on_publish(client, userdata, mid):
    print("Published message, mid = " + str(mid))


# obsluga przychodzacych wiadomosci
def handleMessage(message, topic):
    msg = json.loads(message)
    if not (msg.get("maxCpuUsage") is None) and (
            topic == "uAgentMqtts/requirements/all/maxCpuUsage" or topic == f"uAgentMqtts/requirements/{macAddress}/maxCpuUsage"):
        global maxCpuUsageGlobal
        maxCpuUsageGlobal = msg["maxCpuUsage"]
    if not (msg.get("maxCpuTemp") is None) and (
            topic == "uAgentMqtts/requirements/all/maxCpuTemp" or topic == f"uAgentMqtts/requirements/{macAddress}/maxCpuTemp"):
        global maxCpuTempGlobal
        maxCpuTempGlobal = msg["maxCpuTemp"]
    if not (msg.get("maxRamUsage") is None) and (
            topic == "uAgentMqtts/requirements/all/maxRamUsage" or topic == f"uAgentMqtts/requirements/{macAddress}/maxRamUsage"):
        global maxRamUsageGlobal
        maxRamUsageGlobal = msg["maxRamUsage"]
    if not (msg.get("maxDiskUsage") is None) and (
            topic == "uAgentMqtts/requirements/all/maxDiskUsage" or topic == f"uAgentMqtts/requirements/{macAddress}/maxDiskUsage"):
        global maxDiskUsageGlobal
        maxDiskUsageGlobal = msg["maxDiskUsage"]
    if not (msg.get("period") is None) and (
            topic == "uAgentMqtts/requirements/all/period" or topic == f"uAgentMqtts/requirements/{macAddress}/period"):
        global periodGlobal
        periodGlobal = msg["period"]


# Subskrybowanie
def subscribeTopics(client):
    client.subscribe(f"uAgentMqtts/requirements/all/#")
    client.subscribe(f"uAgentMqtts/requirements/{macAddress}/#")


def publishStatus(client):
    status = {"timestamp": str(datetime.now()), "status": "alive"}
    client.publish(f"uAgentMqtts/informations/{macAddress}/status", json.dumps(status))
    if threadCancel == 0:
        t = threading.Timer(5, publishStatus, args=[client])
        t.start()


def publishOnCpuUsage(client):
    currentValue = psutil.cpu_percent(interval=0)
    if currentValue > maxCpuUsageGlobal:
        cpuUsage = {"timestamp": str(datetime.now()), "cpuUsage": currentValue}
        client.publish(f"uAgentMqtts/informations/{macAddress}/cpuUsage", json.dumps(cpuUsage))
    if threadCancel == 0:
        t = threading.Timer(periodGlobal, publishOnCpuUsage, args=[client])
        t.start()


def publishOnCpuTemp(client):
    i = 0
    temp = 0
    try:
        pythoncom.CoInitialize()
        w = wmi.WMI(namespace="root\OpenHardwareMonitor")
        temperature_infos = w.Sensor()
        for sensor in temperature_infos:
            if sensor.SensorType == u'Temperature':
                if str(sensor.Name).startswith("CPU Core"):
                    i += 1
                    temp += sensor.Value
        currentValue = round(temp / i, 1)
        if currentValue > maxCpuTempGlobal:
            cpuTemp = {"timestamp": str(datetime.now()), "cpuTemp": currentValue}
            client.publish(f"uAgentMqtts/informations/{macAddress}/cpuTemp", json.dumps(cpuTemp))
        if threadCancel == 0:
            t = threading.Timer(periodGlobal, publishOnCpuTemp, args=[client])
            t.start()
    except:
        print("Cannot publish on CPU temp, OpenHardwareMonitor application is not running")


def publishOnRamUsage(client):
    currentValue = psutil.virtual_memory().percent
    if currentValue > maxRamUsageGlobal:
        ramUsage = {"timestamp": str(datetime.now()), "ramUsage": currentValue}
        client.publish(f"uAgentMqtts/informations/{macAddress}/ramUsage", json.dumps(ramUsage))
    if threadCancel == 0:
        t = threading.Timer(periodGlobal, publishOnRamUsage, args=[client])
        t.start()


def publishOnDiskUsage(client):
    currentValue = psutil.disk_usage("/").percent
    if currentValue > maxDiskUsageGlobal:
        diskUsage = {"timestamp": str(datetime.now()), "diskUsage": currentValue}
        client.publish(f"uAgentMqtts/informations/{macAddress}/diskUsage", json.dumps(diskUsage))
    if threadCancel == 0:
        t = threading.Timer(periodGlobal, publishOnDiskUsage, args=[client])
        t.start()
        # time.sleep(3)
        # publishOnDiskUsage(client)


def publishOnLastLogIn(client):
    currentValue = getpass.getuser()
    global logInGlobal
    if currentValue != logInGlobal:
        lastLogIn = {"timestamp": str(datetime.now()), "lastLogIn": currentValue}
        client.publish(f"uAgentMqtts/informations/{macAddress}/lastLogIn", json.dumps(lastLogIn))
    if threadCancel == 0:
        t = threading.Timer(periodGlobal, publishOnLastLogIn, args=[client])
        t.start()
        # time.sleep(2)
        # publishOnLastLogIn(client)


def publishOnIpLan(client):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesnt even have to be reachable
        s.connect(('10.255.255.255', 1))
        currentValue = s.getsockname()[0]
    except Exception:
        currentValue = '127.0.0.1'
    finally:
        s.close()
    global ipLanGlobal
    if currentValue != ipLanGlobal:
        ipLan = {"timestamp": str(datetime.now()), "ipLan": currentValue}
        client.publish(f"uAgentMqtts/informations/{macAddress}/ipLan", json.dumps(ipLan))
    if threadCancel == 0:
        t = threading.Timer(periodGlobal, publishOnIpLan, args=[client])
        t.start()


def publishOnIpWan(client):
    currentValue = str(get('https://api.ipify.org').text)
    global ipWanGlobal
    # global ipWanCount
    # if currentValue != ipWanGlobal and ipWanCount == 1:
    ipWanGlobal = currentValue
    ipWan = {"timestamp": str(datetime.now()), "ipWan": currentValue}
    client.publish(f"uAgentMqtts/informations/{macAddress}/ipWan", json.dumps(ipWan))
    if threadCancel == 0:
        t = threading.Timer(periodGlobal, publishOnIpWan, args=[client])
        t.start()
    # if ipWanCount == 5:
    #     ipWanCount = 1
    # ipWanCount += 1


# Główna funkcja odpowiadająca za działanie agenta
def start(broker, port, period, nick, passwd):
    global periodGlobal
    periodGlobal = period
    client = mqtt.Client(f"uAgent - {macAddress}")

    client.on_log = on_log
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish

    print("Connecting to broker " + broker + "...")

    # TLS setup
    # client.tls_set(ca_certs="certs/ca.crt", certfile="certs/client.crt", keyfile="certs/client.key", cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    # client.tls_insecure_set(True)

    client.username_pw_set(username=nick, password=passwd)

    client.connect(broker, port=port)
    client.loop_start()
    time.sleep(1)

    subscribeTopics(client)
    time.sleep(1)

    publishStatus(client)
    publishOnCpuUsage(client)
    publishOnCpuTemp(client)
    publishOnRamUsage(client)
    publishOnDiskUsage(client)
    publishOnLastLogIn(client)
    publishOnIpLan(client)
    publishOnIpWan(client)

    x = input("> ")
    if x == 'q':
        global threadCancel
        threadCancel = 1
        time.sleep(period)
        client.loop_stop()
        client.disconnect()


# Wywołanie
start("192.168.0.100", 9999, 5, "pc1", "computer1")  # broker ip, port, period [secs], nick, passwd
