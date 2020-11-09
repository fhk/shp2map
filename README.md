#Rechannel

A reverse supply chain api and app

GS1 Hackathon

Using EPICS

##API

TODO

##Data

TODO


## Howto

```
~$ curl -X POST http://localhost:5000/v1/select

~$ curl -X POST http://localhost:5000/v1/add --data '{"ProductName": 1234}' --header "Content-Type: application/json

~$ curl -X POST http://localhost:5000/v1/update --data '{"ProductId": "957359b6-b784-45d0-934c-5f6e9e2eaca1", "Hello": 123}' --header "Content-Type: application/json"

```