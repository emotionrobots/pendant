#!/usr/bin/python3
#========================================================================
#
#  iBeaconScanner.py
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
import sys, getopt, time

sys.path.append('lib')
from beacontools import BeaconScanner, IBeaconFilter 


class iBeaconScanner:

  #========================================================================
  #
  #  Constructor
  #
  #========================================================================
  def __init__(self, uuid, callback):
    self.isScanning = False
    self.callback = callback
    self.uuid = uuid 
    self.iBeaconScanner = BeaconScanner(self.beaconCallback, 
        device_filter=IBeaconFilter(uuid=self.uuid) )

  #========================================================================
  #
  #  Start Scanning 
  #
  #========================================================================
  def start(self):
    if self.isScanning != True:
      self.iBeaconScanner = BeaconScanner(self.beaconCallback, 
                 device_filter=IBeaconFilter(uuid=self.uuid) )
      self.iBeaconScanner.start()
      self.isScanning = True
 
  #========================================================================
  #
  #  Stop Scanning 
  #
  #========================================================================
  def stop(self):
    if self.isScanning:
      self.iBeaconScanner.stop()
      self.isScanning = False


  #========================================================================
  #  Beacon callback
  #========================================================================
  def beaconCallback(self, scanner, beaconType, t_addr, rssi, packet, props):
    if beaconType == "iBeacon":
      major = props['major']
      minor = props['minor']
      txPower = packet.tx_power
      self.callback(major, minor, txPower, rssi) 
    


#========================================================================
#  myCallback
#========================================================================
def myCallback(major, minor, txPower, rssi):
  print(f"major={major}, minor={minor}, txPower={txPower}, rssi={rssi}")


#========================================================================
#
#  main
#
#========================================================================
def main(args):
  scanner = iBeaconScanner(uuid="2f234454-cf6d-4a0f-adf2-f4911ba9ffa6", callback=myCallback) 
  print("Starting iBeaconScanner")
  scanner.start()     

  done = False
  while not done:
    try:
      time.sleep(1.0)
    except KeyboardInterrupt:
      done = True

  scanner.stop()


if __name__ == '__main__':
  main(sys.argv[1:])
   

