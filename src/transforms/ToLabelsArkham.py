import requests
from maltego_trx.entities import Exchange
from maltego_trx.transform import DiscoverableTransform
from apis.return_api import return_ArkhamAPI, return_WalletExplorerAPI

arkham_api = return_ArkhamAPI()
walexp_api = return_WalletExplorerAPI()

class ToLabelsArkham(DiscoverableTransform):
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
    def returnLabel(btc_address):
        r2 = requests.get('https://api.arkhamintelligence.com/intelligence/address/' + btc_address + '?chain=bitcoin', headers = arkham_api)
        if 'arkhamEntity' in r2.json().keys():
            return r2.json()['arkhamEntity']['name']
        if 'arkhamLabel' in r2.json().keys():
            return r2.json()['arkhamLabel']['name']
        

if __name__ == "__main__":
    print(ToLabelsArkham.returnLabel("00000e7158503ed8"))
