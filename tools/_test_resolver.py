from tools.ticker_resolver import resolve_ticker, validate_ticker
from tools.nse_universe import search_company

examples = ['HDFC Bank','HDFC','TCS','Infosys','Reliance','Airtel','Bharti Airtel','Tata Motors']
print('search_company samples:')
for ex in examples:
    print(ex, '->', search_company(ex))

print('\nresolve_ticker samples:')
for ex in examples:
    try:
        print(ex, '->', resolve_ticker(ex))
    except Exception as e:
        print(ex, 'ERROR', e)

print('\nvalidate examples:')
for t in ['TCS.NS','HDFCBANK.NS','FAKE.NS']:
    print(t, '->', validate_ticker(t))
