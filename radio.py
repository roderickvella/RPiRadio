#!/usr/bin/python
# Example using a character LCD plate.
import time
import Adafruit_CharLCD as LCD
import traceback
import subprocess
import os.path
import os
import urllib,json
 
# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()
# create some custom characters
lcd.create_char(1, [2, 3, 2, 2, 14, 30, 12, 0])
lcd.create_char(2, [0, 1, 3, 22, 28, 8, 0, 0])
lcd.create_char(3, [0, 14, 21, 23, 17, 14, 0, 0])
lcd.create_char(4, [31, 17, 10, 4, 10, 17, 31, 0])
lcd.create_char(5, [8, 12, 10, 9, 10, 12, 8, 0])
lcd.create_char(6, [2, 6, 10, 18, 10, 6, 2, 0])
lcd.create_char(7, [31, 17, 21, 21, 21, 21, 17, 31])
 
#turn on green light
lcd.set_color(0.0, 0.0, 1.0)
lcd.clear()
lcd.message("connecting: \n")
 
message = ""
 
def isConnected():
    global lcd
    while True: #keep repeating until internet connection is found
        try:
            ip = subprocess.check_output("hostname -I",shell=True)
            ip = ip[:3]
            if ip != "192":
                counter = 0
                while True:
                    print 'trying to connect to internet'
                    lcd.clear()
                    lcd.message("connecting to\n internet")
                    time.sleep(1)
                    remote_server = "8.8.8.8"
                    status = subprocess.call(['ping','-c','1',remote_server])#test connection with google
                    if(status == 0):
                        refreshRadioStations()
                        lcd.clear()
                        startPlaying()
                        break
                    else:
                        counter +=1
 
                    if(counter > 3):
                        break
            else:
                break
        except:
            pass
 
def refreshRadioStations():
    lcd.clear()
    lcd.message("getting\n radio stations")
    print("clear radio stations")
    subprocess.call("mpc clear ",shell=True)
    url ="https://raw.githubusercontent.com/roderickvella/RPiRadio/main/radiostations.json"
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    print("add radio stations from server")
    for station in data:
        link = station["link"]
        subprocess.call("mpc add "+link,shell=True)
    
       

def startPlaying():
    global lcd
    lcd.clear()
    subprocess.call("mpc stop ",shell=True)
    subprocess.call("mpc play ",shell=True) #start player
    updateCurrentStation()
    lcd.clear()
 
def updateCurrentStation():
    global message
    time.sleep(0.2)
    message = subprocess.check_output('mpc current',shell=True)
    message = updateStationName(message.strip())
    if(len(message) > 15):
        message = message[:16] + '\n' + message[16:30]
 
def updateStationName(message): #this function updates those station name that are not returning a proper name
    if(message == "http://s3.viastreaming.net:8930/"):
        message = "101"
    elif(message == "http://162.252.85.85:8202/stream/1/"):
        message = "One Radio"
    elif(message == "http://s4.radio.co/s0ac89720b/listen"):
        message = "Bkara FM"
    elif(message == "https://s2.radio.co/s955b1ced9/listen"):
        message = "RTK"
    elif(message == "http://media-ice.musicradio.com/ClassicFMMP3"):
        message = "Classic FM"
    return message
 
def checkStatus():
    status = subprocess.check_output('mpc status',shell=True)
    if(status[0:6] == 'volume'): #empty status starts with text volume
        startPlaying()
 
def Main():
 
    global lcd
    global message
    cache_oldmessage = ""
 
    try:
 
        # Make list of button value, text, and backlight color.
        buttons = ( (LCD.SELECT, 'Select', (1,1,1)),
                    (LCD.LEFT,   'Left'  , (1,0,0)),
                    (LCD.UP,     'Up'    , (0,0,1)),
                    (LCD.DOWN,   'Down'  , (0,1,0)),
                    (LCD.RIGHT,  'Right' , (1,0,1)) )
 
        while True:
            isConnected()
            updateCurrentStation()
 
            # Loop through each button and check if it is pressed.
            for button in buttons:
                if lcd.is_pressed(button[0]):
 
                    if(button[0] == LCD.LEFT):
                        print("left button")                       
 
                        lcd.clear()
                        lcd.message("connecting:\n ")
                        subprocess.call("mpc next ",shell=True)
                        checkStatus()
                        updateCurrentStation()
 
                    elif(button[0] == LCD.RIGHT):
                        print("right button")
 
                        lcd.clear()
                        position = subprocess.check_output('mpc status -f %id%',shell=True)
                        position = int(position.partition('\n')[0])
                        if(position == 1):
                            lcd.message("press left\nno more stations")
                        else:
                            lcd.message("connecting: \n")
                        subprocess.call("mpc prev ",shell=True)
                        checkStatus()
                        updateCurrentStation()
 
                    elif(button[0] == LCD.UP):
                        subprocess.call("mpc volume +5" ,shell=True)
                        print("volume increased")
 
                    elif(button[0] == LCD.DOWN):
                        subprocess.call("mpc volume -5" ,shell=True)
                        print("volume decreased")
 
                    elif(button[0] == LCD.SELECT):
                        lcd.set_color(0.0, 1.0, 1.0)
                        lcd.clear()
                        lcd.message('Goodbye...')
                        time.sleep(2.0)
                        lcd.clear()
                        lcd.set_color(0.0, 0.0, 0.0)
 
                        #subprocess.call(['poweroff -f'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        os.system('shutdown now -h')
 
                    time.sleep(0.75) #button click delay
 
            if(cache_oldmessage != message):
                lcd.clear()
                lcd.message(message)
                cache_oldmessage = message
 
    except Exception as ex:
        traceback.print_exc()
        lcd.set_color(1.0, 0.0, 0.0)
        lcd.clear()
        lcd.message("error")
 
Main()