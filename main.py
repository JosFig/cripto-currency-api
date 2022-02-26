import keys as ke
from requests import get
from matplotlib import pyplot as plt
from datetime import datetime
import time
from tabulate import tabulate

#MAIN MENU
def main_menu_options():
    print("\n[1] List of top 100 Cripto Currencies")
    print("[2] List of Top Cripto Exchanges")
    print("[3] Ethereum Scan Address w Graph")
    print("[4] Cripto Currency Details by Name")
    print("[5] Cripto Currency Price History Graph by Name")
    print("[0] Exit\n")

#ETHSCAN
def eth_url_make_api(module, action, address, **kwargs):
    #Def to make full url depending on parameters
    url_eth = ke.ethscan_dict['URL_BASE_ETH'] + f"?module={module}&action={action}&address={address}&apikey={ke.ethscan_dict['api_key']}"

    for key, value in kwargs.items():
        url_eth += f"&{key}={value}"
    return url_eth

def eth_get_account_balace(address):
    balance_url_eth = eth_url_make_api("account", "balance", address, tag="latest")
    balance_response = get(balance_url_eth)
    balance_json = balance_response.json()
    eth_amount = int(balance_json['result']) / ke.ethscan_dict['VALUE_ETH']
    return eth_amount

def eth_get_currentprice():
    # Get Ether Last Price
    currentprice_url_eth = eth_url_make_api("stats", "ethprice", "")
    currentprice_response = get(currentprice_url_eth)
    currentprice_json = currentprice_response.json()

    currentprice_eth = currentprice_json['result']['ethusd']
    currentprice_ethtobtc = currentprice_json['result']['ethbtc']
    print(f"Current ETH price: {currentprice_eth}$ / {currentprice_ethtobtc} BTC")

    return float(currentprice_eth)

def eth_get_current_supply():
    # Get Total Supply of Ether 2
    current_supply_url_eth = eth_url_make_api("stats", "ethsupply", "")
    current_supply_response = get(current_supply_url_eth)
    current_supply_json = current_supply_response.json()
    current_supply = int(current_supply_json['result']) / ke.ethscan_dict['VALUE_ETH']

    print(f"Current ETH Supply: {current_supply} ETH")
    return current_supply

def eth_get_transactions(address):
    transactions_url_eth = eth_url_make_api("account", "txlist", address, startblock=0, endblock=99999999,
                                                page=1, offset=10000, sort="asc")
    transactions_response = get(transactions_url_eth)
    transactions_json = transactions_response.json()["result"]

    internal_tx_url = eth_url_make_api("account", "txlistinternal", address, startblock=0, endblock=99999999,
                                                page=1, offset=10000, sort="asc")
    internal_response = get(internal_tx_url)
    internal_json = internal_response.json()["result"]

    if 'Error! Invalid address format' in internal_json:
        print('Invalid address format')
    else:
        transactions_json.extend(internal_json)
        transactions_json.sort(key=lambda x: int(x['timeStamp']))

        current_balance = 0
        balances = []
        times = []
        list_to = []
        list_from = []
        list_value = []
        list_all = []

        for tx in transactions_json:
            to = tx["to"]
            from_address = tx["from"]
            value = int(tx["value"]) / ke.ethscan_dict['VALUE_ETH']

            list_all.append(to)
            list_all.append(from_address)
            list_all.append(value)

            list_to.append(str(to))
            list_from.append(str(from_address))
            list_value.append(value)

            if "gasPrice" in tx:
                gas = int(tx["gasUsed"]) * int(tx["gasPrice"]) / ke.ethscan_dict['VALUE_ETH']
            else:
                gas = gas = int(tx["gasUsed"]) / ke.ethscan_dict['VALUE_ETH']

            time = datetime.fromtimestamp(int(tx["timeStamp"]))
            money_in = to.lower() == address.lower()

            if money_in:
                current_balance += value
            else:
                current_balance -= value + gas
            balances.append(current_balance)
            times.append(time)

        # initializing N
        N = 10
        # using list slicing Get last N elements from list
        last_10_to = list_to[-N:]
        last_10_from = list_from[-N:]
        last_10_values = list_value[-N:]

        results_formated = [[last_10_from, last_10_to, str(last_10_values)]]
        list_all.append(results_formated)

        current_balance_dollars = float(current_balance) * float(eth_get_currentprice())
        current_balance_dollars = round(current_balance_dollars, 4)
        current_balance = round(current_balance, 4)
        print(f"Current ETH Balance in address: {current_balance:,} ETH / {current_balance_dollars:,}$")

        plt.plot(times, balances)
        # Graph Displaying labels
        plt.xlabel('Date')
        plt.ylabel('ETH')

        # Graph Displaying the title
        plt.title(label=f"Account Balance", fontsize=20, color='blue')
        plt.show()

