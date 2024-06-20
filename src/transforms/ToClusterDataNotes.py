from datetime import datetime
import requests
from maltego_trx.entities import BTCCluster
from maltego_trx.transform import DiscoverableTransform
from apis.return_api import return_ArkhamAPI, return_WalletExplorerAPI

arkham_api = return_ArkhamAPI()
walexp_api = return_WalletExplorerAPI()


class ToClusterDataNotes(DiscoverableTransform):
    """
    Lookup the name associated with a phone number.
    """

    @classmethod
    def create_entities(cls, request, response):
        req_cluster = request.Value
        try:
            data = cls.returnOutboundCluster(req_cluster)
            if data:
                if data['out_amount'] != 'out of range':
                    cluster = response.addEntity(BTCCluster, req_cluster)
                    cluster.setNote(f"Number of addresses: {data['num_adds']}\nAmount Transacted: {data['out_amount']}\nFirst Tx: {data['first_transaction']}\nLast Tx: {data['last_transaction']}\nIncoming txids: {data['inc_tx']}\nOutgoing txids: {data['out_tx']}\nTxids Number: {data['num_txs']}")
                else:
                    cluster = response.addEntity(BTCCluster, req_cluster)
                    cluster.setNote(f"Number of addresses: {data['num_adds']}\nAmount Transacted: {data['out_amount']}\nFirst Tx: {data['first_transaction']}\nLast Tx: {data['last_transaction']}\nIncoming txids: {data['inc_tx']}\nOutgoing txids: {data['out_tx']}\nTxids Number: {data['num_txs']}")
                    cluster.setLinkColor('0x0080FF')
            else:
                response.addUIMessage("No data")
        except Exception as e:
            response.addUIMessage(f"An error occurred: {str(e)}", messageType="PartialError")


    @staticmethod
    def getNumberOfAddresses(req_cluster):
        url = f'https://www.walletexplorer.com/api/1/wallet-addresses?wallet={req_cluster}&from=0&count=100&caller={walexp_api}'
        r = requests.get(url)
        num_adds = r.json()['addresses_count']
        return int(num_adds)

    @staticmethod
    def returnOutboundCluster(req_cluster):
        tx_counter = 1
        out_cluster = []
        num_txs = 0
        inc_tx = 0
        out_tx = 0
        out_amount = 0.0
        in_amount = 0.0
        data = []
        num_adds = ToClusterDataNotes.getNumberOfAddresses(req_cluster)
        r = requests.get(f'https://www.walletexplorer.com/api/1/wallet?wallet={req_cluster}&from=0&count=100&caller={walexp_api}')
        txs_count = r.json()['txs_count']
        last_transaction = r.json()['txs'][0]['time']
        num_txs = r.json()['txs_count']
        if int(txs_count/100) > 10:
            last_pagn = int(txs_count/100)*100
            r = requests.get(f'https://www.walletexplorer.com/api/1/wallet?wallet={req_cluster}&from={last_pagn}&count=100&caller={walexp_api}')
            first_transaction = r.json()['txs'][len(r.json()['txs'])-1]['time']
            inc_tx = out_tx = out_amount = 'out of range'
            return {'num_txs':num_txs, 'inc_tx':inc_tx, 'out_tx':out_tx, 'num_adds':num_adds,
                'first_transaction':datetime.fromtimestamp(first_transaction).strftime('%Y-%m-%d %H:%M:%S'),
                'last_transaction':datetime.fromtimestamp(last_transaction).strftime('%Y-%m-%d %H:%M:%S'), 'out_amount':out_amount}
        else:
            for i in range(0, txs_count, 100):
                r = requests.get(f'https://www.walletexplorer.com/api/1/wallet?wallet={req_cluster}&from={i}&count=100&caller={walexp_api}')
                if i == int(txs_count/100)*100:
                    first_transaction = r.json()['txs'][len(r.json()['txs'])-1]['time']                
                for item in r.json()['txs']:   
                    if item['type']=='sent':
                        out_tx += 1
                        for output in item['outputs']:
                            out_amount += output['amount']
                    if item['type']=='received':
                        inc_tx += 1
                        in_amount += item['amount']
            return {'num_txs':num_txs, 'inc_tx':inc_tx, 'out_tx':out_tx, 'num_adds':num_adds,
                'first_transaction':datetime.fromtimestamp(first_transaction).strftime('%Y-%m-%d %H:%M:%S'),
                'last_transaction':datetime.fromtimestamp(last_transaction).strftime('%Y-%m-%d %H:%M:%S'), 'out_amount':out_amount}           
                     
        return data




if __name__ == "__main__":
    print(ToClusterDataNotes.returnOutboundCluster("00032a2488db48a1"))
