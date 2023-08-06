import base64
import hmac
import json
import requests
import urllib
import urllib.request
from urllib.parse import urljoin
from time import time
from ccxtools.exchange import Exchange
from ccxtools.tools import add_query_to_url


class Bingx(Exchange):
    BASE_URL = 'https://api-swap-rest.bingbon.pro/api/v1'

    def __init__(self, who, market, config):
        super().__init__(market)
        self.API_KEY = config(f'BINGX_API_KEY{who}')
        self.SECRET_KEY = config(f'BINGX_SECRET_KEY{who}')

    def request_get(self, url):
        for i in range(10):
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()

    def request_post(self, url, params):
        for i in range(10):
            params['timestamp'] = int(time() * 1000)

            params_str = '&'.join([f'{x}={params[x]}' for x in sorted(params)])

            signature_msg = f'POST/api/v1{url}{params_str}'
            signature = hmac.new(self.SECRET_KEY.encode('utf-8'), signature_msg.encode('utf-8'), 'sha256').digest()

            params_str += '&sign=' + urllib.parse.quote(base64.b64encode(signature))

            request = urllib.request.Request(Bingx.BASE_URL + url, params_str.encode('utf-8'),
                                             {'User-Agent': 'Mozilla/5.0'})
            post = urllib.request.urlopen(request).read()

            json_response = json.loads(post.decode('utf-8'))

            if 'invalid timestamp' not in json_response['msg']:
                return json_response
            from pprint import pprint
            pprint(json_response)

    def get_contract_sizes(self):
        """
        :return: {
            'BTC': 0.1,
            'ETH': 0.01,
            ...
        }
        """
        contracts = self.get_contracts()['data']['contracts']

        sizes = {}
        for contract in contracts:
            ticker = contract['asset']
            size = float(contract['size'])

            sizes[ticker] = size

        return sizes

    def get_balance(self, ticker):
        """
        :param ticker: <String> ticker name. ex) 'USDT', 'BTC'
        :return: <Int> balance amount
        """
        params = {
            'apiKey': self.API_KEY,
            'currency': ticker
        }
        response = self.request_post('/user/getBalance', params)
        return response['data']['account']['equity']

    def get_contracts(self):
        """
        :return: {
            'code': <Int>,
            'data': {
                {
                    'contracts': [
                        {
                            'asset': 'BTC',
                            'contractId': '100',
                            'currency': 'USDT',
                            'feeRate': 0.0005,
                            'maxLongLeverage': 100,
                            'maxShortLeverage': 100,
                            'name': 'BTC',
                            'pricePrecision': 2,
                            'size': '0.0001',
                            'status': 1,
                            'symbol': 'BTC-USDT',
                            'tradeMinLimit': 1,
                            'volumePrecision': 4
                        },
                        {
                        },
                        ...
                    ]
                }
            },
            'msg': <String> ex) 'Success'
        }
        """
        url = Bingx.BASE_URL + '/market/getAllContracts'
        return self.request_get(url)

    def get_market_depth(self, ticker):
        """
        :param ticker: <String>
        :return: {
            'asks': [
                {
                    'p': 19153.3274,
                    'v': 8.3473
                },
                {
                    'p': 19153.341,
                    'v': 3.3524
                },
                ...
            ],
            'bids': [
                {
                    'p': 19152.6914,
                    'v': 38.871
                },
                {
                    'p': 19152.4835,
                    'v': 2.7036
                },
                ...
            ],
            'ts': '1656868209523'
        }
        """
        url = Bingx.BASE_URL + '/market/getMarketDepth'
        query = {'symbol': f'{ticker}-USDT'}
        return self.request_get(add_query_to_url(url, query))['data']

    def get_ticker(self):
        """
        :return: {
            'code': <Int>,
            'data': {
                {
                    'tickers': [
                        {
                            "symbol": "BTC-USDT",
                            "priceChange": "10.00",
                            "priceChangePercent": "10",
                            "lastPrice": "5738.23",
                            "lastVolume": "31.21",
                            "highPrice": "5938.23",
                            "lowPrice": "5238.23",
                            "volume": "23211231.13",
                            "dayVolume": "213124412412.47",
                            "openPrice": "5828.32"
                        },
                        {
                        },
                        ...
                    ]
                }
            },
            'msg': <String>
        }
        """
        url = Bingx.BASE_URL + '/market/getTicker'
        return self.request_get(url)