#END ETHSCAN API / BEGINNING OF COIN CAP API

def url_make_api_coinlist(module, **kwargs):
    url_coinlist = ke.cryptocompare_dict['URL_BASE_COINCAP'] + module
    for key, value in kwargs.items():
        url_coinlist += f"/{value}"
    return url_coinlist

def coincap_list():
    coinlist_url = url_make_api_coinlist("assets")
    coinlist_response = get(coinlist_url)
    coinlist_json = coinlist_response.json()

    list_coincapcoins = []
    for info in coinlist_json['data']:
        id = info['id']
        rank = info['rank']
        name = info['id']
        symbol = info['symbol']
        supply = info['supply']
        maxsupply =  info['maxSupply']
        marketcapusd = info['marketCapUsd']
        volumeusd24h = info['volumeUsd24Hr']
        currentprice = info['priceUsd']
        change24h = info['changePercent24Hr']
        explorer = info['explorer']

        result_formatedcoinlist = [rank, name, symbol, supply, maxsupply, marketcapusd, volumeusd24h, currentprice, change24h]
        list_coincapcoins.append(result_formatedcoinlist)
    print(tabulate(list_coincapcoins,headers=["Rank", "Name", "Symbol", "Supply", "Max Supply","Market Cap$", "Volume 24h",
                                              "Current Price", "Change 24h %"], numalign="right", floatfmt=".2f"))

    return list_coincapcoins

def coincap_symbol(input_coin):
    coinsymbol_url = url_make_api_coinlist("assets", id=input_coin)
    coinsymbol_response = get(coinsymbol_url)
    coinsymbol_json = coinsymbol_response.json()

    if 'error' in coinsymbol_json:
        error = coinsymbol_json['error']
        timestamp = int(coinsymbol_json['timestamp'])  / 1000
        timestamp =  datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{error} at {timestamp}")

    else:
        id = coinsymbol_json['data']['id']
        rank = coinsymbol_json['data']['rank']
        name = coinsymbol_json['data']['id']
        symbol = coinsymbol_json['data']['symbol']
        supply = coinsymbol_json['data']['supply']
        maxsupply = coinsymbol_json['data']['maxSupply']
        marketcapusd = coinsymbol_json['data']['marketCapUsd']
        volumeusd24h = coinsymbol_json['data']['volumeUsd24Hr']
        currentprice = coinsymbol_json['data']['priceUsd']
        change24h = coinsymbol_json['data']['changePercent24Hr']
        explorer = coinsymbol_json['data']['explorer']

        result_formated_symbol = [[rank, name, symbol, supply, maxsupply, marketcapusd, volumeusd24h, currentprice,
                                   change24h]]
        print(tabulate(result_formated_symbol, headers=["Rank", "Name", "Symbol", "Supply", "Max Supply", "Market Cap$",
                       "Volume 24h", "Current Price", "Change 24h %"], numalign="right", floatfmt=".2f"))
        print("\n")
        return result_formated_symbol

def coincap_exchanges():
    exchanges_url = url_make_api_coinlist("exchanges")
    exchanges_response = get(exchanges_url)
    exchanges_json = exchanges_response.json()

    list_exchange = []

    for info in exchanges_json['data']:
        rank = info['rank']
        name = info['name']
        perctotalvolume = info['percentTotalVolume']
        volusd = info['volumeUsd']
        pairs = info['tradingPairs']
        excurl = info['exchangeUrl']
        time = int(info["updated"])/ 1000
        time = datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M')

        result_formated_exchanges = [rank, name, perctotalvolume, volusd, pairs, excurl, time]
        list_exchange.append(result_formated_exchanges)

    print("\n Top Exchanges")
    print(tabulate(list_exchange, headers=["Rank", "Name", "TotalVol%", "Vol$", "#Pairs", "Url", "Updated"],
                   numalign="right", floatfmt=".2f"))

    return list_exchange

