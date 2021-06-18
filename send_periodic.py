# send_periodic.py
# Written by David McCabe
# on 6/15/2021

#!/usr/bin/env python3

import os
from pyteal import *
import uuid, base64
from algosdk import algod, transaction, account, mnemonic
from periodic_payment import periodic_pay_escrow

#--------- compile & send transaction using Goal and Python SDK ----------

teal_source = compileTeal(periodic_pay_escrow, mode=Mode.Signature, version=2) 

# Write teal source to file
teal_file = str(uuid.uuid4()) + ".teal"
with open(teal_file, "w+") as f:
    f.write(teal_source)
lsig_fname = str(uuid.uuid4()) + ".tealc"

# Give sandbox the raw teal file
os.system("./sandbox copy " + teal_file)

# Compile
exit_status = os.system("./sandbox goal clerk compile -o " + lsig_fname + " " + teal_file)

if exit_status != 0:
    print(exit_status)
    raise

# Send the compiled .tealc file from sandbox back to the current directory
os.system("docker cp algorand-sandbox-algod:opt/testnetwork/Node/" + lsig_fname + " /mnt/c/Users/dmcca/Git_Projects/sandbox")

# Read it
with open(lsig_fname, "rb") as f:
    teal_bytes = f.read()
lsig = transaction.LogicSig(teal_bytes)

# Create algod client
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
acl = algod.AlgodClient(algod_token, algod_address)

# Recover the account that is wanting to delegate signature
passphrase = "left decline warrior donkey alter arch kingdom more execute crew remain ocean labor include column large kitten clever skull deal rule because eyebrow about drama"
sk = mnemonic.to_private_key(passphrase)
addr = account.address_from_private_key(sk)
print("Address of Sender/Delgator: " + addr)

# Sign the logic signature with an account sk
lsig.sign(sk)

# Save/Load logic and signature
# This can be sent to other parties so they can make the transaction(s)
'''

# Save the logic/signature
with open("logic.bytes", "wb") as j:
    j.write(lsig.logic)
with open("sig.txt", "w") as k:
    k.write(lsig.sig)

# Load the logic/signature
with open("logic.bytes", "rb") as j:
    read1 = j.read()
with open("sig.txt", "r") as k:
    read2 = k.read()
recovered = transaction.LogicSig(read1)
recovered.sig = read2

'''

# Send a transaction signed with the LogicSig

# Get suggested parameters
params = acl.suggested_params()
gen = params["genesisID"]
gh = params["genesishashb64"]
startRound = params["lastRound"] - (params["lastRound"] % 100)
endRound = startRound + 100
fee = 1000
amount = 1500
receiver = "CK56G4VABSB6H7PYYWTEPCYLSY6M7AWKSXDFVHTTLDMLYJ57RC5U7PM5TA"
lease = base64.b64decode("JC9xn+dcbJreefCH9kKcGxj1QONGiyRDKfE4FM52yhc=")

print(params["lastRound"])
print(startRound)
print(endRound)

# Create the payment transaction
txn = transaction.PaymentTxn(addr, fee, startRound, endRound, gh, receiver, amount, flat_fee=True, lease=lease)

# Create the LogicSigTransaction with contract account LogicSig
lstx = transaction.LogicSigTransaction(txn, lsig)

# Write to file
txns = [lstx]
transaction.write_to_file(txns, "p_pay.stxn")

# Print account balances
# os.system("python3 checkbalance.py")

# Send raw LogicSigTransaction to network
txid = acl.send_transaction(lstx)
print("Transaction ID: " + txid)