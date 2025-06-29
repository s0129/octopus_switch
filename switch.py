from datetime import date, timedelta
import config
import argparse
from queries import token_query,account_query,replace_agreement_query,gql_query

AGILE_TARIFF = "AGILE-24-10-01"
GO_TARIFF = "GO-VAR-22-10-14"

mpan=None
current_tariff=None
auth_token=None

def get_auth_token():
    if not config.API_KEY:
        raise Exception("No API key provided")   
    query = token_query.format(api_key=config.API_KEY)
    result = gql_query(query)
    token = result.get("obtainKrakenToken", {}).get("token")
    if not token:
        raise Exception("No authentication token")    
    return token

def get_account_details():
    global mpan,current_tariff
    
    if not config.ACC_NUMBER:
        raise Exception("No account number provided")  
    query = account_query.format(acc_number=config.ACC_NUMBER)
    result = gql_query(query,auth_token)
    for agreement in result['account']['electricityAgreements']:
        if agreement['meterPoint']['direction']=="IMPORT":
            mpan=agreement['meterPoint']['mpan']
            current_tariff=agreement['tariff']['productCode']
            if not mpan:
                raise Exception("No mpan found")
            if not current_tariff:
                raise Exception("No current tariff found")
            return

def switch_tariff(target_product_code):
    if current_tariff==target_product_code:
        print(f"Error: Already on {target_product_code} tariff. Exiting.")
        exit()
    change_date = date.today() + timedelta(days=1)
    print(f"Switching from {current_tariff} to {target_product_code} on {change_date}")
    user_input = input("Continue? (Y/N)")
    if user_input.lower() not in ["yes", "y"]:
        exit()
    query = replace_agreement_query.format(account_number=config.ACC_NUMBER, mpan=mpan, product_code=target_product_code, change_date=change_date)
    gql_query(query,auth_token)
    print("Success")

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Octopus tariff switch")
    parser.add_argument("--agile",action="store_true",help="Switch to Agile tariff")
    parser.add_argument("--go",action="store_true",help="Switch to Go tariff")
    args=parser.parse_args()

    auth_token=get_auth_token()
    get_account_details()

    if args.agile:
        switch_tariff(AGILE_TARIFF)
    elif args.go:
        switch_tariff(GO_TARIFF)
    else:
        print("No tariff specified")