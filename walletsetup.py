import ipfsapi
from pyeos_client.NodeosConnect import RequestHandlerAPI
from pyeos_client.EOSWalletApi import WalletAPI
from pyeos_client.EOSChainApi import ChainAPI


connection  = RequestHandlerAPI(base_url='http://localhost:8888', headers={"Accept": "application/json"})


walletapi = WalletAPI(connection)
#print (walletapi.wallet_create(wallet_name='"default"').json())
#print (walletapi.wallet_list().json())