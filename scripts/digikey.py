import requests
import traceback
from configReader import *
from datetime import datetime

###############################
###    Digikey Parts API    ###
###############################


def digikey_get_part(part_id):
    # Get part information from source site given a specified part ID.
    if Config().access_token_string is None:
        raise Exception("No Token Loaded")
    headers = {
        'accept': 'application/json',
        'authorization': Config().access_token_string,
        'content-type': 'application/json',
        'x-digikey-customer-id': Config().customer_id,
        'x-digikey-locale-currency': 'USD',
        'x-digikey-locale-language': 'EN',
        'x-digikey-locale-shiptocountry': 'US',
        'x-digikey-locale-site': 'US',
        'x-ibm-client-id': Config().client_id
    }
    data = '{"Part":"' + part_id + '","IncludeAllAssociatedProducts":"false","IncludeAllForUseWithProducts":"false"}'
    Config().log_write("Query " + part_id + " with token " + Config().access_token_string)
    response = requests.post('https://api.digikey.com/services/partsearch/v2/partdetails', headers=headers, data=data)
    Config().log_write("Response Code " + str(response.status_code))

    if response.status_code != 200:
        r = json.loads(response.text)
        raise Exception(r['Details'])
    return response.text

def is_token_old(token):
    timestamp = token['timestamp']
    expires = token['expires_in']
    expire_timestamp = timestamp + timedelta(seconds=int(expires))
    if expire_timestamp < datetime.now():
        return True
    else:
        return False

def digikey_get_new_token(refresh_token):
    headers = {
        "content-type":"application/x-www-form-urlencoded",
    }
    data = {"refresh_token": refresh_token, "client_id": Config().client_id,
            "client_secret": Config().client_secret, "grant_type": "refresh_token"}
    response = requests.post('https://sso.digikey.com/as/token.oauth2', headers=headers, data=data)
    
    if response.status_code != 200:
        Config().log_write("Data: %s Response: %s" % (data, response))
        raise Exception("Bad status code returned from digikey while updating token: "+str(response.status_code))
    return json.loads(response.text)


def translate_part_json(data):
    data = json.loads(data)
    exclude = Config().exclude
    include = Config().include
    parameter = Config().parameter
    library = Config().library
    libref = Config().libref
    dst = dict()
    indirectForm = re.compile(r"\='([\w\s]+)'")

    try:
        table_name = library[data['PartDetails']['Category']['Text']]
    except KeyError:
        table_name = data['PartDetails']['Category']['Text']

    try:
        dst[parameter['StandardPricing']] = ", ".join(str(i['BreakQuantity'])+"="+str(i['UnitPrice'])
                                                      for i in (data['PartDetails']['StandardPricing']))
        dst[parameter['UnitPrice']] = str(data['PartDetails']['StandardPricing'][0]['UnitPrice'])
        dst[parameter['Category']] = data['PartDetails']['Category']['Text']
        dst[parameter['RohsInfo']] = data['PartDetails']['RohsInfo']
        for e in data['PartDetails']['Parameters']:
            try:
                dst[parameter[e['Parameter']]] = e['Value']
            except KeyError:
                dst[e['Parameter']] = e['Value']

        # Exceptions
        dst[parameter['PrimaryDatasheet']] = data['PartDetails']['PrimaryDatasheet']
        dst[parameter['ManufacturerPartNumber']] = data['PartDetails']['ManufacturerPartNumber']
        dst[parameter['DigiKeyPartNumber']] = data['PartDetails']['DigiKeyPartNumber']
        dst[parameter['ProductDescription']] = data['PartDetails']['ProductDescription']
        dst[parameter['ManufacturerName']] = data['PartDetails']['ManufacturerName']['Text']
        dst[parameter['QuantityOnHand']] = data['PartDetails']['QuantityOnHand']
        dst["Supplier 1"] = "Digi-Key"
        if 'Supplier Device Package' in dst:
            dst["Footprint Ref"] = dst['Supplier Device Package']
        elif 'Package / Case' in dst:
           dst["Footprint Ref"] = dst['Package / Case']
        else:
            dst["Footprint Ref"] = "*"
        cat = dst['Category']
        if cat not in libref:
            dst["Library Ref"] = ""
        else:
            ref = libref[cat]   
            indirectMatch = re.match(indirectForm, ref)
            if indirectMatch is not None:
                dst["Library Ref"] = dst[indirectMatch.group(1)]
            else:
                dst["Library Ref"] = ref
        dst["Base Part Number"] = data['PartDetails']['ManufacturerPartNumber']
        for ex in exclude:
            if ex in dst.keys():
                del dst[ex]
        for incl in include:
            dst[incl] = include[incl]
    except KeyError as e:
        raise Exception("Failed to load all part fields."+str(e))
    return dst, table_name
