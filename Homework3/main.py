from threading import Thread, Lock
from time import sleep
from random import random
from random import randrange
import hashlib
import rsa

no_of_generals = 10
rsa_size = 512
byzantine_prob = .8
delay = .0001
i = 0
lock = Lock() # lock for synchronizing the shared inbox
plock = Lock() # lock for avoiding race condition on stdout
generals_public_keys = set()
generals = []
shared_inbox = []


def rsa_message_sign(message: str, d: int, n: int) -> int:
  digest = hashlib.sha256(message.encode("ascii", "ignore"))
  return pow(int(digest.hexdigest(), 16), d, n)


def rsa_signature_verify(message: str, signature: int, e: int, n: int) -> bool:
  expected_digest = pow(signature, e, n)
  digest = int(
    hashlib.sha256(message.encode("ascii", "ignore")).hexdigest(), 16)
  return expected_digest == digest


class Message:

  def __init__(self, header, content):  #header is a (bool, int, int)
    self.relay = header[0]
    self.src = header[1]  #int
    self.trg = header[2]  #int
    self.text = content[0]
    self.sig_set = content[
      1]  # set of pairs (signature, public_key) where public_key = (n,e)

  def __str__(self):
    if self.relay:
      rv = "relay message from " + str(self.src) + " to " + str(
        self.trg) + " and content: " + str(self.text) + " and sig set ["
    else:
      rv = "broadcast message from " + str(self.src) + " to " + str(
        self.trg) + " and content: " + str(self.text) + " and sig set ["
    i = len(self.sig_set)
    for (sig, public_key) in self.sig_set:
      rv += ("(" + str(sig)[:7] + "..., ")
      rv += ("(" + str(public_key[0])[:7] + "..., ")
      rv += ("(" + str(public_key[1]) + ")")
      i -= 1
      if i:
        rv += ", "
      else:
        rv += "]"
    return rv


class General:

  def __init__(self, index: int, private_key, public_key, byzantine: bool):
    #global general_index
    self.index = index
    self.n = public_key[0]
    self.e = public_key[1]
    self.d = private_key
    self.byzantine = byzantine
    generals_public_keys.add(public_key)


def thread_safe_print(string: str):
  global plock
  plock.acquire()
  print(string)
  plock.release()


def send_message(message: Message
):  # adds the message to a random index of the shared_inbox
  global lock
  lock.acquire()
  shared_inbox.insert(randrange(0, len(shared_inbox) + 1), message)
  lock.release()


  #shared_inbox.append(message)
def send_to_all(relay: bool, source: int, content):
  thread_safe_print("send to all from " + str(source))
  for general in generals:
    if source != general.index:
      header = (relay, source, general.index)
      send_message(Message(header, content))


def send_to_group(relay: bool, source: int, content, first_recepient: int,
last_recepient: int):
  thread_safe_print("Send from general #" + str(source) + " to generals #" +
str(first_recepient) + " ... " + str(last_recepient - 1))
  for general in generals:
    if source != general.index and general.index >= first_recepient and general.index < last_recepient:
      header = (relay, source, general.index)
      send_message(Message(header, content))


def receive_message(recepient: int) -> Message:
  global lock
  rv = None
  lock.acquire()
  for message in shared_inbox:
    if message.trg == recepient:
      rv = message
      shared_inbox.remove(message)
      break
  lock.release()
  thread_safe_print("General # " + str(recepient) + " received " + str(rv))
  return rv


def verify_signatures(recepient: int, message: Message) -> bool:
  unique_public_keys = set()
  for (sig, public_key) in message.sig_set:
    unique_public_keys.add(public_key)
  if len(message.sig_set) > len(unique_public_keys):
   thread_safe_print(
      "General #" + str(recepient) +
      ": Verification failed. Reason: a party has signed the message multiple times"
)
  return False  #a party has signed multiple times...
  if (generals[0].n, generals[0].e) not in unique_public_keys:
    thread_safe_print(
      "General #" + str(recepient) +
      ": Verification failed. Reason: the commander hasn't signed the message")
    return False  #the commander hasn't signed the message
  if (generals[recepient].n, generals[recepient].e) in unique_public_keys:
    thread_safe_print(
      "General #" + str(recepient) +
      ": Verification failed. Reason: current recepient has already signed this message, no need to sign again"
)
    return False  #current recepient has already signed this message, no need to sign again
  for (sig, public_key) in message.sig_set:
    if public_key not in generals_public_keys:
      thread_safe_print("General #" + str(recepient) +
                        ": Verification failed: Reason: public_key " +
                        str(public_key)[:7] + "... is unknown!")
      return False
    if not rsa_signature_verify(message.text, sig, public_key[1],
                                public_key[0]):
      thread_safe_print("General #" + str(recepient) +
                        ": Verification failed. Reason: signature " +
                        str(sig)[:7] + "... is not from " +
                        str(public_key)[:7] + "..." + str(public_key)[-7:] +
                        " on text " + message.text)
      return False
  return True


def general_run(index: int):
  public_key = (generals[index].n, generals[index].e)
  if not index:  # the commander
    sig_set = [(rsa_message_sign("attack", generals[0].d,
                                 generals[0].n), public_key)]
    content = ("attack", sig_set)
    thread_safe_print("The commander " +
                      " is broadcastng the attack message...")
    if not generals[0].byzantine:  #if commander is not byzantine
      send_to_all(False, 0, content)  # command everyone to attack
    else:  #if commander is byzantine
      sig_set = [(rsa_message_sign("retreat", generals[0].d,
                                   generals[0].n), public_key)]
      content2 = ("retreat", sig_set)
      send_to_group(False, 0, content, 1, no_of_generals // 2 + 1)
      # command half of the generals to attack
      send_to_group(False, 0, content2, no_of_generals // 2 + 1,
                    no_of_generals)
      # command the other half to retreat
  else:
    output = None
    first = True
    while True:
      sleep(delay)  #simulating network delays
      message = receive_message(index)
      if not message:
        break
      if verify_signatures(index, message):
        sig_set = []
        sig_set.extend(message.sig_set)
        if generals[index].byzantine:  #flip the message
          text = "attack" if message.text == "retreat" else "retreat"
        else:  # don't change the message
          text = message.text
        signature = rsa_message_sign(text, generals[index].d,
                                     generals[index].n)
        sig_set.append((signature, public_key))
        content = (text, sig_set)
        if first:
          output = message.text
          first = False
        elif output != message.text:
          output = None
        thread_safe_print("General #" + str(index) +
                          " is relaying the message " + message.text +
                          " by sending " + text)
        send_to_all(True, index, content)
    sleep(1)  # wait before consensus
    if not generals[index].byzantine:
      thread_safe_print("Honest general " + str(index) + "'s output: " +
                        str(output))
    else:
      thread_safe_print("Byzantine general " + str(index) +
                        "'s output doesn't matter!")


for k in range(no_of_generals):
  public_key, private_key = rsa.newkeys(rsa_size)
  general = General(k, private_key.d, (public_key.n, public_key.e),
                    random() > (1 - byzantine_prob))
  generals.append(general)

Thread(target=general_run,
       args=(0, )).start()  # commander's thread starts early
threads = []
for k in range(1, no_of_generals):
  thread = Thread(target=general_run, args=(k, ))
  threads.append(thread)
  thread.start()
for thread in threads:
  thread.join()
if generals[0].byzantine:
  thread_safe_print("Commander is byzantine!")
else:
  thread_safe_print("Commander is honest and wants to attack!")
thread_safe_print("Are all honest generals in-consensus?")