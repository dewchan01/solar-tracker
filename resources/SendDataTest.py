import cayenne.client
import time
import requests

import base64

import configparser
config = configparser.ConfigParser()

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME = "0fa09af0-1e3f-11ed-bf0a-bb4ba43bd3f6"
MQTT_PASSWORD = "317896ff1bbcbb93c1b6454f16e5694a3916bcd4"
MQTT_CLIENT_ID = "3dc88190-1e9e-11ed-bf0a-bb4ba43bd3f6"


# The callback for when a message is received from Cayenne.
def on_message(message):
    print("message received: " + str(message))
    # If there is an error processing the message return an error string, otherwise return nothing.


client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883)


def get_latest_history(access_token, device_id, sensor_id):
    bearer = 'Bearer ' + access_token
    URL = 'https://platform.mydevices.com/v1.1/telemetry/' + device_id + '/sensors/' + sensor_id + '/summaries?type=latest'
    response = requests.get(URL,
                            headers={'authorization': bearer}, )
    payload = response.json()
    data = payload[0]['v']
    print('Data history = %d' % data)

while True:
    client.loop()
    get_latest_history("eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0dm94b2dSR1BFclk1YWhzb1lQSTBHemJBQzd1SHB1bWF6S0pISlFhak13In0.eyJqdGkiOiI4NmY5MzQwZi00MDRhLTRkOTUtYmEzMS1jMDg5ODE1YWQxMDEiLCJleHAiOjE2NjYyNDUzMzgsIm5iZiI6MCwiaWF0IjoxNjY2MTU4OTM4LCJpc3MiOiJodHRwczovL2FjY291bnRzLm15ZGV2aWNlcy5jb20vYXV0aC9yZWFsbXMvY2F5ZW5uZSIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI4YWVjODYyMi03OGI4LTQwZWYtODE5Mi1jZjE4NzQwNDYzZDgiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJjYXllbm5lLXdlYi1hcHAiLCJhdXRoX3RpbWUiOjE2NjYxNTg5MzcsInNlc3Npb25fc3RhdGUiOiI2ZmJjNzdkMS0wZWU4LTRiNTUtOWNiNS0yZDVlYjU0ODZiNTIiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInVzZXJfaWQiOiI4YWVjODYyMi03OGI4LTQwZWYtODE5Mi1jZjE4NzQwNDYzZDgiLCJuYW1lIjoiTG93IENvc3QgIEUwNDEiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJkY2hhbjAyNEBlLm50dS5lZHUuc2ciLCJnaXZlbl9uYW1lIjoiTG93IENvc3QgIiwiZmFtaWx5X25hbWUiOiJFMDQxIiwiZW1haWwiOiJkY2hhbjAyNEBlLm50dS5lZHUuc2cifQ.ank8dmBFCRcaUN9yfHtoINxbJNQ0PmAKta6PfxYT12_r-rdXGbWsHwlv73k7JnV1dRiRdSDvsYOVIaGh-pqi_HgeTIIbtQ8FQLb0J56vKHRGHPGy-mR9Vg2Ic2y2ZDHaiHCtdPako_RhNI6adDu0VteT16SdCDtQq9yTfZ3m_DWnx497e9OgcylgydduOJjXmk4JzU2xndEvGZksf6fbpVF6cDIrDUf3ZB-_LjVTyo7Wh4oRhkwWKllW743mTXEhNZcuIKwvjblKFz3bUIOv20CUx71AiY2BozODumhWwTLJ_iRfnNFgBJ2wVCyB5tpuEChZ5ov6sisSc0Ry2SL3Ug",
                       "8aec8622-78b8-40ef-8192-cf18740463d8","2795b910-1e3f-11ed-baf6-35fab7fd0ac8")

