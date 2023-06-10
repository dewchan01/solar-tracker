# Code for retrieving online source (https://www.solar-repository.sg/local-weather)
# Location of the measurement taken is from JTC CleanTech One, CleanTech Park (close to NTU)
# please do not remove the unused code, it may be useful in managing errors
# before running this program, please install and import the required packages
# eg: type 'pip install pytesseract' in Python Console to download 'pytesseract' package
# REMINDER: YOU ONLY CAN EXIT THIS PROGRAM BY PRESSING ESCAPE KEY

import pip
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from PIL import Image
import pytesseract
import cv2
import re
import time
from selenium.webdriver.chrome.options import Options
import gspread
import cayenne.client  # Cayenne MQTT Client
import logging

ind = 2 # insert new data in row 'ind' in google sheet
# this program will refresh every 50 secs to ensure data in google sheet will be refreshed around every 1 minute
dur = 50 # min(dur) >= 10

# MQTT credentials
MQTT_USERNAME = "0fa09af0-1e3f-11ed-bf0a-bb4ba43bd3f6"
MQTT_PASSWORD = "317896ff1bbcbb93c1b6454f16e5694a3916bcd4"
MQTT_CLIENT_ID = "2795b910-1e3f-11ed-baf6-35fab7fd0ac8"

# create your own API that connects to your account and spreadsheet in Google Drive

# Internally use only:
# download %APPDATA% file provided in the IoT subgroup file, copy the path of the file and paste it inside
# the file name and remember to change '\' to '/'
# then this program will connects to the google sheet that I posted in the IoT file
sa = gspread.service_account(filename = '../packages/%APPDATA%/gspread/service_account.json')
sh = sa.open("Solar Irradiance Data")
wks = sh.worksheet("Code1")

# download Tesseract-OCR from the same path and do the same thing I mentioned above
pytesseract.pytesseract.tesseract_cmd = r'../packages/tesseract.exe'

# establish the connection with Cayenne dashboard
client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID,port=8883)

#send all the data to cayenne dashboard to display
def send_param(si,msi,at,rh,power):
    client.virtualWrite(13, str(si)) #Publish global irradiance to Cayenne MQTT Broker Channel 13
    client.virtualWrite(14, str(msi)) # Publish max global irradiance to Cayenne MQTT Broker Channel 14
    client.celsiusWrite(15, str(at)) # Publish ambient temperature to Cayenne MQTT Broker Channel 15
    client.celsiusWrite(16, str(rh)) # Publish relative humidity to Cayenne MQTT Broker Channel 16
    client.celsiusWrite(31, str(power))  # Publish optimal power to Cayenne MQTT Broker Channel 31
    #client.virtualWrite(17, str(si)) # Publish global irradiance to Cayenne MQTT Broker Channel 17


# monitor data if any error occurs
    print("Global Irradiance: " + str(si) + " W/m^2\n")
    print("Daily Max Global Irradiance: " + str(msi) + " W/m^2\n")
    print("Ambient Temperature: " + str(at) + " C\n")
    print("Relative Humidity: " +str(rh) + " %\n")
    #print("Temperature of cell: "+ str(tempcell)+"\n")
    #print("Max Power of cell: " + str(Pcell) +' W')

