# **MQTTS PC Monitoring**
**Virtual Internet of Things object based on MQTTS protocol reporting the status of a monitored PC**

### Notice
*The code repository is part of a bachelor's thesis in Telecommunications (ICT) done at the Warsaw University of Technology. The Bachelor of Science (BSc) degree was awarded in February 2022.*

## Description
The thesis presents a system for monitoring the environment of multiple computers, based on the concept of the Internet of Things. The main element of the system is an agent, i.e. an application which reports the state of the monitored PC. It collects the values of examined metrics with a certain time interval, and then sends them to the administrator application using the MQTTS protocol, which is a secure version of the MQTT data transmission protocol. Security is ensured by the use of another protocol (TLS), responsible for the integrity and confidentiality of the transmitted information. An intermediary in the communication between the agent and the administrator's application is the broker, whose logic is based on sharing information between clients by storing it in appropriate topics, allowing only the subscribers to read it. The metrics checked on a given computer include CPU utilization and temperature, RAM utilization, hard disk space utilization, the name of the currently logged in user, or the private and public IP address.

All components of the system, namely the agent, broker and administrator application, were tested. The tests concerned the individual functionalities of each of them, communication between them and security, i.e. the TLS protocol and implemented user authentication when trying to connect to the broker.

The designed system is intended mainly for use in home or office environments, where there are several to a dozen computers. Compared to other solutions available on the market, it is characterized by high performance through the use of lightweight MQTT protocol and a clear and easy-to-use graphical interface of the administrator application.

## OS Compatibility
* Microsoft Windows
* Linux

## Additional components required (not available in repo)
* TLS certificates for both Agent and Admin
* Mosquitto MQTT Broker
* Open Hardware Monitor Software
