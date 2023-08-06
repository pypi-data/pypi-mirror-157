import archethic
from pprint import pprint
sk, pk = archethic.derive_keypair("mysuperpassphraseorseed", 0)

transaction = archethic.TransactionBuilder("transfer")

address = archethic.derive_address("python", 0)
pprint(transaction.json())
transaction.add_uco_transfer(address, 100)
print(transaction.previous_signature)
transaction.build("mysuperpassphraseorseed", 0)
print(transaction.previous_signature.hex())
print(len(transaction.previous_signature.hex()))
pprint(transaction.json())