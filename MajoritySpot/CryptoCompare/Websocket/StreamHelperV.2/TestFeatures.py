from HelperStreamPoints import *


class Hfsp(dict):
    def __init__(self, metrics):
        super(Hfsp, self).__init__()
        self.metrics = metrics
        self.__sendto = None
        self.__response_data = None
    
    @property
    def sendto(self):
        """ This is the 'sendto' property w/ the requirements for request.get() """
        return self.__sendto
    
    @sendto.getter
    # def sendto(self):
    #     for elem in self.metrics:
    #         foo = TopLists(endpoint=elem, **kwargs)
    #         sendto[elem] = [foo['url'], foo['parameters']['requestData']]
    #
    #     # def sender(**kwargs):
    #     #     """
    #     #     TODO Docstring functionality
    #     #     """
    #     #     sendto = dict()
    #     #     for elem in self.metrics:
    #     #         foo = TopLists(endpoint=elem, **kwargs)
    #     #         sendto[elem] = [foo['url'], foo['parameters']['requestData']]
    #     #         print(f"\n>>> GENERATING METRICS FOR: {elem}. . .")
    #     #
    #     #     print(line)
    #     #     return response_object(**sendto)
    #     # return sender
        
    @sendto.setter
    def sendto(self, value):
        self.__sendto = value

    @sendto.deleter
    def sendto(self):
        del self.__sendto
        
    @staticmethod
    def response_wrapper(func):
        
        def response_object(**sendto):
            """
            TODO Docstring and mongo push
            TODO :MongoDB: dict(metric=report, data=requests.get(passing[0], params=passing[1]).json())
            """
            func()
            response_dict = dict()
            for report, passing in sendto.items():
                try:
                    report = report + datetime.now().isoformat()
                    daters = requests.get(passing[0], params=passing[1])
                    response_dict[report] = daters.json()
                
                    print(f'>>> Received Request Response:({report})]'
                          f'\n\tFrom: "{daters.url}"')
                
                    del response_dict[report]['SponsoredData']
                    time.sleep(.25)
            
                except requests.exceptions.ConnectionError:
                    print('CONNECTION REFUSED INCREASE DURATION BETWEEN SUBSEQUENT REQUESTS')
                    break
            return response_dict
        return response_object
    
    @staticmethod
    @response_wrapper
    def responder():
        print('\n>>> Executing .get() task. . .\n')

    # def __get__(self, instance, owner):
    #     return self.__dict__[instance]
    #
    # def __set__(self, instance, value):
    #     self.__dict__[instance] = value

    # def __getitem__(self, item):
    #     print(f">> CALLED: __getitem__({item})")
    #     return self.__dict__[item]
    #
    # def __setattr__(self, key, value):
    #     print(f">> CALLED: __setattr__({key}, {value})")
    #     super(Hfsp, self).__setattr__(key, value)
    #
    # def request_parameters(self):


'splitComment'
# def run_wrapper(func):
#     def execute(verify_items, **kwargs):
#         func()
#         if not Verified(verify_items):
#             print("\nVerify List Entries. . .")
#
#         else:
#             cc = HaveFunStayingPoor()
#             return cc.send_agent(**kwargs)  # returns full response
#
#     return execute


# @run_wrapper
# def execute_call():
#     print('>>> ATTEMPTING TO EXECUTE REQUEST.GET(). . .')


if __name__ == "__main__":
    print(f"\n>>> Initializing `ConfigureHelperV.2` as '{__name__}'...\n")
    my_list = ["TopPercentChange"]  # , "TopByPrice", "TopMktCap", "TopVolSubs", "TopDirectVol"]
    # my_list = ["TopByPrice", "TopMktCap", "TopVolSubs", "TopDirectVol"]
    # my_list = ["TopPerceange"]
    # executed = execute_call(my_list)
    # print(f'\n>>> Request-Response Date:\n'
    #       f'\n{json.dumps(executed, indent=4, sort_keys=True)}')
    
    keyWordArgs = {'limit': 10}
    
    dgm = ["TopPercentChange", "TopByPrice"]
    dg = Hfsp(dgm)
    
    print(dg.sendto)
    # dg.sendto = keyWordArgs
    # pprint(dg.sendto)
    
    # print(f'\n>>> Request Metrics: {dg.metrics} <<<'
    #       f'\n>>>  <<<'
    #       f'\n>>> Response Content Dict: {dg.response_content} <<<'
    #       f'\n>>> dg:\n{dg}\n <<<')
    #
    # print(f'\ndir(dg):\n{dir(dg)}\n')
    

else:
    print(f"\n>>> Initializing `ConfigureHelperV.2` as '{__name__}'...")
