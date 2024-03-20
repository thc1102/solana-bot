from solders.message import Message
from solders.keypair import Keypair
from solders.instruction import Instruction
from solders.hash import Hash
from solders.transaction import Transaction
from solders.pubkey import Pubkey

program_id = Pubkey.default()
print(program_id)
arbitrary_instruction_data = bytes([1])
print(arbitrary_instruction_data)
accounts = []
instruction = Instruction(program_id, arbitrary_instruction_data, accounts)
print(instruction)
payer = Keypair()
print(payer)
message = Message([instruction], payer.pubkey())
print(message)
blockhash = Hash.default()  # replace with a real blockhash
print(blockhash)
tx = Transaction([payer], message, blockhash)
print(tx)
