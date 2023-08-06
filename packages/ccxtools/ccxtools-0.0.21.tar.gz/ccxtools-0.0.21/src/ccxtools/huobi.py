import ccxt
from ccxtools.exchange import CcxtExchange


class Huobi(CcxtExchange):

    def __init__(self, who, market, config):
        super().__init__(market)

        if market == 'USDT':
            self.ccxt_inst = ccxt.huobi({
                'apiKey': config(f'HUOBI_API_KEY{who}'),
                'secret': config(f'HUOBI_SECRET_KEY{who}'),
                'options': {
                    'defaultType': 'swap',
                    'defaultSubType': 'linear'
                }
            })

    def get_contract_sizes(self):
        """
        :return: {
            'BTC': 0.1,
            'ETH': 0.01,
            ...
        }
        """
        if self.market == 'USDT':
            contracts = self.ccxt_inst.fetch_markets()

            sizes = {}
            for contract in contracts:
                if contract['info']['contract_status'] != '1':
                    continue

                ticker = contract['base']
                size = float(contract['info']['contract_size'])

                sizes[ticker] = size

            return sizes

    def get_balance(self, ticker):
        """
        :param ticker: <String> Ticker name. ex) 'USDT', 'BTC'
        :return: <Int> Balance amount
        """
        response = self.ccxt_inst.contractPrivatePostLinearSwapApiV1SwapCrossAccountPositionInfo(
            params={'margin_account': 'USDT'})
        return float(response['data']['margin_balance'])
