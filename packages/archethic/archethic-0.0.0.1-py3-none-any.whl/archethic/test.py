import archethic
from pprint import pprint
sk, pk = archethic.derive_keypair("mysuperpassphraseorseed", 0)

transaction = archethic.TransactionBuilder("transfer")

address = archethic.derive_address("python", 0)
transaction.add_uco_transfer(address, 1)
pprint(transaction.previous_signature_payload().hex())
transaction.build("mysuperpassphraseorseed", 0)
pprint(transaction.previous_signature_payload().hex())