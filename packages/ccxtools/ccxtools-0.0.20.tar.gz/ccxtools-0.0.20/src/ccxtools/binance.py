import ccxt
from ccxtools.exchange import CcxtExchange


class Binance(CcxtExchange):

    def __init__(self, who, market, config):
        super().__init__(market)

        if market == 'USDT':
            self.ccxt_inst = ccxt.binance({
                'apiKey': config(f'BINANCE_API_KEY{who}'),
                'secret': config(f'BINANCE_SECRET_KEY{who}'),
                'options': {'defaultType': 'future'}
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
                if contract['info']['contractType'] != 'PERPETUAL' or contract['info']['status'] != 'TRADING':
                    continue

                ticker = contract['base']
                for fil in contract['info']['filters']:
                    if fil['filterType'] == 'LOT_SIZE':
                        size = float(fil['stepSize'])

                sizes[ticker] = size

            return sizes
