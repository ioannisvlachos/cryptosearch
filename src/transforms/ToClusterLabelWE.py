import requests
from maltego_trx.entities import Exchange
from maltego_trx.transform import DiscoverableTransform
from apis.return_api import return_ArkhamAPI, return_WalletExplorerAPI

arkham_api = return_ArkhamAPI()
walexp_api = return_WalletExplorerAPI()

class ToClusterLabelWE(DiscoverableTransform):
    """
    Lookup the name associated with a phone number.
    """

    @classmethod
    def create_entities(cls, request, response):
        req_cluster = request.Value
        try:
            data = cls.returnLabel(req_cluster)
            if data:
                response.addEntity(Exchange, data)
            else:
                response.addUIMessage("No data")
        except Exception as e:
            response.addUIMessage(f"An error occurred: {str(e)}", messageType="PartialError")

    @staticmethod
    def returnLabel(req_cluster):
        r = requests.get(f'https://www.walletexplorer.com/api/1/wallet?wallet={req_cluster}&from=0&count=100&caller={walexp_api}')
        if 'label' in r.json():
            return r.json()['label']
        

if __name__ == "__main__":
    print(ToClusterLabelWE.returnLabel("00000e7158503ed8"))
