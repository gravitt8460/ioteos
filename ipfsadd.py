
from pyeos_client.NodeosConnect import RequestHandlerAPI
from pyeos_client.EOSWalletApi import WalletAPI
from pyeos_client.EOSChainApi import ChainAPI
import datetime
import ipfsapi

import ctypes
import hashlib
from ctypes import *

import base58
import pkg_resources

# from eosiopy.exception import CantFindRecId, CantFindResInPack
# from eosiopy.exception import IllegalKey


def get_res_path(name):
    for i in pkg_resources.resource_listdir(__name__, "../"):
        if i.find(name) >= 0:
            return i


def get_private_ket_by_wif(wif):
    eos_byte_array = bytearray(base58.b58decode(wif))
    if eos_byte_array[0] != 0x80:
        raise IllegalKey()
    hex_bytea_array = eos_byte_array[1:33]
    return hex_bytea_array


def sign(wfi, trx):
    pri = get_private_ket_by_wif(wfi)
    sha = hashlib.sha256(trx)
    trx = sha.digest()
    pri = bytes(pri)
    ll = ctypes.cdll.LoadLibrary
    try:
        if get_res_path("uECC"):
            libuecc = pkg_resources.resource_filename(__name__, "../" + get_res_path("uECC.cpython"))
        else:
            raise CantFindResInPack
    except:
        libuecc = './uECC.so'

    libuecc = ll(libuecc)
    c_uint_array = c_uint8 * 64
    c_uint_array32 = c_uint8 * 32
    signature = c_uint_array(0)
    c_trx = c_uint_array32(0)
    c_pri = c_uint_array32(0)
    for i in range(32):
        c_trx[i] = trx[i]
        c_pri[i] = pri[i]

    recId = libuecc.uECC_sign_forbc(c_pri, c_trx, signature)
    if recId == -1:
        raise CantFindRecId
    print(recId)
    bin = bytearray()
    binlen = 65 + 4
    headerBytes = recId + 27 + 4
    bin.append(headerBytes)
    bin.extend(bytearray(signature))
    temp = bytearray()
    temp.extend(bin[0:65])
    temp.append(75)
    temp.append(49)
    rmd160 = hashlib.new("rmd160")
    rmd160.update(temp)
    bin.extend(rmd160.digest())
    sig = str(base58.b58encode(bytes(bin)))[2:-1]
    sig = "SIG_K1_" + sig
    return sig



# api = ipfsapi.connect('34.193.139.251', 8989)
api = ipfsapi.connect('127.0.0.1', 5001)

res = api.add ('filetoadd')


filehash = res["Hash"]


print (res)
print (filehash)

res = api.cat (filehash)
print (res)

connection  = RequestHandlerAPI(base_url='http://localhost:8888', headers={"Accept": "application/json"})
chainapi = ChainAPI(connection)
print ("-------------------- Chain Info ------------------------------")
result = chainapi.get_info().json()
print (result)
print ("--------------------------------------------------------------")
print ("\n\n")

print ("-------------  Last Irreversible Block Number  -------------- ")
print (result["last_irreversible_block_num"])
print ("--------------------------------------------------------------")
print ("\n\n")

