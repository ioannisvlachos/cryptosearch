from maltego_trx.entities import Website
from maltego_trx.transform import DiscoverableTransform

class ToAddressesOfCluster(DiscoverableTransform):
    """
    Lookup the name associated with a phone number.
    """

    @classmethod
    def create_entities(cls, request, response):
        req_cluster = request.Value
        try:
            response.addEntity(Website, f'http://walletexplorer.com/wallet/{req_cluster}/addresses')
        except Exception as e:
            response.addUIMessage(f"An error occurred: {str(e)}", messageType="PartialError")

