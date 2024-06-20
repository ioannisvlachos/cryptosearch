import requests
from maltego_trx.entities import BTCCluster
from maltego_trx.transform import DiscoverableTransform
from apis.return_api import return_ArkhamAPI, return_WalletExplorerAPI

arkham_api = return_ArkhamAPI()
walexp_api = return_WalletExplorerAPI()

class ToOutboundClustersWE(DiscoverableTransform):
    """
    Lookup the name associated with a phone number.
    """ 

    @classmethod
    def create_entities(cls, request, response):
        req_cluster = request.Value
        try:
            data = cls.returnOutboundCluster(req_cluster)
            if data:
                for item in data:
                    for cluster in item['outputs']:
                        response.addEntity(BTCCluster, cluster['wallet_id'])
            else:
                response.addUIMessage("No data")
        except Exception as e:
            response.addUIMessage(f"An error occurred: {str(e)}", messageType="PartialError")

    @staticmethod
    def returnOutboundCluster(req_cluster):
        tx_counter = 1
        out_cluster = []
        r = requests.get(f'https://www.walletexplorer.com/api/1/wallet?wallet={req_cluster}&from=0&count=100&caller={walexp_api}')
        txs_count = r.json()['txs_count']
        if txs_count > 1000:
            txs_count = 1000
        for i in range(0, txs_count, 100):
            r = requests.get(f'https://www.walletexplorer.com/api/1/wallet?wallet={req_cluster}&from={i}&count=100&caller={walexp_api}')
            for item in r.json()['txs']:
                if item['type']=='sent':
                    out_cluster.append({'tx':tx_counter, 'time':item['time'], 'outputs':item['outputs']})
                    tx_counter += 1
        return out_cluster


if __name__ == "__main__":
    print(ToOutboundClustersWE.returnOutboundCluster("e15826db9536d59b"))
