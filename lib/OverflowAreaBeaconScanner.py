#!/usr/bin/python3
#========================================================================
#
#  OverflowAreaBeaconScanner 
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
from __future__ import absolute_import, print_function, unicode_literals
from optparse import OptionParser, make_option
import sys, getopt
import dbus
import dbus.mainloop.glib

from gi.repository import GLib
sys.path.append('lib')
import bluezutils
from HammingEcc import HammingEcc


class OverflowAreaBeaconScanner:

  #=========================================================
  #
  #  Constructor
  #
  #=========================================================
  def __init__(self, callback):

    # Get mainloop 
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Connect to the system bus
    self.bus = dbus.SystemBus()

    # Find available adapter (usually just one)
    self.adapter = bluezutils.find_adapter()


    # Setup interface added callback 
    self.bus.add_signal_receiver(
        self.interfaces_added,
        dbus_interface = "org.freedesktop.DBus.ObjectManager",
        signal_name = "InterfacesAdded")

    # Setup properties_changed callback 
    self.bus.add_signal_receiver(
        self.properties_changed,
        dbus_interface = "org.freedesktop.DBus.Properties",
        signal_name = "PropertiesChanged",
        arg0 = "org.bluez.Device1",
        path_keyword = "path")

    # Initialize devices
    self.devices = {}

    # Get ad manager
    om = dbus.Interface(self.bus.get_object("org.bluez", "/"),
         "org.freedesktop.DBus.ObjectManager")

    objects = om.GetManagedObjects()
    for path, interfaces in objects.items():
      if "org.bluez.Device1" in interfaces:
        self.devices[path] = interfaces["org.bluez.Device1"]

    # Initialize an empty scan filter 
    self.scan_filter = dict()

    # No scanning initially
    self.is_scanning = False

    # Save user callback
    self.callback = callback

  #=========================================================
  #
  #  Set filter 
  #
  #=========================================================
  def set_filter(self, uuids=[], rssi=-1, pathloss=-1, transport=''):

    if len(uuids) > 0: 
       self.scan_filter.update({ "UUIDs": uuids })

    if rssi != -1:
       self.scan_filter.update({ "RSSI": dbus.Int16(rssi) })

    if pathloss != -1:
       self.scan_filter.update({ "Pathloss": dbus.UInt16(pathloss) })

    if transport != '':
       self.scan_filter.update({ "Transport": transport })

 
  #=========================================================
  #
  #  clear filter 
  #
  #=========================================================
  def clear_filter(self):
    self.scan_filter = dict()


  #=========================================================
  #
  #  Start Scanning 
  #
  #=========================================================
  def start(self):
    if self.is_scanning is not True: 
      self.adapter.SetDiscoveryFilter(self.scan_filter)
      self.adapter.StartDiscovery()
      self.is_scanning = True
      self.mainloop = GLib.MainLoop()
      self.mainloop.run()
 

  #=========================================================
  #
  #  Stop scanning 
  #
  #=========================================================
  def stop(self):
    if self.is_scanning:
      self.adapter.StopDiscovery()
      self.mainloop.quit()
      self.is_scanning = False


  #========================================================================
  #
  #  Interface added callback 
  #
  #========================================================================
  def interfaces_added(self, path, interfaces):
    properties = interfaces["org.bluez.Device1"]

    if not properties:
      return

    if path in self.devices:
      dev = self.devices[path]
      self.devices[path].update(properties)
    else:
      self.devices[path] = properties

    if "Address" in self.devices[path]:
      address = properties["Address"]
    else:
      address = "<unknown>"

    self.find_beacon(address, self.devices[path])


  #========================================================================
  #
  #  Properties changed callback 
  #
  #========================================================================
  def properties_changed(self, interface, changed, invalidated, path):
    if interface != "org.bluez.Device1":
      return

    if path in self.devices:
      dev = self.devices[path]
      self.devices[path].update(changed)
    else:
      self.devices[path] = changed

    if "Address" in self.devices[path]:
      address = self.devices[path]["Address"]
    else:
      address = "<unknown>"

    self.find_beacon(address, self.devices[path])

  #========================================================================
  #
  #  Find overflowArea beacons
  #
  #========================================================================
  def find_beacon(self, address, props):
    byte_array = []
    packet_array = []
    if 'ManufacturerData' in props.keys():
      if 0x004c in props['ManufacturerData']:
        for b in props['ManufacturerData'][0x004c]:
          hex_str = '{:02x}'.format(int(b))
          packet_array.append(hex_str[0])
          packet_array.append(hex_str[1])
          byte_array.append(int(b))

      packet = ''.join(packet_array)

      if packet[0:2] == '01':
        # Remove the first byte which is '01' indicating overflow packet
        bt_addr = props['Address']
        rssi = int(props['RSSI'])
        self.beaconCallback("OverflowArea", bt_addr, rssi, 
                            byte_array[1:len(byte_array)], props)

  #========================================================================
  #  Extract beacon bytes 
  #========================================================================
  def extractBeaconBytes(self, byteBuffer, countToExtract=5):

    # Pi per-byte bit ordering is reversed from iOS 
    bitBuffer = HammingEcc().bytesToBits(byteBuffer, bigEndian=True)
    byteBuffer = HammingEcc().bitsToBytes(bitBuffer, bigEndian=False)

    matchingByte = 0xaa 
    payload = []

    # buffer.removeFirst(bytePosition)
    bytePosition = 8
    buffer = byteBuffer[bytePosition:len(byteBuffer)]

    bitBuffer = HammingEcc().bytesToBits(buffer, bigEndian=False)

    hammingBitsToDecode = 8*(countToExtract + 1) + 7 

    # bitBuffer.removeLast(bitBuffer.count - hammingBitsToDecode)
    bitBuffer = bitBuffer[0:hammingBitsToDecode] 

    goodBits = HammingEcc().decodeBits(bitBuffer) 

    if len(goodBits) > 0:
      bytes = HammingEcc().bitsToBytes(goodBits)
      if bytes[0] == matchingByte:
        payload = bytes[1:len(bytes)]
      else:
        print("This is not our overflow advert")
    else:
      print("Overflow area advert does not have our beacon data or it is corrupted")

    return payload


  #========================================================================
  #  Beacon callback
  #========================================================================
  def beaconCallback(self, beaconType, bt_addr, rssi, packet, props):
    payload = self.extractBeaconBytes(packet, 5)
    if len(payload) == 5:
      major = payload[0] * 256 + payload[1]
      minor = payload[2] * 256 + payload[3]     
      txPower = payload[4]-256
      self.callback(major, minor, txPower, rssi)

    
#========================================================================
#  Custom callack
#========================================================================
def myCallback(major, minor, txPower, rssi):
  print(f"major={major}, minor={minor}, txPower={txPower}, rssi={rssi}")
   
#========================================================================
#
#  main
#
#========================================================================
def main(args):
  scanner = OverflowAreaScanner(myCallback)
  scanner.start()     


if __name__ == '__main__':
  main(sys.argv[1:])
   

