class BalanceERC20:
    def __init__(self, address, api_key):
        from requests import get
        import collections
        self.address = address
        self.api_key = api_key
        self.module = 'account'
        self.BASE_URL = 'https://api.etherscan.io/api'
        self.get = get
        self.collections = collections

    def get_eth_balance(self):
        get_eth_url = self.BASE_URL + f'?module={self.module}&action=balance' \
                                      f'&address={self.address}&apikey={self.api_key}'
        response = self.get(get_eth_url)
        data = response.json()
        return int(data['result']) / 10 ** 18

    def get_erc20_balance(self):
        get_erc20_url = self.BASE_URL + f'?module={self.module}&action=tokentx' \
                                        f'&address={self.address}&sort=asc&apikey={self.api_key}'
        response = self.get(get_erc20_url)
        data = response.json()
        result = data['result']
        in_list = list()
        out_list = list()
        for token in result:
            if token['to'] == self.address.lower():
                in_list.append(token)
            else:
                out_list.append(token)

        list_in_value = list()
        for i in in_list:
            symbol_dict = dict()
            decimal = 10 ** int(i.get('tokenDecimal'))
            symbol = i.get('tokenSymbol')
            value = float(i.get('value')) / decimal
            symbol_dict[symbol] = value
            list_in_value.append(symbol_dict)

        counter_in = self.collections.Counter()
        for d in list_in_value:
            counter_in.update(d)

        list_out_value = list()
        for i in out_list:
            symbol_dict = dict()
            decimal = 10 ** int(i.get('tokenDecimal'))
            symbol = i.get('tokenSymbol')
            value = float(i.get('value'))
            symbol_dict[symbol] = value / decimal
            list_out_value.append(symbol_dict)

        counter_out = self.collections.Counter()
        for d in list_out_value:
            counter_out.update(d)
        balance_erc20 = dict(counter_in - counter_out)
        return balance_erc20


a = BalanceERC20('0x7547A453486E359eb5A3Ee797281b409c964Ab81', '6CAG7PSD917C2EEY7MFC1JPEMJN551SQWQ')
print(a.get_erc20_balance())