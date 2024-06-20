from datetime import datetime
import requests
from maltego_trx.entities import StartTime, StopTime, IncomingTRX, OutgoingTRX, Transactions, BitcoinAmount, BTCAddressCount, Website
from maltego_trx.transform import DiscoverableTransform
from apis.return_api import return_ArkhamAPI, return_WalletExplorerAPI

arkham_api = return_ArkhamAPI()
walexp_api = return_WalletExplorerAPI()


class ToClusterDataAsEntities(DiscoverableTransform):
    """
    Lookup the name associated with a phone number.
    """

    @classmethod
    def create_entities(cls, request, response):
        req_cluster = request.Value
        try:
            data = cls.returnOutboundCluster(req_cluster)
            if data:
                f_trx = response.addEntity(StartTime, data['first_transaction'])
                f_trx.setLinkLabel('First transaction time')
                l_trx = response.addEntity(StopTime, data['last_transaction'])
                l_trx.setLinkLabel('Last transaction')
                num_txs = response.addEntity(Transactions, data['num_txs'])
                num_txs.setLinkLabel('Number of transactions time')
                inc_txs = response.addEntity(IncomingTRX, data['inc_tx'])
                inc_txs.setLinkLabel('Incoming transactions')
                out_txs = response.addEntity(OutgoingTRX, data['out_tx'])
                out_txs.setLinkLabel('Outgoing transactions')
                out_amount = response.addEntity(BitcoinAmount, data['out_amount'])
                out_amount.setLinkLabel('Amount')
                num_adds = response.addEntity(BTCAddressCount, data['num_adds'])
                num_adds.setLinkLabel('Number of addresses in cluster')
                response.addEntity(Website, f'http://walletexplorer.com/wallet/{req_cluster}/addresses')
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
        num_adds = ToClusterDataAsEntities.getNumberOfAddresses(req_cluster)
        r = requests.get(f'https://www.walletexplorer.com/api/1/wallet?wallet={req_cluster}&from=0&count=100&caller={walexp_api}')
        txs_count = r.json()['txs_count']
        last_transaction = r.json()['txs'][0]['time']
        num_txs = r.json()['txs_count']
        if int(txs_count/100) > 10:
            last_pagn = int(txs_count/100)*100
            r = requests.get(f'https://www.walletexplorer.com/api/1/wallet?wallet={req_cluster}&from={last_pagn}&count=100&caller={walexp_api}')
            first_transaction = r.json()['txs'][len(r.json()['txs'])-1]['time']
            inc_tx = out_tx = 'out of range'
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
                        out_amount += item['balance']
                    if item['type']=='received':
                        inc_tx += 1
                        in_amount += item['balance']
            return {'num_txs':num_txs, 'inc_tx':inc_tx, 'out_tx':out_tx, 'num_adds':num_adds,
                'first_transaction':datetime.fromtimestamp(first_transaction).strftime('%Y-%m-%d %H:%M:%S'),
                'last_transaction':datetime.fromtimestamp(last_transaction).strftime('%Y-%m-%d %H:%M:%S'), 'out_amount':out_amount}           
                     
        return data




if __name__ == "__main__":
    print(ToClusterDataAsEntities.returnOutboundCluster("00032a2488db48a1"))
