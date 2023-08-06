import ccxt
from ccxtools.exchange import CcxtExchange


class Ftx(CcxtExchange):

    def __init__(self, who, market, config):
        super().__init__(market)

        self.ccxt_inst = ccxt.ftx({
            'apiKey': config(f'FTX_API_KEY{who}'),
            'secret': config(f'FTX_SECRET_KEY{who}')
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
            contracts = self.ccxt_inst.publicGetFutures()['result']

            sizes = {}
            for contract in contracts:
                if not contract['perpetual'] or not contract['enabled']:
                    continue

                ticker = contract['underlying']
                size = float(contract['sizeIncrement'])

                sizes[ticker] = size

            return sizes
