#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import os

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined. 
      To access global parameters use conf['global']['parameterName']. For end-user parameters use conf['secret']['parameterName'] 
     
    Refer to the documentation for further details. 
    """ 
    import requests
    import json
    import os
    
    current_session_id = intentMessage.session_id
    userid = os.path.basename(__file__).split('-')[1]
    intent = intentMessage.intent.intent_name
    text = intentMessage.input
    slots = list(intentMessage.slots.items())
    request_json = { 'body': {'userid': userid, 'intent': intent, 'slots': slots, 'text': text}}
    #print(request_json)   
 
    headers = {'Content-Type': 'application/json',
      'x-api-key': 'OiepfKJ1Xq9lsX6TEsCGsqCGNWqeELW6kYNAOmc7', 'Accept': '*/*'}
    
    response = requests.post('https://qt982azrm0.execute-api.us-west-2.amazonaws.com/prod/testIntent',
      headers=headers,
      data=json.dumps(request_json))
    body = response.json()
    print(response, response.content)
    print(body.get('displayText', 'Something went wrong')) 

    body = response.json()
    hermes.publish_end_session(current_session_id, body.get('displayText', 'Something went wrong'))

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("TSchmidty:LaunchMagicDoor", subscribe_intent_callback) \
         .start()
