#!/usr/bin/python3
#========================================================================
#
#  vBeacon.py
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
import getopt
import time
import datetime
import threading 
from threading import Lock, Thread 

sys.path.append('lib')
from iBeaconAdvertiser import iBeaconAdvertiser
from iBeaconScanner import iBeaconScanner
from OverflowAreaBeaconScanner import OverflowAreaBeaconScanner


class vBeacon:

  #========================================================================
  #
  #  Constructor
  #
  #========================================================================
  def __init__(self, uuid, major, minor, txPower, 
                                  callback=None, expiration=10):
    self.isScanning = False
    self.isAdvertising = False

    self.uuid = uuid
    self.major = major
    self.minor = minor
    self.txPower = txPower
    self.callback = callback
    self.expiration = expiration
 
    self.iBeaconScanner = iBeaconScanner(self.uuid, self._iBeaconCallback) 
    self.overflowAreaBeaconScanner = OverflowAreaBeaconScanner(self._overflowAreaBeaconCallback) 
    self.iBeaconAdvertiser = iBeaconAdvertiser(self.uuid, self.major, self.minor, self.txPower)

    self.nearbyBeacons = {}
    self.lock = Lock() 


  #========================================================================
  #
  #  Start Scanning 
  #
  #========================================================================
  def startScanning(self):
    if self.isScanning != True:
      self.scanningThread = Thread(target=self._startScanning)
      self.scanningThread.start()
      self.isScanning = True


  #========================================================================
  #
  #  Start Advertising 
  #
  #========================================================================
  def startAdvertising(self):
    if self.isAdvertising != True:
      self.advertisingThread = Thread(target=self._startAdvertising)
      self.advertisingThread.start()
      self.isAdvertising = True

  #========================================================================
  #
  #  Stop Scanning 
  #
  #========================================================================
  def stopScanning(self):
    if self.isScanning:
      self.iBeaconScanner.stop()
      self.overflowAreaBeaconScanner.stop()
      self.scanningThread.join()  
      self.isScanning = False


  #========================================================================
  #
  #  Stop advertising 
  #
  #========================================================================
  def stopAdvertising(self):
    if self.isAdvertising:
      self.iBeaconAdvertiser.stop()
      self.advertisingThread.join()  
      self.isAdvertising = False
    
  #========================================================================
  #
  #  Return a list of nearby beacons
  #
  #========================================================================
  def getNearbyBeacons(self): 
    beacons = [] 

    self.lock.acquire()

    for beacon in self.nearbyBeacons.values():
      beacons.append(beacon)

    self.lock.release()

    return beacons 
  

  #========================================================================
  #
  #  Start VBeacon advertisement
  #
  #========================================================================
  def _startAdvertising(self):
    self.iBeaconAdvertiser.start()


  #========================================================================
  #
  #  Start both beacon type scanning
  #
  #========================================================================
  def _startScanning(self):
    self.iBeaconScanner.start() 
    self.overflowAreaBeaconScanner.start() 

  #========================================================================
  #
  #  Update nearby beacons
  #
  #========================================================================
  def _updateNearbyBeacons(self, major, minor, txPower, rssi):

    id = str(major)+"-"+str(minor)

    self.lock.acquire()
    self.nearbyBeacons[id] = { 
      "date":    datetime.datetime.utcnow(),
      "major":   major,
      "minor":   minor,
      "txPower": txPower,
      "rssi":    rssi
    }

    removeId = []
    for id in self.nearbyBeacons.keys(): 
      beacon = self.nearbyBeacons[id]
      diff = datetime.datetime.utcnow() - beacon["date"]
      if diff.seconds > self.expiration:
        removeId.append(id)
    
    for id in removeId:
      #print(f"Deleting ${self.nearbyBeacons[id]}")
      del(self.nearbyBeacons[id])

    self.lock.release()

 
  #========================================================================
  #
  #  iBeacon callback
  #
  #========================================================================
  def _iBeaconCallback(self, major, minor, txPower, rssi):
    self._updateNearbyBeacons(major, minor, txPower, rssi)
    if self.callback != None:
      self.callback(major, minor, txPower, rssi) 
    
  #========================================================================
  #
  #  OverflowAreaBeacon callback
  #
  #========================================================================
  def _overflowAreaBeaconCallback(self, major, minor, txPower, rssi):
    self._updateNearbyBeacons(major, minor, txPower, rssi)
    if self.callback != None:
      self.callback(major, minor, txPower, rssi) 



#========================================================================
#  myCallback
#========================================================================
def myCallback(major, minor, txPower, rssi):
  # print(f"major={major}, minor={minor}, txPower={txPower}, rssi={rssi}")
  pass

#========================================================================
#
#  main
#
#========================================================================
def main(args):
  vbeacon = vBeacon(uuid="2f234454-cf6d-4a0f-adf2-f4911ba9ffa6", 
                   major=2, minor=8877, txPower=-59, callback=myCallback, expiration=60) 

  #print("Starting vBeacon Advert")
  vbeacon.startAdvertising()    
  #print("Starting vBeacon")
  vbeacon.startScanning()    
 
  done = False
  while not done:
    #print("nearbyBeacons: ---------")
    try:
      nearby = vbeacon.getNearbyBeacons()
      for beacon in nearby: 
        #print(f"{beacon}")
        pass

      time.sleep(1.0)
    except KeyboardInterrupt:
      done = True

  vbeacon.stopAdvertising()
  vbeacon.stopScanning()


if __name__ == '__main__':
  main(sys.argv[1:])
   

