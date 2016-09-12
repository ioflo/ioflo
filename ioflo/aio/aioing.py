"""
aioing.py  helper module for aio package

"""
from __future__ import absolute_import, division, print_function

import sys
import os
import subprocess

# Import ioflo libs
from ..aid.sixing import *
from ..aid.consoling import getConsole

console = getConsole()




def arpCreate(ether, host, interface="en0", temp=True):
    """
    Create arp entry for ethernet mac address ether at ip address host on interface
    If temp is false then the entry is permanent otherwise its temporary

    Assumes added /etc/sudoers entry to run arp with no password for user's group
    $ sudo visudo

    ## Group to run arp as root with no password
    Cmnd_Alias  ARP = /usr/sbin/arp
    %arp_group ALL=(ALL) NOPASSWD: ARP

    """
    temp = "temp" if temp else ""
    console.terse("{0}: Creating {1} arp entry for {2} at {3} on {4}\n".format(
                                        datetime.datetime.utcnow().isoformat(),
                                        temp,
                                        ether,
                                        host,
                                        interface))
    console.flush()

    # sudo arp -s 10.0.2.49 70:b3:d5:0:e0:30 ifscope en3 temp
    try:
        process = subprocess.run(["sudo",
                                  "/usr/sbin/arp",
                                  "-s",
                                  host,
                                  ether,
                                  "ifscope",
                                  interface,
                                  temp],
                                 check=True)
    except subprocess.SubprocessError as ex:
        console.terse("{0}: Failed Creation of {1} arp entry for {2} at {3} on {4}\n".format(
                                                datetime.datetime.utcnow().isoformat(),
                                                temp,
                                                ether,
                                                host,
                                                interface))
    console.flush()


def arpDelete(host, interface="en0"):
    """
    Delete arp entry for ip address host on interface

    Assumes added /etc/sudoers entry to run arp with no password for user's group
    $ sudo visudo

    ## Group to run arp as root with no password
    Cmnd_Alias  ARP = /usr/sbin/arp
    %arp_group ALL=(ALL) NOPASSWD: ARP

    """

    console.terse("{0}: Deleting arp entry at {1} on {2}\n".format(
                                        datetime.datetime.utcnow().isoformat(),
                                        host,
                                        interface))
    console.flush()

    # sudo arp -d 10.0.2.49 ifscope en3
    try:
        process = subprocess.run(["sudo",
                                  "/usr/sbin/arp",
                                  "-d",
                                  host,
                                  "ifscope",
                                  interface],
                                 check=True)
    except subprocess.SubprocessError as ex:
        console.terse("{0}: Failed Deletion of arp entry at {1} on {2}\n".format(
                                                datetime.datetime.utcnow().isoformat(),
                                                host,
                                                interface))
    console.flush()



try:  # only if netifaces installed
    import netifaces

except ImportError:
    pass

else:
    def getDefaultHost():
        """
        Gets host ip address of default interface using netifaces

        import netifaces
        >>> def_gw_device = netifaces.gateways()['default'][netifaces.AF_INET][1]
        This will get you the name of the device used by the default IPv4 route. You can get the MAC address of that interface like this:

        >>> macaddr = netifaces.ifaddresses('enp0s25')[netifaces.AF_LINK][0]['addr']

        """
        iface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        info = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
        host = info['addr']
        return host

    def getDefaultBroadcast():
        """
        Gets host ip address of default interface using netifaces

        import netifaces
        >>> def_gw_device = netifaces.gateways()['default'][netifaces.AF_INET][1]
        This will get you the name of the device used by the default IPv4 route. You can get the MAC address of that interface like this:

        >>> macaddr = netifaces.ifaddresses('enp0s25')[netifaces.AF_LINK][0]['addr']

        """
        iface =  netifaces.gateways()['default'][netifaces.AF_INET][1]
        info = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
        bcast = info['broadcast']
        return bcast


