import requests

URL = "https://api.octopus.energy/v1/graphql/"

token_query = """mutation {{
	obtainKrakenToken(input: {{ APIKey: "{api_key}" }}) {{
	    token
	}}
}}"""

replace_agreement_query = """mutation {{
  replaceAgreement(input: {{
    accountNumber: "{account_number}",
    mpxn: "{mpan}",    
    replaceOnDate: "{change_date}",
    newProductCode: "{product_code}",
  }})
  {{
    account {{
      number
    }}
  }}
}}"""

account_query = """query{{
    account(
        accountNumber: "{acc_number}"
    ) {{
    electricityAgreements(active: true) {{
        validFrom
        validTo
        meterPoint {{            
            mpan
            direction
        }}
        tariff {{
            ... on HalfHourlyTariff {{
                productCode
                }}
            }}
        }}
    }}
}}"""

def gql_query(query,auth_token=None):    
    payload = {
            "query": query,
            "variables": {}
        }
    
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json'
        }
    
    if auth_token:
        headers['Authorization']=auth_token
    
    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    if not response.ok:
        raise Exception(f"GQL query failed: {response.status_code}: {response.text}")
    result = response.json()

    if "errors" in result:
        raise Exception(f"GQL errors: {result['errors']}")
    return result.get("data", {})