from threading import Thread, Lock
from time import time_ns
from random import random
from random import randrange
import rsa
import hashlib
from collections import deque

no_of_miners = 3
miner_incentive = 8000000#NYTP = 8 NYTC
mined_blocks_per_miner = 2
rsa_size = 512
difficulty = 1 << 236  # keep it larger than or equal to 1 << 236
transaction_rate = .5  # per second. Max allowed: 10 per seconds
i = 0
transaction_pool = deque()
blockchain = []
transaction_lock = Lock()  # lock for synchronizing the transaction_pool
blockchain_lock = Lock()  # lock for synchronizing the blockchain
plock = Lock()  # lock for avoiding race condition on stdout
miners = []


class Transaction_input:

    def __str__(self):
        rv = "[" + str(self.block_id) + "," + str(self.transaction_id) + "," + str(
            self.output_id) + "]"
        return rv

    def __init__(self, block_id, transaction_id, output_id):
        self.block_id = block_id
        self.transaction_id = transaction_id
        self.output_id = output_id



class Transaction_output:

  def __str__(self):
    rv = "[" + str(self.new_owner_index) + "," + str(self.amount) + "]"
    return rv

  def __init__(self, new_owner_index: int, amount: int):
    self.new_owner_index = new_owner_index
    self.amount = amount
    self.spent = False


class Transaction:

  def __str__(self):
    rv = "[" + str(self.owner_index) + "," + str(self.timestamp) + ",["
    for j in range(len(self.inputs)):
      rv += str(self.inputs[j])
      if j != len(self.inputs) - 1:
        rv += ","
    rv += "],["
    for j in range(len(self.outputs)):
      rv += str(self.outputs[j])
      if j != len(self.outputs) - 1:
        rv += ","
    rv += "]"
    return rv

    def __init__(self, owner_index: int, inputs, outputs):
        self.owner_index = owner_index
        self.timestamp = time_ns()
        self.inputs = inputs
        self.outputs = outputs
        self.signature = rsa_message_sign(str(self), miners[owner_index].d,
            miners[owner_index].n)


def rsa_message_sign(message: str, d: int, n: int) -> int:
  digest = hashlib.sha256(message.encode("ascii", "ignore"))
  return pow(int(digest.hexdigest(), 16), d, n)


def rsa_signature_verify(message: str, signature: int, e: int, n: int) -> bool:
  expected_digest = pow(signature, e, n)
  digest = int(
    hashlib.sha256(message.encode("ascii", "ignore")).hexdigest(), 16)
  return expected_digest == digest


class Block:

  def __init__(self, transactions, pred_digest: int, block_number: int,block_miner_index: int, timestamp, nonce: int):
    self.transactions = transactions #list of all transactions in the block
    self.pred_digest = pred_digest # previous block's digest (SHA256)
    self.block_number = block_number # number of predecessors in the blockchain
    self.block_miner_index = block_miner_index 
    self.nonce = nonce
    self.timestamp = timestamp
    self.digest = int(
      hashlib.sha256(str(self).encode("ascii", "ignore")).hexdigest(), 16)

  def __str__(self):
    rv = "[" + str(self.pred_digest) + "," + "["
    for j in range(len(self.transactions)):
      rv += (str(self.transactions[j]) + ":" + str(self.transactions[j].signature))
      if j != len(self.transactions) - 1:
        rv += ","
    rv += ("]," + str(self.block_number) + "," + str(self.block_miner_index) + "," + str(self.timestamp) + "," + str(self.nonce) + "]")
    return rv


def thread_safe_print(string: str):
  global plock
  plock.acquire()
  print(string)
  plock.release()


def send_transaction(transaction: Transaction):
  global transaction_lock
  transaction_lock.acquire()
  transaction_pool.append(transaction)
  transaction_lock.release()


def prune(blockchain):
  rv = dict()
  for b in blockchain:
    rv[b.block_number] = b
  rv_list = []
  for k in range(len(rv)):
      rv_list.append(rv[k])
  return rv_list


def make_transaction(sender: int, receivers, amount: int):
  #makes a transaction from sender to ALL receivers of given amount
  global blockchain_lock, transaction_lock, blockchain
  outs = []
  ins = []
  for j in receivers:
    outs.append(Transaction_output(j, amount))
  total = amount * len(receivers)
  blockchain_lock.acquire()
  blockchain = prune(blockchain)
  spent_outs = set()
  for b in range(len(blockchain)):
    for t in range(len(blockchain[b].transactions)):
      for o in range(len(blockchain[b].transactions[t].outputs)):
        output = blockchain[b].transactions[t].outputs[o]
        if total > 0 and output.new_owner_index == sender and not output.spent:
          output.spent = True
          spent_outs.add(output)
          ins.append(Transaction_input(b, t, o))
          total -= output.amount
  if total > 0:
    thread_safe_print("Error: insufficient fund!")
    for o in spent_outs:#undo expenditures!
      o.spent = False
    blockchain_lock.release()
    return False
  blockchain_lock.release()
  if total < 0:# the change goes back to sender's wallet!
    outs.append(Transaction_output(sender, -total))
    miners[sender].balance += total
  t = Transaction(sender, ins, outs)
  send_transaction(t)
  thread_safe_print("Transaction sent: " + str(t))
  return True

