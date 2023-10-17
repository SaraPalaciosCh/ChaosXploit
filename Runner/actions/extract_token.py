import requests
import json

def get_token():  
    r = requests.put('http://169.254.169.254/latest/api/token', headers={'X-aws-ec2-metadata-token-ttl-seconds':'21600'})  

    token = r.text
    r2 = requests.get("http://169.254.169.254/latest/meta-data/iam/security-credentials/iamfullaccess", headers={"X-aws-ec2-metadata-token":token})
    sol = r2.json()
    with open('AccessKeys.json', 'w') as f:
        json.dump(sol, f)

    return sol
get_token()