from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests
import time
import telebot

api_tg = 'tg api'
api_bscscan = 'api bscscan' # Bscscan API брать тут - https://bscscan.com/myapikey
bot = telebot.TeleBot(api_tg)

w3 = Web3(Web3.HTTPProvider('https://bsc.blockpi.network/v1/rpc/public'))

w3.middleware_onion.inject(geth_poa_middleware, layer=0)


@bot.message_handler(content_types=['text'])
def start_message(message):
    response = requests.post(
        f'https://api.bscscan.com/api?module=account&action=txlist&address=0x8b6c8fd93d6f4cea42bbb345dbc6f0dfdb5bec73&startblock=0&endblock=99999999&page=1&offset=10&sort=desc&apikey={api_bscscan}').json()
    # Адреса валидаторов, которые подбирают <5 gwei (по умолчанию передаю в апи первого валидатора):
    # Validator: LEGENDA 0x295e26495cef6f69dfa69911d9d8e4f3bbadb89b
    # Validator: LEGENDA III 0x8b6c8fd93d6f4cea42bbb345dbc6f0dfdb5bec73
    block_number = int(response['result'][0]['blockNumber'])

    block = w3.eth.getBlock(block_number, full_transactions=False)

    transaction_hashes = block['transactions']

    all_gwei = []

    print(f"Transaction hashes in block {block_number}:")
    for tx_hash in transaction_hashes:
        transaction_hash = tx_hash.hex()

        transaction = w3.eth.getTransaction(transaction_hash)

        print("Transaction information:")
        print(f"  Hash: {transaction_hash}")
        print(f"  Gas linit: {transaction['gas']}")
        print(f"  GWEI: {Web3.fromWei(transaction['gasPrice'], 'gwei')} gwei")
        all_gwei.append(Web3.fromWei(transaction['gasPrice'], 'gwei'))

    print(f'\nMinimum GWEI: {min(all_gwei[:-1])}')
    bot.send_message(message.chat.id, f'\nIn the block #{block_number} the Minimum GWEI: {min(all_gwei[:-1])}')

bot.polling()
