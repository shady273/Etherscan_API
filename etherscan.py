class GetResult:
    def __init__(self, address: str, api_key: str):
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

    def get_abi(self, contract_address: str):
        get_abi_url = self.BASE_URL + f'?module=contract&action=getabi' \
                                      f'&address={contract_address}&sort=asc&apikey={self.api_key}'
        response = self.get(get_abi_url)
        data = response.json()
        result = data['result']
        if 'tokenURI' not in result:
            return None
        else:
            return result

    def get_image(self, contract_address: str, token_id: int, provider_url: str):
        import check_URL
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider(provider_url))
        get_abi = GetResult(contract_address, self.api_key)
        abi = get_abi.get_abi(contract_address)

        if abi is None:
            return None
        else:
            check_address = Web3.toChecksumAddress(contract_address)
            contract_instance = w3.eth.contract(address=check_address, abi=abi)
            token_url = contract_instance.functions.tokenURI(token_id).call()

            try:
                url = check_URL.check_url(token_url)
                get_url = self.get(url)
                json_data = get_url.json()
                image_url = json_data['image']
                if image_url[:4] == 'ipfs':
                    good_url = ('https://ipfs.io/ipfs/' + image_url[7:])
                    return good_url
                return json_data['image']
            except Exception:
                url = check_URL.check_url(token_url)
                return url

    def get_erc721_balance(self, provider_url: str):
        get_erc721_url = self.BASE_URL + f'?module={self.module}&action=tokennfttx' \
                                         f'&address={self.address}&sort=asc&apikey={self.api_key}'
        response = self.get(get_erc721_url)
        data = response.json()
        result = data['result']
        in_list = list()
        out_list = list()
        for token in result:
            if token['to'] == self.address.lower():
                in_list.append(token)
            else:
                out_list.append(token)

        out_id = [out_id['tokenID'] for out_id in out_list]

        balance_erc721 = [x for x in in_list if x['tokenID'] not in out_id]
        thisdict = dict()
        for i in balance_erc721:
            get_image = GetResult.get_image(self, i['contractAddress'], int(i['tokenID']), provider_url)
            token_name = i['tokenName']
            token_id = i['tokenID']
            thisdict[f'{token_name} - {token_id}'] = get_image
        return thisdict

