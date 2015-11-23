"""
asynchronous (nonblocking) serial io package


To prevent circular import dependencies, the policy is that any sub packages
or modules must not import this __init__.py file or the serial package.
This allows future proofed external import dependencies on the toplevel names
in this package that are imported here from sub packages or modules
for the purpose of hiding the internal structure of thid package.
"""

from .serialing import ConsoleNb, DeviceNb, SerialNb, Driver
