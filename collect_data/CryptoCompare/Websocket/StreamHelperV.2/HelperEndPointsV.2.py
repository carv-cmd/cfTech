class SubsList:
    by_subs = {
            "SubsByPair": "https://min-api.cryptocompare.com/data/v2/subs",
            "SubsWatchlist": "https://min-api.cryptocompare.com/data/subsWatchlist",
            "genCoinInfo": "https://min-api.cryptocompare.com/data/coin/generalinfo"
    }
    
    def __init__(self, endpoint, tsym='USD', fsyms='BTC'):
        self.url = self.by_subs[endpoint]
        self.parameters = dict(tsym=tsym, fsyms=fsyms)
    
    def set_url(self, change_url):
        self.url = self.by_subs[change_url]