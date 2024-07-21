var devices = 0
var macAddressesList = []
var statusList = []
var timer = 0
var tableSize = 5

var connected_flag = 0
var mqtt;
var reconnectTimeout = 5;
// var host = "192.168.0.100"; //moved to HTML file (webAdmin.html)
// var port = 9999; //moved to HTML file (webAdmin.html)
var globHost = "";
var globPort = 0;
var sub_topic = "uAgentMqtts/informations/#";

// TLS setup
// var fs = require('fs');
// var KEY = fs.readFileSync(__dirname + '/client.key');
// var CERT = fs.readFileSync(__dirname + '/client.crt');
// var TRUSTED_CA_LIST = fs.readFileSync(__dirname + '/ca.crt');

function onConnectionLost() {
    devices = 0;
    console.log("connection lost");
    document.getElementById("status").innerHTML = devices;
    connected_flag = 0;
}

function onFailure(message) {
    console.log("Attempting to reconnect to host " + host);
    setTimeout(MQTTconnect, reconnectTimeout);
}

function onConnect() {
    console.log("Connected to " + globHost + " on port " + globPort)
    connected_flag = 1
    console.log("on Connect " + connected_flag);
    mqtt.subscribe(sub_topic);
}

function onMessageArrived(r_message) {
    let msg = JSON.parse(r_message.payloadString)
    out_msg = "Message received: " + r_message.payloadString;
    out_msg = out_msg + " on Topic: " + r_message.destinationName;
    console.log(out_msg);
    var topic = r_message.destinationName;

    //if (topic == "uAgentMqtts/informations/macAddresses") {
    checkMacAddress(r_message.destinationName)
    //}

    //if (!topic.startsWith("uAgentMqtts/informations/macAddresses")) {
    let mac = topic.substring(topic.indexOf("informations/") + 13, topic.lastIndexOf("/"))
    let metric = topic.substring(topic.indexOf(mac + "/") + 13)
    document.getElementById("mac" + checkMacIndex(mac)).innerHTML = mac;
    switch (metric) {
        case "cpuUsage":
            document.getElementById("cpuu" + checkMacIndex(mac)).innerHTML = msg.cpuUsage;
            break
        case "cpuTemp":
            document.getElementById("cput" + checkMacIndex(mac)).innerHTML = msg.cpuTemp;
            break
        case "ramUsage":
            document.getElementById("ramu" + checkMacIndex(mac)).innerHTML = msg.ramUsage;
            break
        case "diskUsage":
            document.getElementById("disku" + checkMacIndex(mac)).innerHTML = msg.diskUsage;
            break
        case "lastLogIn":
            document.getElementById("user" + checkMacIndex(mac)).innerHTML = msg.lastLogIn;
            break
        case "ipLan":
            document.getElementById("iplan" + checkMacIndex(mac)).innerHTML = msg.ipLan;
            break
        case "ipWan":
            document.getElementById("ipwan" + checkMacIndex(mac)).innerHTML = msg.ipWan;
            break
        case "status":
            statusList[checkMacIndex(mac)] = 1
            break
        default:
            console.log("no such metric")
    }
    //}
}

function checkMacAddress(message) {
    var mac = message.slice(25, 37)
    for (i in macAddressesList) {
        if (macAddressesList[i] == mac)
            return
    }
    macAddressesList.push(mac)
    statusList.push(1)
    devices += 1
    if (devices == 1)
        addToDropDownMenu("all")
    addToDropDownMenu(mac)
    document.getElementById("status").innerHTML = devices
    //let msg = JSON.parse(message)
    //let mac = msg.macAddress
    //let connection = msg.connection
    // if (connection == 1) {
    //     for (i in macAddressesList) {
    //         if (macAddressesList[i] == mac)
    //             return;
    //     }
    //     macAddressesList.push(mac)
    //     devices = devices + 1
    //     if (devices == 1)
    //         addToDropDownMenu("all")
    //     addToDropDownMenu(mac)
    //     document.getElementById("status").innerHTML = devices
    // }
    // else if (connection == 0) {
    //     for (i in macAddressesList) {
    //         if (i == mac)
    //             macAddressesList.splice(i, 1)
    //         else
    //             print("Mac address ERROR")
    //     }
    // }
}

function checkMacIndex(mac) {
    for (i in macAddressesList) {
        if (macAddressesList[i] == mac)
            return i
    }
}

