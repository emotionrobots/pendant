#!/usr/bin/python3
#========================================================================
#
#  vBeaconTest.py
#
#  Copyright (c) 2020-2021, E-Motion, Inc.
#
#  This SOFTWARE PRODUCT is provided "as-is". PROVIDER  makes no 
#  representations or warranties of any kind concerning the suitability 
#  and safety of the SOFTWARE PRODUCT for any applications.  Makers of 
#  products containing the SOFTWARE are solely responsible for the 
#  suitability and safety the product.  E-Motion will not be liable 
#  for any damages one may suffer in connection with using, modifying, 
#  or distributing this SOFTWARE PRODUCT.
#
#========================================================================
import sys
import time
import qrcode
from threading import Timer

sys.path.append('lib')
from PiSugar2 import PiSugar2
from ePaper import ePaper
from ui import UI, TextBox, ImageBox, Color, TTFont
from vBeacon import vBeacon
from Buzzer import Buzzer


class App(UI):

  welcomeMessage = "Welcome to ViroGuard!"  

  #-----------------------------------------------------------
  #  Constructor
  #-----------------------------------------------------------
  def __init__(self, display, buttonPress, buzzer): 
    super(App, self).__init__(display, buttonPress)

    self.buzzer = buzzer

    self.vbeacon = vBeacon(
      uuid="2f234454-cf6d-4a0f-adf2-f4911ba9ffa6",
      major=2,
      minor=7777,
      txPower=-59,
      expiration=30
    )
    self.vbeacon.startScanning()
    self.vbeacon.startAdvertising()
   
    self.sqTextBox = TextBox() 
    self.sqLogoBox = ImageBox()
    self.sqQrBox = ImageBox() 
    self.menuHome = TextBox()

    self.statusTimeout = 5  # 20 sec
    self.statusTimer = Timer(self.statusTimeout, self.hideStatus) 

 
  #-----------------------------------------------------------
  #  UI builder
  #-----------------------------------------------------------
  def build(self):

    menuW = 70
    menuH = 20
    menuDim = [menuW, menuH]
    marginDim = [2,2]
    sqSide = 100
    sqPos = [2*menuW+5, 0] 
    sqDim = [sqSide,sqSide]
    statusH = 20
    desktopDim = [self.display.width, self.display.height]
 
    #  Blank background  
    blank = self.addRect(pos=[0,0], dim=desktopDim, outline=Color.white, fill=Color.white)
    blank.isSelectable = False

    # Home menu 
    self.menuHome = self.addTextBox(text="Home", font=TTFont(14), 
                  pos=[0,0], dim=menuDim, margin=marginDim,
                  textColor=Color.black, outline=Color.black, fill=Color.white)
    self.menuHome.onFocus = self.showLogo      


    # Show menu
    menuShow = self.addDropList(text="Show", font=TTFont(14),
                pos=[0,menuH], dim=menuDim, margin=marginDim, offset=[menuW,-menuH+menuH/2], 
                textColor=Color.black, outline=Color.black, fill=Color.white)

    optShow0 = menuShow.addEntry(0, "QR code")
    optShow0.onSelect = self.showQrCode

    optShow1 = menuShow.addEntry(1, "Nearby")
    optShow1.onSelect = self.showNearby

    optShow2 = menuShow.addEntry(2, "My Info")
    optShow2.onSelect = self.showMyInfo

    optShow3 = menuShow.addEntry(3, "About")
    optShow3.onSelect = self.showAbout


    # Privacy menu
    menuPrivacy = self.addDropList(text="Privacy", font=TTFont(14),
                  pos=[0,2*menuH], dim=menuDim, margin=marginDim, offset=[menuW,-2*menuH+menuH/2],
                  textColor=Color.black, outline=Color.black, fill=Color.white)

    optPrivacy0 = menuPrivacy.addEntry(0, "ON")
    optPrivacy0.onSelect = self.privacyOn

    optPrivacy1 = menuPrivacy.addEntry(1, "OFF")
    optPrivacy1.onSelect = self.privacyOff


    #-----------------------------------------------
    # Widgets for the square display area 
    #-----------------------------------------------

    # Logo
    self.sqLogoBox = self.addImageBox(pos=sqPos, dim=sqDim,
        imageFile="/etc/PiBeacon/pics/ViroGuardLogoWithText.bmp")
    self.sqLogoBox.isSelectable = False
    self.sqLogoBox.isVisible = True


    # TextBox
    self.sqTextBox = self.addTextBox(text="", font=TTFont(14), 
                            pos=sqPos, dim=sqDim, margin=marginDim,
                            textColor=Color.black, outline=Color.black, fill=Color.white)
    self.sqTextBox.isSelectable = False 
    self.sqTextBox.isVisible = False


    # QR code
    self.sqQrBox = self.addImageBox(pos=sqPos, dim=sqDim)
    self.sqQrBox.isSelectable = False
    self.sqQrBox.isVisible = False 


    #-----------------------------------------------
    # Widgets for the bottom status area
    #-----------------------------------------------

    # Ticker tape
    self.ticker = self.addTickerTape(pos=[0, self.display.height-statusH], dim=[2,statusH], 
                  text= self.welcomeMessage, 
                  font=TTFont(14),
                  textColor=Color.black, outline=Color.white, fill=Color.white)
    self.ticker.isSelectable = False
    self.ticker.isVisible = True 


    # Status Box 
    self.status = self.addTextBox( text="Status",
                  pos=[0, self.display.height-statusH], dim=[self.display.width, statusH],
                  font=TTFont(14),
                  textColor=Color.white, outline=Color.white, fill=Color.black)
    self.status.isSelectable = False
    self.status.isVisible = False 

    self.firstFocusId = self.menuHome.id
  
    return


  #-----------------------------------------------------------
  #  Show user info
  #-----------------------------------------------------------
  def showMyInfo(self):
    self.sqTextBox.text = "Myinfo is"
    self.showInSquare("text")
    self.showStatus("My Info")
    self.render()

  #-----------------------------------------------------------
  #  Make QR image from a string
  #-----------------------------------------------------------
  def showQrCode(self):
    qr = qrcode.QRCode(
      version=1,
      error_correction=qrcode.constants.ERROR_CORRECT_M,
      box_size=3,
      border=0,
    )
    qr.add_data("https://e-motion.consulting")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white") 
    self.sqQrBox.image = img
    self.showInSquare("qr")
    self.showStatus("QR code")
    self.render()


  #-----------------------------------------------------------
  #  Show nearby beacons
  #-----------------------------------------------------------
  def showNearby(self):
    if self.vbeacon is not None:
      nearby = self.vbeacon.getNearbyBeacons()
      self.sqTextBox.text = ""
      for beacon in nearby:
        self.sqTextBox.text += str(beacon['major']) + "-" + str(beacon['minor']) + "\n" 
      self.showInSquare("text")
      self.showStatus("Nearby")
    self.render()


  #-----------------------------------------------------------
  #  Show About 
  #-----------------------------------------------------------
  def showAbout(self):
    self.sqTextBox.text = "ViroGuard\nPendent\nFW: v1.0.0" 
    self.showInSquare("text")
    self.showStatus("About")
    self.render()


  #-----------------------------------------------------------
  #  Show logo 
  #-----------------------------------------------------------
  def showLogo(self):
    self.menuHome.fill = Color.black
    self.menuHome.textColor = Color.white

    self.showInSquare("logo")
    self.render()
 
     
  #-----------------------------------------------------------
  #  Show item in square display 
  #-----------------------------------------------------------
  def showInSquare(self, item):
    self.sqLogoBox.isVisible = False
    self.sqTextBox.isVisible = False
    self.sqQrBox.isVisible = False

    if item == "logo":  
      self.sqLogoBox.isVisible = True
    elif item == "qr":  
      self.sqQrBox.isVisible = True
    elif item == "text":  
      self.sqTextBox.isVisible = True


  #-----------------------------------------------------------
  #  Show status 
  #-----------------------------------------------------------
  def showStatus(self, text):
    self.status.text = text
    self.showInStatusBar("status")


  #-----------------------------------------------------------
  #  Show ticker 
  #-----------------------------------------------------------
  def showTicker(self, text):
    self.ticker.text = text
    self.showInStatusBar("ticker")

   
  #-----------------------------------------------------------
  #  Show item in status bar  
  #-----------------------------------------------------------
  def showInStatusBar(self, item):
    self.statusTimer.cancel()

    self.status.isVisible = False
    self.ticker.isVisible = False

    if item == "ticker":  
      self.ticker.isVisible = True

    elif item == "status":  
      self.status.isVisible = True
      self.statusTimer = Timer(self.statusTimeout, self.hideStatus) 
      self.statusTimer.start()
  
  
  #-----------------------------------------------------------
  #  Hide status bar   
  #-----------------------------------------------------------
  def hideStatus(self):
    self.showInStatusBar("ticker")
    self.render()

 
  #-----------------------------------------------------------
  #  Set beacon on   
  #-----------------------------------------------------------
  def privacyOn(self):
    self.vbeacon.stopAdvertising()
    self.showStatus("Privacy ON")
    self.render()

 
  #-----------------------------------------------------------
  #  Set beacon off  
  #-----------------------------------------------------------
  def privacyOff(self):
    self.vbeacon.startAdvertising()
    self.showStatus("Privacy OFF")
    self.render()


#--------------------------------------------------------------------------
#  Main
#--------------------------------------------------------------------------
def main(args):
  pisugar = PiSugar2()
  paper = ePaper()
  buzzer = Buzzer(pin=16)
 
  app = App(paper, pisugar.get_button_press, buzzer)

  print("Starting app...")
  app.start()

  while True:
    time.sleep(1.0)


if __name__ == '__main__':
  main(sys.argv[1:])
   

