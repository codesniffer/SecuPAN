import threading
import time
import math

totalBufferSize = 1024
allocatedPortionOfBuffer = 0
unAllocatedPortionOfBuffer = 0

packetTimer = 60