function checkAlive() {
    if (statusList.length != 0) {
        for (i in statusList) {
            if (statusList[i] == 0) {
                console.log("Connection with " + macAddressesList[i] + " has dropeed")

                let j = i
                while (j < statusList.length) {
                    document.getElementById("mac" + j).innerHTML = "-";
                    document.getElementById("cpuu" + j).innerHTML = "-";
                    document.getElementById("cput" + j).innerHTML = "-";
                    document.getElementById("ramu" + j).innerHTML = "-";
                    document.getElementById("disku" + j).innerHTML = "-";
                    document.getElementById("user" + j).innerHTML = "-";
                    document.getElementById("iplan" + j).innerHTML = "-";
                    document.getElementById("ipwan" + j).innerHTML = "-";
                    j++
                }
                
                devices -= 1
                document.getElementById("status").innerHTML = devices
                deleteFromDropDownMenu(macAddressesList[i])
                if (devices == 0)
                    deleteFromDropDownMenu("all")
                statusList.splice(i, 1)
                macAddressesList.splice(i, 1)
                return
            }
        }
    }
}

//Time
function startTime() {
    //console.log(timer)
    const today = new Date();
    let h = today.getHours();
    let m = today.getMinutes();
    let s = today.getSeconds();
    h = addZero(h);
    m = addZero(m);
    s = addZero(s);
    document.getElementById('time').innerHTML = h + ":" + m + ":" + s;
    setTimeout(startTime, 1000);
    if (timer == 0) {
        for (i in statusList)
            statusList[i] = 0
    }
    if (timer == 10) {
        checkAlive()
        timer = -1
    }
    timer += 1
}

function addZero(i) {
    if (i < 10) {
        i = "0" + i
    };
    return i;
}

function currentTime() {
    var today = new Date();
    var date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
    var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
    var dateTime = date + ' ' + time;
    return dateTime
}

//Logs
window.console = {
    log: function (str) {
        var node = document.createElement("div");
        node.prepend(document.createTextNode(str));
        document.getElementById("logs").prepend(node);
    }
}

//Message send
function dropDownMenu() {
    var select = document.getElementById("selectPC");
}

function addToDropDownMenu(addr) {
    var select = document.getElementById("pc");
    var el = document.createElement("option");
    el.textContent = addr;
    el.value = addr;
    select.appendChild(el);
}

function deleteFromDropDownMenu(addr) {
    var select = document.getElementById("pc");
    for (i = 0; i < select.length; i++) {
        if (addr != "all") {
            if (select.options[i+2].value == addr) {
                select.remove(i+2)
                return
            }
        }
        else {
            select.remove(i+1)
            return           
        }
    }
}

function sendMessage() {
    var val = document.getElementById("amount").value;
    var pc = document.getElementById("pc").value;
    var met = document.getElementById("metric").value;
    if (pc == "Choose PC") {
        console.log("Choose PC from the list")
        return false
    }
    if (met == "Choose metric") {
        console.log("Choose metric from the list")
        return false
    }
    if (connected_flag == 0) {
        out_msg = "Not connected, so cannot be send"
        console.log(out_msg);
        return false;
    }

    var mess = "{" + '"timestamp": ' + '"' + String(currentTime()) + '"' + ", " + '"' + String(met) + '": ' + String(val) + "}"
    message = new Paho.MQTT.Message(mess);
    message.destinationName = "uAgentMqtts/requirements/" + String(pc) + "/" + String(met);
    mqtt.send(message);
    console.log("Message sent: " + String(mess) + " on Topic " + String(message.destinationName))
    return false;
}

function MQTTconnect(host, port, nick, passwd) {
    globHost = host
    globPort = port
    startTime()
    dropDownMenu()
    console.log("connecting to " + host + " " + port);
    var cname = "Admin - " + host;
    mqtt = new Paho.MQTT.Client(host, port, cname);

    // TLS setup
    // var fs = require('fs');
    // var KEY = fs.readFileSync('certs/client.key');
    // var CERT = fs.readFileSync('certs/client.crt');
    // var CAfile = [fs.readFileSync('certs/ca.crt')];

    var options = {
        timeout: 5,
        onSuccess: onConnect,
        onFailure: onFailure,
        userName: nick,
        password: passwd,
        // TLS setup
        // ca: CAfile,
        // certPath: CERT,
        // keyPath: KEY
    };

    mqtt.onConnectionLost = onConnectionLost;
    mqtt.onMessageArrived = onMessageArrived;

    mqtt.connect(options);

    return false;
}