# checkbalance.py
# Algorand Dev Project 01

from algosdk.v2client import algod
from algosdk import mnemonic

# Connect to the Client
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_client = algod.AlgodClient(algod_token, algod_address)

p = ["left decline warrior donkey alter arch kingdom more execute crew remain ocean labor include column large kitten clever skull deal rule because eyebrow about drama",
     "cannon install eight square fiber crucial talk lock wrong turtle giraffe hair street mass chunk donor trip speed quote pact movie lend strategy abstract imitate"]
# Query for Wallet Info
for mnemonic_phrase in p:

    # Generate + Print Account Info
    private_key = mnemonic.to_private_key(mnemonic_phrase)
    account_address = mnemonic.to_public_key(mnemonic_phrase)

    print("Account Address: {}".format(account_address))

    account_info = algod_client.account_info(account_address)
    print("Account Balance: {} microAlgos".format(account_info.get('amount')))
