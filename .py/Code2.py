# Code for retrieving online source (https://www.ema.gov.sg/solarmap.aspx)
# Location of the measurement taken may not accurate since the point is random picked which is close to NTU
# do not run this program too frequent since it may cause data traffic congestion for the source server to response the call
# please do not remove the unused code, it may be useful in managing errors
# before running this program, please install and import the required packages
# eg: type 'pip install cayenne' in Python Console to download 'cayenne' package
# REMINDER: YOU ONLY CAN EXIT THIS PROGRAM BY PRESSING ESCAPE KEY

import cv2
import numpy as np
import pandas as pd
import urllib.request
import time
from bs4 import BeautifulSoup
import re
import gspread
import cayenne.client  # Cayenne MQTT Client

MQTT_USERNAME = "0fa09af0-1e3f-11ed-bf0a-bb4ba43bd3f6"
MQTT_PASSWORD = "317896ff1bbcbb93c1b6454f16e5694a3916bcd4"
MQTT_CLIENT_ID = "3dc88190-1e9e-11ed-bf0a-bb4ba43bd3f6"

# establish the connection with Cayenne dashboard
client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)

r = g = b = 0 #initiate all the rgb value to 0
xpos = 120 #initiate horizontal position of measurement on this map
ypos = 255 #initiate vertical position of measurement on this map
ind = 2 #insert new data in row 'ind' in google sheet
dur = 60 #refreshing time
maxSi = 0 #maximum daily solar irradiance

#retrieve the captured colour rgb data values and match with colour in xlsx file 'colors' in IoT subgroup folder
index=["color","color_name","hex","R","G","B"]

# create your own API that connects to your account and spreadsheet in Google Drive

# Internally use only:
# download %APPDATA% file provided in the IoT subgroup file, copy the path of the file and paste it inside
# the file name and remember to change '\' to '/'
# then this program will connects to the google sheet that I posted in the IoT file
csv = pd.read_csv('colors.csv', names=index, header=None)
sa = gspread.service_account(filename = 'packages/%APPDATA%/gspread/service_account.json')
sh = sa.open("Solar Irradiance Data")
wks = sh.worksheet("Code2")

# function to calculate minimum distance from all colors and get the most matching color
def getColorName(R, G, B):
    minimum = 10000
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if (d <= minimum):
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname

# measure specific point of irradiance based on the colour shown at the right colour range bar using this algo
def aveSolIrrad(r,g,b):
    sums = 0
    if r < 1 and b < 1 and 0 < g <= 238:# 0-700: G: 0-238 & B: 0
        sums = 700/238 * g
    if r < 1 and 1 <= b < 125 and 238 < g < 255:# 700-850: G: 238-255 & B: 1-125
        sums = 2.9378 * g + 0.8069 * b
    if 1 < r < 60 and 64 < b < 125 and g == 255:# 850-950: R: 0-60 & G: 255 & B: 64-125
        sums = 8.6538 * r + 6.7308 * b
    if 60 <= r < 105 and 20 < b <= 64 and g == 255: # 950-1000: R: 60-105 & G: 255-245 & B: 64-20
        sums = 8.1522 * r + 7.2011 * b
    if 105 <= r < 122 and 0 <= b < 20 and 245 < g < 255:# 1000-1050: R: 105-122 & G: 245-255 & B: 20-0
        sums = 60.1316 * r + 53.6184 * b - 25.0439 * g
    if 122 <= r < 132 and 0 <= b < 60 and 245 < g < 255:# 1050-1100: R: 122-132 & G: 255-245 & B: 0-60
        sums = 3.2499 * r + 0.9993 * b + 2.4941 * g
    if 132 <= r < 144 and 60 <= b < 144 and 240 <= g < 245: # 1100-1200: R: 132-144 & G: 245-240 & B: 60-144
        sums = -3.3981 * r + 2.0227 * b + 5.8252 * g
    return int(sums)

def send_irrad(si):
    client.virtualWrite(13, str(si))  # Publish global irradiance to Cayenne MQTT Broker Channel 13
    client.virtualWrite(14, str(maxSi))  # Publish max global solar irradiance to Cayenne MQTT Broker Channel 14
    print(str(si) + " W/m^2\n")

# (unused code) function to get x,y coordinates of mouse double click
# def draw_function(event, x, y, flags, param):
    # if event == cv2.EVENT_LBUTTONDBLCLK:
    #     global b, g, r, xpos, ypos, clicked
    #     clicked = True
    #     xpos = x
    #     ypos = y


while (1):
    #loop cayenne function
    client.loop()


    # open the website with opener
    class AppURLopener(urllib.request.FancyURLopener):
        version = "Chrome/6.0"


    opener = AppURLopener()

    # response of website
    resp = opener.open("https://www.ema.gov.sg/solarmap.aspx")

    # transform webpage to html scripts
    soup = BeautifulSoup(resp.fp)

    # find code of the src image from the scripts
    img = soup.find("div", {"id": "divIrradianceGraph"}).find("img").get('src')

    print(img)  # src of image

    # since webpage is dynamic, the src of image will have to be kept updating
    req = urllib.request.urlopen('https://www.ema.gov.sg' + img)

    # read the src of image in unicode form
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)

    # 'Load it as it is, remain unchanged IMREAD_COLOR'
    img = cv2.imdecode(arr, -1)

    # resize the image to 700 x 500
    img = cv2.resize(img, (700, 500))

    # open up a window for image
    cv2.namedWindow('Solar Irradiation Map')

    #fix the position of the observed point on the map which is close to NTU
    b, g, r = img[ypos, xpos]
    b = int(b)
    g = int(g)
    r = int(r)
    #run the function to store the measured irradiance based on (color r, g, b on map) in variable si
    si = aveSolIrrad(r,g,b)

    #compare the solar irradiance with daily maximum solar irradiance
    if si>maxSi:
        maxSi = si

    # cv2.rectangle(image, startpoint, endpoint, color, thickness)-1 fills entire rectangle
    cv2.rectangle(img, (0, 0), (750, 30), (b, g, r), -1)

    # Creating text string to display( Color name and RGB values and measured irradiance)
    text = getColorName(r, g, b) + ' R=' + str(r) + ' G=' + str(g) + ' B=' + str(b)
    text2 ='Captured Solar Irradiance around NTU: ' + str(si) + 'W/m^2'
    # cv2.putText(img,text,start,font(0-7),fontScale,color,thickness,lineType )
    cv2.putText(img, text, (50, 25), 2, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, text2, (20, 480), 2, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    # For very light colours we will display text in black colour
    if (r + g + b >= 600):
        cv2.putText(img, text, (50, 50), 2, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

    #show map
    cv2.imshow('Solar Irradiation Map', img)

    #call the function send_irrad to send the irradiance to cayenne
    send_irrad(si,maxSi)

    #update the date and irradiance to google sheet
    wks.update('A'+str(ind),time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    wks.update('B'+str(ind),int(si))
    wks.update('C'+str(ind), int(maxSi))

    #exit the program only if ESC key is clicked
    if cv2.waitKey(20) & 0xFF == 27:
        break

    #refresh the measurement every 'dur' seconds
    time.sleep(dur)

    # close all the opening windows
    cv2.destroyAllWindows()

    #record the new data in next column in google sheet
    ind+=1

# close all the windows after exit from the 'while' loop
cv2.destroyAllWindows()

# (unused code) button = Button(2)  # Declaring button pin 2

# (unused code) button.when_pressed = send_on  # When button pressed run send_on function
# (unused code) button.when_released = send_off  # When button released run send_off function