def coincap_symbolhist(coin, interval):
    #GET HISTORIC VALUES FOR A INTERVAL
    symbolhist_url = url_make_api_coinlist("assets", id=coin, url=f"history?interval={interval}")
    symbolhist_response = get(symbolhist_url)
    symbolhist_json = symbolhist_response.json()

    #Check if error in reply
    if 'error' in symbolhist_json:
        error = symbolhist_json['error']
        timestamp = int(symbolhist_json['timestamp'])  / 1000
        timestamp =  datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{error} at {timestamp}. Please try again")

    #Check if not empty in reply
    elif not symbolhist_json['data']:
        timestamp = int(symbolhist_json['timestamp']) / 1000
        timestamp = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n {coin.capitalize()} Not found at {timestamp}. Please try again")
    else:
        #SORT JSON BY DATE
        symbolhist_price_list = []
        symbolhist_date_list = []

        for hist in symbolhist_json['data']:
            price = float(hist['priceUsd'])
            #RESULT TIME RETURNED IN MILISECONDS WHICH DIVIDED BY 1000 CONVERTS TO SECONDS
            time = int(hist['time']) / 1000

            #LIMIT RESULT TO 2 DECIMAL PLACES
            price = round(price,2)

            #CONVERT DATE TO YEAR-MONTH-DAY
            time = datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d')

            #APPEND RESULTS TO LISTS FOR GRAPH LATER
            symbolhist_price_list.append(price)
            symbolhist_date_list.append(time)

        #GRAPH
        plt.plot(symbolhist_date_list, symbolhist_price_list, color='green')
        #Graph Displaying labels
        plt.xlabel('Date')
        plt.ylabel('USD')
        #Graph Displaying the title
        plt.title(label=f"{coin.capitalize()}", fontsize=20, color='blue')
        plt.show()

# END COIN CAP API / BEGINING OF MAIN

class MainApp():
    inputsearch = ""
    print("Welcome. \nPlease choose one of the options using the number ID:")
    while inputsearch != "end" or inputsearch != "exit" or inputsearch != "quit":
        main_menu_options()
        input_option = input("Insert a number from the menu or end to exit the program: ").lower()
        if input_option == "end" or input_option == "exit" or input_option == "0":
            break
        elif (not input_option.isdigit()):
            print("\nPlease insert a valid number")
            continue
        elif input_option == "1":
            print("\n[1] List of Top 100 Cripto Currencies")
            coincap_list()
        elif input_option == "2":
            print("\n[2] List of Top 50 Cripto Exchanges")
            coincap_exchanges()
        elif input_option == "3":
            print("\n[3] Ethereum Scan Address with Graph")
            input_address = input("Please insert ethereum address:")
            eth_get_transactions(input_address)
        elif input_option == "4":
            print("\n[4] Cripto Currency Details by Name")
            input_coin = input("Please insert a coin name:")
            coincap_symbol(input_coin)
        elif input_option == "5":
            print("\n[5] Cripto Currency Price History Graph by Name\n")
            #Intervals available in API
            list_coinsymbol_interval = ["m1", "m5", "m15", "m30", "h1", "h2", "h6", "h12", "d1"]
            coinsymbol = input("Insert a coin name:")
            print("\nIntervals available: "
                                        "\n min (m) - m1, m5, m15, m30, "
                                        "\n hour(h) - h1, h2, h6, h12, "
                                        "\n day (d) - d1\n")
            coinsymbol_interval = input("Insert an interval: ")

            if coinsymbol_interval not in list_coinsymbol_interval:
                print(f"{coinsymbol_interval} Interval not in range. \n Try again and insert an interval "
                      f"- m1, m5, m15, m30, h1, h2, h6, h12, d1")
                continue
            else:
                coincap_symbolhist(coinsymbol, coinsymbol_interval)

if __name__ == "__main__":
    MainApp().run() #Call the function to run
