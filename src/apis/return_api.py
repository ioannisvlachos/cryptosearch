import json

def load_config():
    with open('config.json') as js:
        return json.load(js)

def return_ArkhamAPI():
	conf = load_config()['api']
	return {'API-Key':conf['arkham-api']}

def return_WalletExplorerAPI():
	conf = load_config()['api']
	return conf['walletexplorer-api']

