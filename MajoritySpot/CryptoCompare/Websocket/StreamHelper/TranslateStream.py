from HelperEndPoints import *


if __name__ == "__main__":
    print(f">>> 'TranslateStream' initializing as '{__name__}'")

    sysAdmin = TopsREST()
    try:
        # d = telesto()
        # degeneracy = json.dumps(d(limit=100))
        degeneracy = sysAdmin.top_percent_change(limit=100)
        degeneracy.decode('utf-8')

        mb = len(degeneracy) / 1000000

        print(f"\nMAX byte count for BSON document is (160,000,000bytes) or (16MB)!"
              f"\n\tCurrent BSON Representation Byte Count: {len(degeneracy)}"
              f"\n\t\tApprox Document Size:\n\t\t\t({mb}MB / 16MB)")
        
        print('\nData Set:\n')

        pprint(degeneracy)
        
    except TypeError or AttributeError or UnicodeError:
        print('degeneracy is not a UTF-8. Fix ur shit')
        raise
    
    # fuckHead = TopsREST()
    #
    # print(f"\n{TopsREST.__mro__}\n"
    #       f"\ndir('ConfigureRESTapi'):\n{dir('ConfigureRESTapi')}\n"
    #       f"\n{fuckHead.__dict__}\n")
    
else:
    print(f">>> 'TranslateStream' initializing as '{__name__}'")
