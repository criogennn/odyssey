import json
import time
import datetime
from web3 import Web3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome(executable_path="path to chromedriver.exe")

hop_protocol = "https://app.hop.exchange/#/send?token=ETH&sourceNetwork=optimism&destNetwork=arbitrum"
optimism_url = "https://mainnet.optimism.io/"
hop_address = "0x86cA30bEF97fB651b8d866D45503684b90cb3312"
hop_abi = '[{"inputs":[{"internalType":"contract IL2_Bridge","name":"_bridge","type":"address"},{"internalType":"contract IERC20","name":"_l2CanonicalToken","type":"address"},{"internalType":"bool","name":"_l2CanonicalTokenIsEth","type":"bool"},{"internalType":"contract IERC20","name":"_hToken","type":"address"},{"internalType":"contract ISwap","name":"_exchangeAddress","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"attemptSwap","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"bridge","outputs":[{"internalType":"contract IL2_Bridge","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"exchangeAddress","outputs":[{"internalType":"contract ISwap","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"hToken","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"l2CanonicalToken","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"l2CanonicalTokenIsEth","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"bonderFee","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint256","name":"destinationAmountOutMin","type":"uint256"},{"internalType":"uint256","name":"destinationDeadline","type":"uint256"}],"name":"swapAndSend","outputs":[],"stateMutability":"payable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

web3 = Web3(Web3.HTTPProvider(optimism_url))

print(web3.isConnected())

print(web3.eth.get_transaction_receipt('0x43e90bf000138ba876a48ce6b7ec0d4ff2bb6cd23485604fa25eb2159e35105d'))

amount = input('ETH to bridge: ')

addresses = ['address1', 'address2']
keys = ['key1', 'key2']
i = 0

try:
    driver.get(url = hop_protocol)
    driver.implicitly_wait(10)
    eth_input = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[2]/div[2]/div[2]/div/input')
    eth_input.clear()
    eth_input.send_keys(amount)
    time.sleep(5)
    while i < 8:
        bonderFee = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[6]/div/div[1]/h6[2]')
        amountOutMin = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[6]/div/div[2]/h6[2]')
        bonderFee = web3.toWei((bonderFee.text.replace(' ETH', '')), 'ether')
        amountOutMin = web3.toWei((amountOutMin.text.replace(' ETH', '')), 'ether')
        destinationAmountOutMin = int(amountOutMin - amountOutMin/100)

        dt = datetime.datetime.now()
        epoch = int(dt.timestamp() + 180)

        address= web3.toChecksumAddress(addresses[i])
        private_key = keys[i]

        nonce = web3.eth.getTransactionCount(address)

        contract = web3.eth.contract(address = hop_address, abi = hop_abi)

        value = web3.toWei(amount, 'ether')

        hop_tx = contract.functions.swapAndSend(42161, address, value, bonderFee, amountOutMin, epoch, destinationAmountOutMin, epoch).buildTransaction({
            'from': address,
            'nonce': nonce,
            'value': value,
            'gas': 300000,
            'gasPrice': web3.toWei(0.001, 'gwei')
        })

        signed_tx = web3.eth.account.signTransaction(hop_tx, private_key)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        print(web3.toHex(tx_hash))
        i = i + 1
finally:
    driver.close()
    driver.quit()
