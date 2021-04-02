# Decorators for ConfigureHelperV.2

def verification_wrapper(func):
    verified = ["TopPercentChange", "TopVolSubs", "TopMktCap", "TopByPrice", "TopDirectVol", "TopTierVolSubs"]
    
    def verifier(unverified):
        func()
        for checking in unverified:
            if checking not in verified:
                print(f"\n>>> INVALID INPUT: ['{checking}']")
                return False
            else:
                pass
        return True
    return verifier


@verification_wrapper
def user_entry():
    print('\n>>> CHECKING USER INPUTS BEFORE CALLING API. . .')


def print_wrapper(func):
    def printer(requested_data, coin_info='FullName', conversion_info='SubsNeeded'):
        func()
        degens = dict()
        for ik, iv in requested_data.items():
            returns_degen = []
            for metric in iv['Data']:
                returns_degen.append([metric['CoinInfo'][coin_info], metric['ConversionInfo'][conversion_info]])
            degens[ik] = returns_degen
        return degens
    return printer


@print_wrapper
def quick_print():
    print("\n>>> Generating a Quick Reference List <<<")
    

if __name__ == "__main__":
    needs_verification = ["TopPercentChange", "TopVolSubs", "TopMktCap", "TopByPrice"]
    
    if user_entry(needs_verification):
        print('\n>>> INPUT STRINGS VERIFIED CORRECT\n>>> Proceeding w/ requests.get(). . .')
    else:
        print('\n>>> Modify metrics list to satisfy entry requirements. . .')

else:
    Verifier = user_entry
    Printer = quick_print


# def to_bson(json_elem):
    #     bson_obj = bson.encode(json_elem)
    #     logs.info(f"\nAttempting Connection w/: {req_url}"
    #               f"\nMAX byte count for BSON document is (160,000,000bytes) or (16MB)!"
    #               f"\n\tCurrent BSON Representation Byte Count: ({len(bson_obj)}-rawBytes)"
    #               f"\n\t\tApprox Document Size:\n\t\t\t({len(bson_obj) / 1000000}MB / 16MB)\n"
    #               f"\n\n{bson_obj}\n\n")
    #     return bson_obj
