#!/usr/bin/python3
#===============================================================
#
#  IBeaconAdvertiser
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
#===============================================================
import argparse
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import time
import threading

from gi.repository import GLib


BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'


#---------------------------------------------------------------
#  InvalidArgsException
#---------------------------------------------------------------
class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


#---------------------------------------------------------------
#  NotSupportedException
#---------------------------------------------------------------
class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'


#---------------------------------------------------------------
#  NotPermittedException
#---------------------------------------------------------------
class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'


#---------------------------------------------------------------
#  InvalidValueLengthException
#---------------------------------------------------------------
class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'


#---------------------------------------------------------------
#  FailedException
#---------------------------------------------------------------
class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'


#---------------------------------------------------------------
#  class Advertisement 
#---------------------------------------------------------------
class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.local_name = None
        self.include_tx_power = None
        self.data = None
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
                                                    signature='s')
        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
                                                    signature='s')
        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(
                self.manufacturer_data, signature='qv')
        if self.service_data is not None:
            properties['ServiceData'] = dbus.Dictionary(self.service_data,
                                                        signature='sv')
        if self.local_name is not None:
            properties['LocalName'] = dbus.String(self.local_name)
        if self.include_tx_power is not None:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)

        if self.data is not None:
            properties['Data'] = dbus.Dictionary(
                self.data, signature='yv')
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dbus.Dictionary({}, signature='qv')
        self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dbus.Dictionary({}, signature='sv')
        self.service_data[uuid] = dbus.Array(data, signature='y')

    def add_local_name(self, name):
        if not self.local_name:
            self.local_name = ""
        self.local_name = dbus.String(name)

    def add_data(self, ad_type, data):
        if not self.data:
            self.data = dbus.Dictionary({}, signature='yv')
        self.data[ad_type] = dbus.Array(data, signature='y')

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')

    def Release(self):
      pass

#---------------------------------------------------------------
#  class IBeaconAdvertiser 
#---------------------------------------------------------------
class iBeaconAdvertiser():

  #---------------------------------------------------------------
  #  Constructor
  #---------------------------------------------------------------
  def __init__(self, uuid, major, minor, tx_power):
    self.company_id = 0x004C
    self.beacon_type = [0x02, 0x15]

    self.uuid = self._parse_uuid(uuid) 

    self.major = [(major & 0xff00)>>8, (major & 0x00ff)]  
    self.minor = [(minor & 0xff00)>>8, (minor & 0x00ff)]  
    if tx_power < 0:
      self.tx_power = [256+tx_power]
    else:
      self.tx_power = [tx_power]
   
    self.is_advert = False
 
    #self._setupAdvertiser()
      

  #---------------------------------------------------------------
  #  _setupAdvertiser 
  #---------------------------------------------------------------
  def _setupAdvertiser(self): 
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = self._find_adapter(bus)
    if not adapter:
      self.error = "LEAdvertisingManager1 interface not found"
      return -1

    adapter_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                   "org.freedesktop.DBus.Properties")

    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    self.ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)

    self.advertiser = Advertisement(bus, 0, 'peripheral')

    self.mainloop = GLib.MainLoop()

    self.ad_manager.RegisterAdvertisement(self.advertiser.get_path(), {},
                                     reply_handler=self._register_ad_cb,
                                     error_handler=self._register_ad_error_cb)

    data = self.beacon_type + self.uuid + self.major + self.minor + self.tx_power
    self.advertiser.add_manufacturer_data(self.company_id, data)

    return 0 

 
  #---------------------------------------------------------------
  #  Parse UUID string into a list of byte value
  #---------------------------------------------------------------
  def _parse_uuid(self, uuid):
    parts = uuid.split("-")
    whole = "" 
    for part in parts:
      whole += part
    return list(bytes.fromhex(whole))

 
  #---------------------------------------------------------------
  #  Unregister callack
  #---------------------------------------------------------------
  def _register_ad_cb(self):
    pass


  #---------------------------------------------------------------
  #  Register error callack
  #---------------------------------------------------------------
  def _register_ad_error_cb(self, error):
    self.error = "failed to register error: " + str(error)
    self.mainloop.quit()

  #---------------------------------------------------------------
  #  Find adaptor on bus 
  #---------------------------------------------------------------
  def _find_adapter(self, bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), 
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()
    for o, props in objects.items():
      if LE_ADVERTISING_MANAGER_IFACE in props:
        return o
    return None


  #---------------------------------------------------------------
  #  Stop advertising
  #---------------------------------------------------------------
  def stop(self):
    if self.is_advert:
      self.mainloop.quit()
      self.is_advert = False
      self.ad_manager.UnregisterAdvertisement(self.advertiser)
      dbus.service.Object.remove_from_connection(self.advertiser)


  #---------------------------------------------------------------
  #  Start advertising 
  #---------------------------------------------------------------
  def start(self):
    if self.is_advert != True:
      self.is_advert = True 
      self._setupAdvertiser()
      self.mainloop.run()  # blocks until mainloop.quit() is called


#---------------------------------------------------------------
#  Main 
#---------------------------------------------------------------
def main():
  uuid = "2f234454-cf6d-4a0f-adf2-f4911ba9ffa6"
  major = 2 
  minor = 8888 
  tx_power = -59
  advertiser = IBeaconAdvertiser(uuid, major, minor, tx_power)
  advertiser.start()                  


if __name__ == '__main__':
  main()
