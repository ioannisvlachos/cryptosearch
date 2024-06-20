from datetime import datetime
import requests
from maltego_trx.entities import BTCAddress, BTCCluster, Exchange, Phrase
from maltego_trx.transform import DiscoverableTransform
from apis.return_api import return_ArkhamAPI, return_WalletExplorerAPI

arkham_api = return_ArkhamAPI()
walexp_api = return_WalletExplorerAPI()

class ToOutboundAddress(DiscoverableTransform):
    """
    Lookup the name associated with a phone number.
    """

    @classmethod
    def create_entities(cls, request, response):
        req_address = request.Value
        try:
            data = cls.returnData(req_address)
            if data:
                if len(data['label']) != 0:
                    for label in data['label']:
                        exchange_ = response.addEntity(Exchange, label)
                        exchange_.setLinkColor('0xB63115')
                        exchange_.setLinkThickness(5) 
                response.addEntity(BTCCluster, data['cluster_id'])
                if len(data['data']) == 0:
                    response.addEntity(Phrase, 'unspent')
                for item in data['data']:
                    txid = item['txid']
                    for address in item['outbound_addresses']:
                        if len(data['label']) != 0:
                            btc_address_entity = response.addEntity(BTCAddress, address['address'])
                            btc_address_entity.setLinkLabel(txid)
                            btc_address_entity.setLinkColor('0x0080FF')
                            btc_address_entity.setValue('Hot Wallet')
                            btc_address_entity.setBookmark('0xFF0000')
                            # btc_address_entity.setNote(f"Timestamp: {item['timestamp']}\nAmount: {address['amount']}\nThis is a Hot Wallet!")  
                        else:
                            btc_address_entity = response.addEntity(BTCAddress, address['address'])
                            btc_address_entity.setLinkLabel(txid)   
                            btc_address_entity.setNote(f"Timestamp: {item['timestamp']}\nAmount: {address['amount']}") 
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
        label = ToOutboundAddress.returnLabel(cluster_id, btc_address)
        num_trans = js['txs_count']
        outbound_txids = [x['txid'] for x in js['txs'] if x['used_as_output'] == False]
        result = [ToOutboundAddress.reqTxid(tx) for tx in outbound_txids]
        return {'cluster_id':cluster_id, 'num_trans':num_trans, 'label':label, 'data':result}



    @staticmethod
    def returnLabel(cluster_id, btc_address):
        out_list = []
        # walletexplorer req
        r1 = requests.get('https://www.walletexplorer.com/api/1/wallet-addresses?wallet=' + cluster_id + '&from=0&count=100&caller=' + walexp_api)
        if 'label' in r1.json().keys():
            out_list.append(r1.json()['label'])
        r1_ = requests.get('https://www.walletexplorer.com/api/1/wallet-addresses?wallet=' + cluster_id + '&from=0&count=100&caller=' + walexp_api)
        # arkham intelligence req
        r2 = requests.get('https://api.arkhamintelligence.com/intelligence/address/' + btc_address + '?chain=bitcoin', headers = arkham_api)
        if 'arkhamEntity' in r2.json().keys():
            out_list.append(r2.json()['arkhamEntity']['name'])
        if 'arkhamLabel' in r2.json().keys():
            out_list.append(r2.json()['arkhamLabel']['name'])
            
        return out_list
 

    @staticmethod
    def reqTxid(txid):
        r = requests.get('https://www.walletexplorer.com/api/1/tx?txid='+ txid + '&caller=' + walexp_api)
        js = r.json()
        timestamp = datetime.fromtimestamp(js['time']).strftime('%Y-%m-%d %H:%M:%S')
        data = [{'address':x['address'], 'amount':x['amount'], 'cluster_id':x['wallet_id']} for x in js['out']]
        return {'txid':txid, 'timestamp':timestamp, 'outbound_addresses':data}

if __name__ == "__main__":
    print(ToOutboundAddress.returnData("1CAahWcHEznFcZRUjyHoaFCer1pcaPDHFK"))
