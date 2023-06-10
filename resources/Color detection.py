import cv2
import numpy as np
import pandas as pd
import urllib.request
import time
from bs4 import BeautifulSoup
import re

clicked = False
r = g = b = xpos = ypos = 0
index=["color","color_name","hex","R","G","B"]
csv = pd.read_csv('colors.csv', names=index, header=None)
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


# function to get x,y coordinates of mouse double click
def draw_function(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        global b, g, r, xpos, ypos, clicked
        clicked = True
        xpos = x
        ypos = y
        b, g, r = img[y, x]
        b = int(b)
        g = int(g)
        r = int(r)

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
cv2.setMouseCallback('Solar Irradiation Map',draw_function)

while (1):

    cv2.imshow('Solar Irradiation Map', img)

    if (clicked):

        # cv2.rectangle(image, startpoint, endpoint, color, thickness)-1 fills entire rectangle
        cv2.rectangle(img, (20, 20), (750, 60), (b, g, r), -1)

        # Creating text string to display( Color name and RGB values )
        text = getColorName(r, g, b) + ' R=' + str(r) + ' G=' + str(g) + ' B=' + str(b)

        # cv2.putText(img,text,start,font(0-7),fontScale,color,thickness,lineType )
        cv2.putText(img, text, (50, 50), 2, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        # For very light colours we will display text in black colour
        if (r + g + b >= 600):
            cv2.putText(img, text, (50, 50), 2, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

        clicked = False

    if cv2.waitKey(20) & 0xFF == 27:
        break
    # time.sleep(5)
cv2.destroyAllWindows()
    # time.sleep(3)