def initiate_transaction(sender: int, transaction_rate: float):
  miners[sender].balance_lock.acquire()
  if miners[sender].balance > 1000 and random() > (1 - transaction_rate / 10.0):
        #spend half of the account balance
        receivers = []
        for j in range(no_of_miners):
          if j != sender:
            receivers.append(j)
        val = miners[sender].balance // (2 * len(receivers))
        if make_transaction(sender, receivers, val):
          miners[sender].balance -= len(receivers) * val
  miners[sender].balance_lock.release()
def miner_run(index: int):
  global transaction_lock, blockchain, blockchain_lock, no_of_miners
  public_key = (miners[index].n, miners[index].e)
  start_time = time_ns()
  nonce = 0
  mining_incentive = Transaction(
    index,
    [], #no input for this special transaction 
    [Transaction_output(index, miner_incentive)])
  transactions = [mining_incentive]
  transaction_lock.acquire()
  for t in transaction_pool:
    transactions.append(t)
  transaction_lock.release()
  block_index = -1
  pred_digest = 0
  count = 0
  while count < mined_blocks_per_miner:
    if (time_ns() -
        start_time) // 1000000 > 100:  #updates every tenth of a second!
      mining_incentive = Transaction(
        index,
        [], #no input for this special transaction
        [Transaction_output(index, miner_incentive)])
      transactions = [mining_incentive]
      transaction_lock.acquire()
      for t in transaction_pool:
        transactions.append(t)
      transaction_lock.release()
      longest_chain = -1
      blockchain_lock.acquire()
      for block in blockchain:
        if block.block_number > longest_chain:
          longest_chain = block.block_number
          pred_digest = block.digest
      blockchain_lock.release()
      block_index = longest_chain
      start_time = time_ns()
      initiate_transaction(index, transaction_rate)

    #try the proposed block with a new nonce
    proposed = Block(transactions, pred_digest, block_index + 1, index,
                     start_time, nonce)

    if proposed.digest < difficulty:  #miner wins the lottery!
      count += 1
      transaction_lock.acquire()
      blockchain_lock.acquire()
      red_flag = False
      for j in range(1, len(transactions)):
        if transactions[j] not in transaction_pool:
          red_flag = True
          break
      if not red_flag:
        miners[index].balance += miner_incentive
        for j in range(1, len(transactions)):
          transaction_pool.remove(transactions[j])
          for o in transactions[j].outputs:
            miners[o.new_owner_index].balance_lock.acquire()
            miners[o.new_owner_index].balance += o.amount
            miners[o.new_owner_index].balance_lock.release()
        blockchain.append(proposed)
      blockchain_lock.release()
      transaction_lock.release()
      thread_safe_print(
          "new block: " +
          str(proposed))# + "\n\t\t" + str(proposed.digest))
      for miner in miners:
        thread_safe_print("miner's " + str(miner.index) + " balance is " +  str(miner.balance / 1000000))
      nonce = 0
    else:
      nonce += 1


class Miner:

  def __init__(self, index: int, private_key, public_key):
    self.index = index
    self.n = public_key[0]
    self.e = public_key[1]
    self.d = private_key
    self.balance = 0
    self.balance_lock = Lock()

start = time_ns()
for k in range(no_of_miners):
  public_key, private_key = rsa.newkeys(rsa_size)
  miner = Miner(k, private_key.d, (public_key.n, public_key.e))
  miners.append(miner)

threads = []
for k in range(0, no_of_miners):
  thread = Thread(target=miner_run, args=(k, ))
  threads.append(thread)
  thread.start()
for thread in threads:
  thread.join()
total = 0
for miner in miners:
  thread_safe_print("miner's " + str(miner.index) + " balance is " +
                    str(miner.balance / 1000000))
  total += miner.balance
thread_safe_print("Total coins: " + str(total / 1000000))
total_outs = 0
for t in transaction_pool:
  for o in t.outputs:
    total_outs += o.amount
thread_safe_print("Total coins in the pool: " + str(total_outs / 1000000))
thread_safe_print("Total time of this experiment in seconds: " + str(round((time_ns()-start)/1000000000.0)))