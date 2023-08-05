from random import randint
import time
import zmq
from aicmder.service import CLIENT_PORT, WORKER_PORT

LRU_READY = "\x01"

context = zmq.Context(1)
worker = context.socket(zmq.REQ)

identity = "%04X-%04X" % (randint(0, 0x10000), randint(0,0x10000))
worker.setsockopt_string(zmq.IDENTITY, identity)
worker.connect(f"tcp://localhost:{WORKER_PORT}")

print("I: (%s) worker ready" % identity)
worker.send_string(LRU_READY)

cycles = 0
while True:
    msg = worker.recv_multipart()
    if not msg:
        break

    cycles += 1
    if cycles>0 and randint(0, 5) == 0:
        print("I: (%s) simulating a crash" % identity)
        break
    elif cycles>3 and randint(0, 5) == 0:
        print("I: (%s) simulating CPU overload" % identity)
        time.sleep(3)
    print("I: (%s) normal reply" % identity)
    time.sleep(1) # Do some heavy work
    worker.send_multipart(msg)