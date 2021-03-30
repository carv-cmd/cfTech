from HelperEndPoints import *

# # <<SINGLE HELPER ENDPOINT CALL STRUCTURE>>
# susAdmin = TopsREST()
# top_change = {'Top_Volume': susAdmin.top_vol_subs(limit=10)}
# degeneracy = nested_printer(top_change)
# print(degeneracy)

# <<PASS DICTIONARY TO NESTED PRINTER TO PRINT JSON RESPONSE OBJECTS>>
# coiner = TopsREST()
# toppers = {'topPrices': coiner.top_by_price(limit=10),
#            'topVolumes': coiner.top_vol_subs(limit=10)}
# nested_printer(toppers)

# <<<CALLS MULTIPLE REQUESTS AND PRINTS MULTIPLE RESPONSES>> <<see telesto docstring>>>
coining = telesto()
coinWizard = coining(limit=50)
degeneracy = nested_printer(coinWizard)

for irx in degeneracy:
    print(f'\nGroup Sets: {irx}'
          f'\nValues:\n\t\t>>> {degeneracy[irx]}\n')
