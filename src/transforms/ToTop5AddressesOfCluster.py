from datetime import datetime
import requests
from maltego_trx.entities import BTCAddress
from maltego_trx.transform import DiscoverableTransform
from apis.return_api import return_ArkhamAPI, return_WalletExplorerAPI

arkham_api = return_ArkhamAPI()
walexp_api = return_WalletExplorerAPI()

class ToTop5AddressesOfCluster(DiscoverableTransform):
    """
    Lookup the name associated with a phone number.
    """

    @classmethod
    def create_entities(cls, request, response):
        req_cluster = request.Value
        try:
            data = cls.returnAddresses(req_cluster)
            if data:
                for address in data:
                    btc_address = response.addEntity(BTCAddress, address['address'])
                    # btc_address.setNote(f"Balance: {address['balance']}\nIncoming txs: {address['incoming_txs']}")
            else:
                response.addUIMessage("No data")
        except Exception as e:
            response.addUIMessage(f"An error occurred: {str(e)}", messageType="PartialError")


    @staticmethod
    def returnAddresses(req_cluster):
        data = []
        r = requests.get(f'https://www.walletexplorer.com/api/1/wallet-addresses?wallet={req_cluster}&from=0&count=100&caller={walexp_api}')
        if r.json()['addresses_count'] > 6:
            for i in range(5):
                data.append(r.json()['addresses'][i])
            return data
        else:
            for address in r.json()['addresses']:
                data.append(address)
            return data                


if __name__ == "__main__":
    print(ToTop5AddressesOfCluster.returnAddresses("00032a2488db48a1"))
