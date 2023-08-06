import requests
from Base import Base

class rpcAggregation(Base):

    def get_token_balance(self, user, token, network, rpc_url=None):
        url = self.url + "tokenBalance"
        headers = { 'X-API-KEY': self.key }
        data = {
            "network": network,
            "user": user,
            "token": token,
            "rpc_url": rpc_url
        }
        response = requests.get(url, json=data, headers=headers)
        return response.json()

    def get_token_balances_for_user(self, user, tokens : list, network, rpc_url=None):
        url = self.url + "tokenBalancesForUser"
        headers = { 'X-API-KEY': self.key }
        data = {
            "network": network,
            "user": user,
            "tokens": tokens,
            "rpc_url": rpc_url
        }
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    
    def get_token_balance_for_users(self, users : list, token, network, rpc_url=None):
        url = self.url + "tokenBalanceForUsers"
        headers = { 'X-API-KEY': self.key }
        data = {
            "network": network,
            "users": users,
            "token": token,
            "rpc_url": rpc_url
        }
        response = requests.post(url, json=data, headers=headers)
        return response.json()

    def calculate_token_price_from_pair(self, pool, network, rpc_url=None):
        url = self.url + "calculateTokenPriceFromPair"
        headers = { 'X-API-KEY': self.key }
        data = {
            "network": network,
            "lp_token": pool,
            "rpc_url": rpc_url
        }
        response = requests.get(url, json=data, headers=headers)
        return response.json()
    
    def calculate_reserves_amount_from_pair(self, pool, amount, network, rpc_url=None):
        url = self.url + "calculateReservesAmountsFromPair"
        headers = { 'X-API-KEY': self.key }
        data = {
            "network": network,
            "lp_token": pool,
            "amount": amount,
            "rpc_url": rpc_url
        }
        response = requests.get(url, json=data, headers=headers)
        return response.json()
    
    def get_reserves_from_pair(self, pool, network, rpc_url=None):
        url = self.url + "getReservesFromPair"
        headers = { 'X-API-KEY': self.key }
        data = {
            "network": network,
            "lp_token": pool,
            "rpc_url": rpc_url
        }
        response = requests.get(url, json=data, headers=headers)
        return response.json()





