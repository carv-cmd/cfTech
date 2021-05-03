# Generates Stream Parameter Dictionary:
# Formatting: {'action'=action, 'subs'=['subListElem1', 'subListElem2', ...]}
# TODO make string formatter for the subListElement auto completion from REST API's

class CallingFor(object):
    def __init__(self):
        self.subs = list()
        self.action = 'SubAdd'
    
    
class Parameters(CallingFor):
    def __init__(self):
        super().__init__()
        self.parameters = dict()
        
    def parametrics(self):
        self.parameters = dict(action=self.action, subs=self.subs)

    def subscriber(self, subs, sub_flag=True):
        self.subs = subs
        if sub_flag:
            self.action = 'SubAdd'
        else:
            self.action = "SubRemove"
        self.parametrics()
    
    def __repr__(self):
        return f'{self.parameters}'

        
cc = Parameters()

subbing = ['0~Coinbase~BTC~USD', '5~CCCAGG~BTC~USD', '8~Binance~BTC~USDT']
cc.subscriber(subbing)
print(f'\nSubscribe Stream:\n\n\t{cc}')

unsub = ['0~Coinbase~BTC~USD']
cc.subscriber(unsub, sub_flag=False)
print(f'\nUnsubscribe Stream:\n\n\t{cc}')