print("------------------  Block Info --------------------------------")
block_info = chainapi.get_block("{\"block_num_or_id\":" + str(result["last_irreversible_block_num"]) + "}").json()
print (block_info)
print ("Timestamp: " + block_info["timestamp"])
d1 = datetime.datetime.strptime(block_info["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
d2 = d1.replace(minute=d1.minute+1)
print ("Minute: " + str(d1.minute))
print ("d2: " + str(d2))

exp = str(d2)[0:10] + "T" + str(d2)[11:19]
print ("exp: " + exp)

print ("--------------------------------------------------------------")
print ("\n\n")

walletapi = WalletAPI(connection)
#print (walletapi.wallet_create(wallet_name='"default"').json())
print (walletapi.wallet_list().json())
print("------------------  Wallet Unlock & Import --------------------")
print (walletapi.wallet_unlock(wallet_name_password='["default","PW5JQ6S1824W2Zu44RpU9LqJuqgKcssTkrCuSU7R6sMhPWjNgd8EB"]').json())
print (walletapi.wallet_import_key(wallet_name_privKey='["default","5JhhMGNPsuU42XXjZ57FcDKvbb7KLrehN65tdTQFrH51uruZLHi"]').json())
print ("--------------------------------------------------------------")
print ("\n\n")


print("-------------------  JSON Action ------------------------------")
json_action = "{\"code\":\"gh\",\"action\":\"newscan\", \"args\":{\"_serial\":\"12345\",\"_sku\":\"CCZ-20oz\",\"_latlon\":\"New York, NY\",\"_imagehash\":\"" + filehash + "\"}}"
print (json_action)
print ("--------------------------------------------------------------")
print ("\n\n")

print("-------------------  Binary Action ----------------------------")
binary_act = chainapi.abi_json_to_bin(data=json_action).json()
print (binary_act)
print ("\n")
print (binary_act["binargs"])
print ("--------------------------------------------------------------")
print ("\n\n")


print ("-----------------  Transaction to Sign ----------------------" )
sign_trx = "[{\"ref_block_num\":" + str(result["last_irreversible_block_num"]) + ",\"ref_block_prefix\":" + \
        str(block_info["ref_block_prefix"]) + \
        ",\"expiration\":\"" + exp + "\",\"scope\":[\"gh\"],\"read_scope\":[],\"messages\":[{\"code\":\"gh\",\"type\":\"newscan\",\"authorization\":[{\"account\":\"gh\",\"permission\":\"active\"},{\"account\":\"gh\",\"permission\":\"active\"}],\"data\":\"" \
        + str(binary_act["binargs"]) + "\"}],\"signatures\":[]},[\"EOS7ckzf4BMgxjgNSYV22rtTXga8R9Z4XWVhYp8TBgnBi2cErJ2hn\"],\"\"]"

print (sign_trx)
print ("--------------------------------------------------------------")
print ("\n\n")


print ("----------------  Signed Transaction ------------------------" )
#signed_trx = walletapi.wallet_sign_trx(transaction_data=sign_trx)
wif = "5JhhMGNPsuU42XXjZ57FcDKvbb7KLrehN65tdTQFrH51uruZLHi"
signed_trx = sign(wif, sign_trx)
print (signed_trx.json())
signature = signed_trx.json()["signatures"][0]
print (signature)
print ("--------------------------------------------------------------")

print ("----------------  Pushing Transaction -------------------------" )
transaction =  "{\"compression\":\"none\",\"transaction\":{\"expiration\":\"" + exp + "\",\"ref_block_num\":" + str(result["last_irreversible_block_num"]) + ",\"ref_block_prefix\":" + \
                str(block_info["ref_block_prefix"]) + ",\" net_usage_words\": 0,\"max_cpu_usage_ms\": 0,\"delay_sec\": 0," + \
                "\"context_free_actions\": [],\"actions\": [{\"account\": \"gh\",\"name\":\"newscan\",\"authorization\": [{" + \
                "\"actor\": \"gh\",\"permission\": \"active\"},{\"actor\":\"gh\",\"permission\":\"active\"}],\"data\":\"" + str(binary_act["binargs"]) + "\"}],\"transaction_extensions\": []},\"signatures\":[\"" + str(signature) + "\"]}"

#transaction = "{\"compression\":\"none\",\"transaction\":\"" + str(binary_act["binargs"]) + "\",\"signatures\":\"" + str(signature) + "\"}"

#
# 
#transaction = "{\"compression\":\"none\",\"transaction\":{\"code\":\"pigeon\",\"\type\":\"createdel\",\"authorization\":[{\"account\":\"pigeon\",\"permission":"active"}" + \",\"signatures\":\"" + str(signature) + "\"}"
# transaction = "{\"compression\":\"none\",\"transaction\":{\"code\":\"pigeon\",\"action\":\"createdel\", \"args\":{\"deliverykey\":\"QmSqcJwsXMivki9q52qkYun3iXjPPvnLyv1jh9tfZdko7U\"}},\"signatures\":[\"" + str(signature) + "\"]}"

print (transaction)
print ("--------------------------------------------------------------")

print ("\n\n")


print ("----------------  Pushed Transaction -------------------------" )
pushed_trx = chainapi.push_transaction(transaction=transaction)
print (pushed_trx.json())
print ("--------------------------------------------------------------")

print ("\n\n")

