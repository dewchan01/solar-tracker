import cv2
import numpy as np
import pandas as pd
import urllib.request
import time
from bs4 import BeautifulSoup
import re
import gspread

r = g = b = 0
xpos = 120
ypos = 255
ind = 2
index=["color","color_name","hex","R","G","B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# create your own API that connects to your account and spreadsheet in Google Drive
sa = gspread.service_account(filename = 'C:/Users/USER/Downloads/%APPDATA%/gspread/service_account.json')
sh = sa.open("Solar Irradiance Data")
wks = sh.worksheet("Sheet1")
# return the image


# function to calculate minimum distance from all colors and get the most matching color
def getColorName(R, G, B):
    minimum = 10000
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if (d <= minimum):
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname

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

# function to get x,y coordinates of mouse double click
#def draw_function(event, x, y, flags, param):
    # if event == cv2.EVENT_LBUTTONDBLCLK:
    #     global b, g, r, xpos, ypos, clicked
    #     clicked = True
    #     xpos = x
    #     ypos = y


class AppURLopener(urllib.request.FancyURLopener):
    version = "Chrome/6.0"

opener = AppURLopener()
resp = opener.open("https://www.ema.gov.sg/solarmap.aspx")#https://www.ema.gov.sg/cmsmedia/irradiance/plot.png?ref=637995385969446326
soup = BeautifulSoup(resp.fp)
img = soup.find("div", {"id": "divIrradianceGraph"}).find("img").get('src')
print(img)
req = urllib.request.urlopen('https://www.ema.gov.sg'+img)
arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
img = cv2.imdecode(arr, -1)  # 'Load it as it is'
img = cv2.resize(img, (700, 500))

cv2.namedWindow('Solar Irradiation Map')

while (1):
    b, g, r = img[ypos, xpos]
    b = int(b)
    g = int(g)
    r = int(r)
    si = aveSolIrrad(r,g,b)

    # cv2.rectangle(image, startpoint, endpoint, color, thickness)-1 fills entire rectangle
    cv2.rectangle(img, (0, 0), (750, 30), (b, g, r), -1)

    # Creating text string to display( Color name and RGB values )
    text = getColorName(r, g, b) + ' R=' + str(r) + ' G=' + str(g) + ' B=' + str(b)
    text2 ='Captured Solar Irradiance around NTU: ' + str(si) + 'W/m^2'
    # cv2.putText(img,text,start,font(0-7),fontScale,color,thickness,lineType )
    cv2.putText(img, text, (50, 25), 2, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, text2, (20, 480), 2, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    # For very light colours we will display text in black colour
    if (r + g + b >= 600):
        cv2.putText(img, text, (50, 50), 2, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow('Solar Irradiation Map', img)
    wks.update('A'+str(ind),time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    wks.update('B'+str(ind),int(si))
    if cv2.waitKey(20) & 0xFF == 27:
        break
    time.sleep(10)
    cv2.destroyAllWindows()
    ind+=1
cv2.destroyAllWindows()

#code will be sent to google drive(collab), then the generated value will be stored in new google spreadsheet every n secs.
# Arduino IDE will request the google spreadsheet data by linking another api key which is provided by google spreadsheet