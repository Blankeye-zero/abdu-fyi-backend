 # def update_godaddy_nameservers(self, domain, nameservers):
    #     gd_prod_key = "XXXX"
    #     gd_prod_secret = "XXXXX"
    #     godaddy_key = "XXXX"
    #     godaddy_secret = "XXXXX"
    #     gd_url = f'https://api.godaddy.com/v1/domains/{domain}/records'

    #     headers = {
    #         'Authorization': f'sso-key {gd_prod_key}:{gd_prod_secret}',
    #         'Content-Type': 'application/json'
    #     }

    #     data = [
    #         {
    #             "type": "NS",
    #             "name": "@",
    #             "data": ns,
    #             "ttl": 3600
    #         } for ns in nameservers
    #     ]

    #     response = requests.put(
    #         gd_url, headers=headers, data=json.dumps(data),)

    #     if response.status_code == 200:
    #         CfnOutput(self, id="domain name server change", key="result",
    #                   value=f"Successfully updated nameservers for {domain}")
    #     else:
    #         CfnOutput(self, id="domain name server change", key="result",
    #                   value=f"Failed to update nameservers: {response.content}")