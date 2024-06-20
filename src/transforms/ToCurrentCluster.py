import requests
from maltego_trx.entities import BTCCluster
from maltego_trx.transform import DiscoverableTransform
from apis.return_api import return_ArkhamAPI, return_WalletExplorerAPI

arkham_api = return_ArkhamAPI()
walexp_api = return_WalletExplorerAPI()

class ToCurrentCluster(DiscoverableTransform):
    """
    Lookup the name associated with a phone number.
    """

    @classmethod
    def create_entities(cls, request, response):
        req_address = request.Value
        try:
            data = cls.returnData(req_address)
            if data:
                response.addEntity(BTCCluster, data['cluster_id'])
            else:
                response.addUIMessage("No data")
        except Exception as e:
            response.addUIMessage(f"An error occurred: {str(e)}", messageType="PartialError")

    @staticmethod
    def returnData(btc_address):
        # req btc address, returns txids
        r = requests.get('https://www.walletexplorer.com/api/1/address?address=' + btc_address + '&from=0&count=100&caller=' + walexp_api)
        js = r.json()
        cluster_id = js['wallet_id']
        return {'cluster_id':cluster_id}

if __name__ == "__main__":
    print(ToCurrentCluster.returnData("1CAahWcHEznFcZRUjyHoaFCer1pcaPDHFK"))