while (1):
    # loop cayenne function
    client.loop()

    # open up a webpage powered by Chrome
    driver = webdriver.Chrome(ChromeDriverManager().install())
    chrome_options = Options()

    # open up the specific webpage
    driver.get('https://www.solar-repository.sg/local-weather')

    # clear the cookies by applying click action on the button
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn btn-primary')]"))).click()


    # (unused code) S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)

    # set the window size and resolution to 1000x1000
    driver.set_window_size(1000, 1000)  # 1000x1000
    chrome_options.add_argument('window-size=1000x1000')  # 1000x1000

    # scroll the webpage to 250px down
    driver.execute_script("window.scrollTo(0, 250)")  # 250

    # for users to take a look on the webpage for 3 seconds
    time.sleep(3)

    # (unused code) driver.execute_script("arguments[0].click()", button)

    # save 5 screenshots of the webpage based on the viewed window size
    driver.save_screenshot('../data/screenshot.png')
    driver.save_screenshot('../data/screenshot0.png')
    driver.save_screenshot('../data/screenshot1.png')
    driver.save_screenshot('../data/screenshot2.png')
    driver.save_screenshot('../data/screenshot3.png')

    #close the webpage
    driver.quit()

    # read the captured image
    img = cv2.imread('../data/screenshot1.png')

    # (unused code) cv2.imshow("original", img)
    # (unused code) print('Original Dimensions : ',img.shape)#
    # (unused code) cv2.imshow("img", img)
    # (unused code) img = cv2.resize(img,(1234,938))

    #based on diff pc, dimensions will be various,eg: 15.6'' screen: (938,1234)
    print('Original Dimensions : ',img.shape)

    # crop the image that shows desired data
    cropped_image = img[350:800, 700:1200] # column of global irradiance and wind speed
    cropped_image1 = img[350:400, 700:1200] # data of global irradiance
    cropped_image2 = img[520:560, 800:1000] # data of maximum global irradiance
    cropped_image3 = img[430:480, 200:450] # data of ambient temperature
    cropped_image4 = img[430:480, 500:700] # data of relative humidity

    # resize the image to ease the process of recognition of the characters in the image
    cropped_image1 = cv2.resize(cropped_image1, (600, 100))
    cropped_image2 = cv2.resize(cropped_image2, (500, 100))
    # (unused code) cropped_image3 = cv2.resize(cropped_image3, (500, 500))
    # (unused code) cropped_image = cv2.resize(cropped_image, (500, 500))

    # (unused code) to show all the cropped images
    # cv2.imshow("cropped", cropped_image)
    # cv2.imshow("cropped1", cropped_image1)
    # cv2.imshow("cropped2", cropped_image2)
    # cv2.imshow("cropped3", cropped_image3)
    # cv2.imshow("cropped4", cropped_image4)

    # overwrite all the previous images that save to your pc with cropped images
    cv2.imwrite("../data/screenshot.png", img)
    cv2.imwrite("../data/screenshot0.png", cropped_image1)
    cv2.imwrite("../data/screenshot1.png", cropped_image2)
    cv2.imwrite("../data/screenshot2.png", cropped_image3)
    cv2.imwrite("../data/screenshot3.png", cropped_image4)

    # detect and recognize the words and numbers inside all the cropped images
    globalIrradiance = pytesseract.image_to_string(
        Image.open('../data/screenshot0.png'))
    maxGlobalIrradiance = pytesseract.image_to_string(
        Image.open('../data/screenshot1.png'))
    ambientTemperature = pytesseract.image_to_string(
        Image.open('../data/screenshot2.png'))
    relativeHumidity = pytesseract.image_to_string(
        Image.open('../data/screenshot3.png'))
    # print(re.findall('(\d+)', globalIrradiance),len(re.findall('(\d+)', globalIrradiance)))

    # retrieve the only numeric number from the words and numbers recognized above and construct them into float number
    if len(re.findall('(\d+)', globalIrradiance))==1:
        globalIrradiance = str(re.findall('(\d+)', globalIrradiance)[0])
    elif len(re.findall('(\d+)', globalIrradiance))>1:
        globalIrradiance = str(re.findall('(\d+)', globalIrradiance)[0])  + '.'+ str(re.findall('(\d+)', globalIrradiance)[1])
    else:
        globalIrradiance = '0' # captured error
    if len(re.findall('(\d+)', maxGlobalIrradiance))==1:
        maxGlobalIrradiance = str(re.findall('(\d+)', maxGlobalIrradiance)[0])
    elif len(re.findall('(\d+)', maxGlobalIrradiance))>1:
        maxGlobalIrradiance = str(re.findall('(\d+)', maxGlobalIrradiance)[0]) + '.'+ str(re.findall('(\d+)', maxGlobalIrradiance)[1])
    else:
        maxGlobalIrradiance = 0
    if len(re.findall('(\d+)', ambientTemperature))==1:
        ambientTemperature = str(re.findall('(\d+)', ambientTemperature)[0])
    elif len(re.findall('(\d+)', ambientTemperature))>1:
        ambientTemperature = str(re.findall('(\d+)', ambientTemperature)[0]) + '.'+ str(re.findall('(\d+)', ambientTemperature)[1])
    else:
        ambientTemperature = 0
    if len(re.findall('(\d+)', relativeHumidity))==1:
        relativeHumidity = str(re.findall('(\d+)', relativeHumidity)[0])
    elif len(re.findall('(\d+)', relativeHumidity))>1:
        relativeHumidity = str(re.findall('(\d+)', relativeHumidity)[0]) + '.'+ str(re.findall('(\d+)', relativeHumidity)[1])
    else:
        relativeHumidity = 0

    # calculate the optimal outcome power based on online ambient temperature using power coefficient

    # ambientTemperature = int(float(ambientTemperature))
    # power = 5
    # StdAt = 25 # Standard Ambient Temperature
    # for i in range(0, (abs(ambientTemperature - StdAt))):
    #     if ambientTemperature - StdAt >= 0:
    #         power = power - 0.675 / 100 * power
    #     else:
    #         power = power + 0.675 / 100 * power

    # impp = 0.3
    # Vmpp = 16.8
    # volcoe = -0.13
    # Vmax = Vmpp + volcoe*(tempcell-25)

    # calculate the optimal outcome power based on online ambient temperature using power coefficient
    Pmax = 5
    TNOCT = 48
    powcoe = -0.675

    tempcell = float(ambientTemperature) + (TNOCT-20)/800*float(globalIrradiance)
    power = Pmax + powcoe/100*(tempcell-25)

    # check errors if they are not able to send it to google sheet and cayenne
    print(globalIrradiance,maxGlobalIrradiance,ambientTemperature,relativeHumidity,power)

    # call the function 'send_irrad' to google sheet and cayenne
    send_param(globalIrradiance,maxGlobalIrradiance,ambientTemperature,relativeHumidity,power)

    # update all the data to the columns with corresponding titles
    wks.update('A' + str(ind), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    wks.update('B' + str(ind), float(globalIrradiance))
    wks.update('C' + str(ind), float(maxGlobalIrradiance))
    wks.update('D' + str(ind), float(ambientTemperature))
    wks.update('E' + str(ind), float(relativeHumidity))
    wks.update('F' + str(ind), float(power))

    # exit the program only if ESC key is clicked
    if cv2.waitKey(20) & 0xFF == 27:
        break

    # whole program will refresh to do new measurement after 'dur' seconds
    time.sleep(dur)

    # record the new data in next column in google sheet
    ind+=1

    # close all the opening windows
    cv2.destroyAllWindows()
    client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID,port=8883)

# close all the windows after exit from the 'while' loop
cv2.destroyAllWindows()


