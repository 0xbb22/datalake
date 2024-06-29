from web3 import Web3
from eth_account import Account
import json
import time
from colorama import init, Fore, Style

# Inisialisasi colorama
init(autoreset=True)

# Inisialisasi koneksi ke RPC
rpc_url = 'https://rpc-mokotow.data-lake.co'
chain_id = 2676
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Pastikan koneksi berhasil
if not w3.is_connected():
    print(Fore.RED + "Koneksi ke RPC gagal")
    exit()

# Fungsi untuk membaca private key dari file
def read_private_key(filename='private_key.txt'):
    try:
        with open(filename, 'r') as file:
            private_key = file.read().strip()
        return private_key
    except FileNotFoundError:
        print(Fore.RED + f"File {filename} tidak ditemukan.")
        exit()

# Fungsi untuk membuat alamat baru
def create_new_addresses(count):
    addresses = []
    for _ in range(count):
        account = Account.create()
        addresses.append((account.address, account.key.hex()))
    return addresses

# Fungsi untuk menyimpan alamat ke dalam file
def save_addresses_to_file(addresses, filename='addresses.json'):
    try:
        with open(filename, 'r') as file:
            existing_addresses = json.load(file)
    except FileNotFoundError:
        existing_addresses = []

    with open(filename, 'w') as file:
        existing_addresses.extend(addresses)
        json.dump(existing_addresses, file, indent=4)

# Fungsi untuk membaca alamat dari file
def read_addresses_from_file(filename='addresses.json'):
    try:
        with open(filename, 'r') as file:
            addresses = json.load(file)
    except FileNotFoundError:
        addresses = []
    return addresses

# Fungsi untuk mengirim token
def send_tokens(sender_private_key, to_address, amount, nonce, gas_price, gas_limit):
    sender_address = Account.from_key(sender_private_key).address
    amount_wei = w3.to_wei(amount, 'ether')

    # Periksa saldo akun pengirim
    balance = w3.eth.get_balance(sender_address)
    total_cost = amount_wei + (gas_price * gas_limit)
    if balance < total_cost:
        raise ValueError(f'Saldo tidak cukup: saldo {balance}, biaya total {total_cost}')

    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': amount_wei,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': chain_id
    }

    signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash

# Main program
def main():
    print(Fore.MAGENTA + "===============================")
    print(Fore.CYAN + "Data Lake Auto Send")
    print(Fore.MAGENTA + "===============================")
    print(Fore.CYAN + "Channel : t.me/UGDAirdrop")
    print(Fore.MAGENTA + "===============================\n")

    sender_private_key = read_private_key('private_key.txt')
    sender_address = Account.from_key(sender_private_key).address

    # Menampilkan saldo pengirim dalam UNIT0
    balance_wei = w3.eth.get_balance(sender_address)
    balance_unit0 = w3.from_wei(balance_wei, 'ether')
    print(Fore.CYAN + f"Alamat: {sender_address}")
    print(Fore.CYAN + f"Saldo: {balance_unit0} mLAKE\n")

    input_address = input(Fore.YELLOW + "Masukkan alamat tujuan (atau tekan Enter untuk membuat alamat baru): ").strip()
    gas_price_gwei = 0.1
    gas_price = w3.to_wei(gas_price_gwei, 'gwei')
    gas_limit = 3000000
    delay = float(input(Fore.YELLOW + "Masukkan jeda waktu antar transaksi dalam detik: ").strip())

    total_transactions = 0

    if input_address == '':
        address_count = int(input(Fore.YELLOW + "Masukkan jumlah alamat baru yang ingin dibuat: ").strip())
        addresses = create_new_addresses(address_count)
        save_addresses_to_file(addresses)
        for address, private_key in addresses:
            print(Fore.GREEN + f'Generated Address: {address}, Private Key: {private_key}')
        # Membaca alamat dari file dan mengirim token secara otomatis
        addresses = read_addresses_from_file()
        amount = float(input(Fore.YELLOW + "Masukkan jumlah token yang akan dikirim ke setiap alamat: ").replace(',', '.'))
        nonce = w3.eth.get_transaction_count(sender_address)
        for address in addresses:
            while True:
                try:
                    tx_hash = send_tokens(sender_private_key, address[0], amount, nonce, gas_price, gas_limit)
                    print(Fore.GREEN + f'Transaksi berhasil dikirim ke {address[0]} dengan hash: {tx_hash.hex()}')
                    total_transactions += 1
                    nonce += 1
                    break
                except ValueError as e:
                    print(Fore.RED + f'Error sending to {address[0]}: {e}')
                    if 'Nonce too low' in str(e) or 'Known transaction' in str(e):
                        nonce = w3.eth.get_transaction_count(sender_address)
                    else:
                        break
                except Exception as e:
                    print(Fore.RED + f'Transaksi gagal untuk {address[0]}: {e}')
                    break
            time.sleep(delay)
    else:
        addresses = [(input_address, None)]
        save_addresses_to_file(addresses)
        amount = float(input(Fore.YELLOW + "Masukkan jumlah token yang akan dikirim: ").replace(',', '.'))
        nonce = w3.eth.get_transaction_count(sender_address)
        while True:
            try:
                tx_hash = send_tokens(sender_private_key, input_address, amount, nonce, gas_price, gas_limit)
                print(Fore.GREEN + f'Transaksi berhasil dikirim ke {input_address} dengan hash: {tx_hash.hex()}')
                total_transactions += 1
                break
            except ValueError as e:
                print(Fore.RED + f'Error: {e}')
                if 'Nonce too low' in str(e) or 'Known transaction' in str(e):
                    nonce = w3.eth.get_transaction_count(sender_address)
                else:
                    break
            except Exception as e:
                print(Fore.RED + f'Transaksi gagal: {e}')
                break

    print(Fore.MAGENTA + "\n===============================")
    print(Fore.YELLOW + "Pengiriman selesai!")
    print(Fore.CYAN + f"Total transaksi berhasil: {total_transactions}")
    print(Fore.CYAN + "Terima kasih telah menggunakan script ini.")
    print(Fore.CYAN + "Channel : t.me/UGDAirdrop")
    print(Fore.MAGENTA + "===============================")

if __name__ == '__main__':
    main()
