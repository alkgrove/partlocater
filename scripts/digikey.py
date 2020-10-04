import requests
import traceback
from configReader import *
from datetime import datetime
from urllib.parse import quote

###############################
###    Digikey Parts API    ###
###############################

def digikey_get_part(part_id):
    # Get part information from source site given a specified part ID.
    # GET /Search/v3/Products/p5555-nd HTTP/1.1
    # Host: api.digikey.com
    # X-DIGIKEY-Client-Id: heWGx9w6DK8kZf3jRv5E9jXAhXrGBU67
    # Authorization: Bearer s4T5DbmFZadjNRAEbUnN9zkU3DBj
    # X-DIGIKEY-Locale-Site: US
    # X-DIGIKEY-Locale-Language: en
    # X-DIGIKEY-Locale-Currency: USD
    # X-DIGIKEY-Locale-ShipToCountry: us
    # X-DIGIKEY-Customer-Id: 0
    
    if Config().access_token_string is None:
        raise Exception("No Token Loaded")
    headers = {
        'accept': 'application/json',
        'authorization': 'Bearer ' + Config().access_token_string,
        'X-DIGIKEY-Client-Id': Config().client_id,
        'X-DIGIKEY-Locale-Site': Config().locale_site,
        'X-DIGIKEY-Locale-Language': Config().locale_language,
        'X-DIGIKEY-Locale-Currency': Config().locale_currency,
        'X-DIGIKEY-Locale-ShipToCountry': Config().locale_shiptocountry,
        'X-DIGIKEY-Customer-Id': Config().customer_id
    }
    url = 'https://api.digikey.com/Search/v3/Products/' + quote(part_id, safe='')
    Config().log_write("Query " + part_id + " with token " + Config().access_token_string)
    response = requests.get(url, headers=headers)
    Config().log_write("Response Code " + str(response.status_code))
    if response.status_code != 200:
        r = json.loads(response.text)
        if 'Details' in r:
            s = r['Details']
        elif 'moreInformation' in r:
            s = r['moreInformation']
        else:
            s = 'Unknown Response from Digi-Key'
        raise Exception(s)
    return response.text


def is_token_old(token):
    timestamp = token['timestamp']
    expires = token['expires_in']
    expire_timestamp = timestamp + timedelta(seconds=int(expires))
    if expire_timestamp < datetime.now():
        return True
    else:
        return False

def is_token_expired(token):
    timestamp = token['timestamp']
    expires = token['refresh_token_expires_in']
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
    response = requests.post('https://api.digikey.com/v1/oauth2/token', headers=headers, data=data)
    
    if response.status_code != 200:
        Config().log_write("Data: %s Response: %s" % (data, response))
        raise Exception("Bad status code returned from digikey while updating token: "+str(response.status_code))
    return json.loads(response.text)

def translate_part_json(data):
    if data is None:
        return None, None, None, None
    data = json.loads(data)
    exclude = Config().exclude
    include = Config().include
    parameter = Config().parameter
    library = Config().library
    libref = Config().libref
    dst = dict()
    hidden = dict()
    indirect_form = re.compile(r"\='([\w\s]+)'")
    try:
        table_name = library[data['LimitedTaxonomy']['Children'][0]['Value']]
    except KeyError:
        table_name = data['LimitedTaxonomy']['Children'][0]['Value']

    try:
        dst[parameter['StandardPricing']] = ", ".join(str(i['BreakQuantity'])+"="+str(i['UnitPrice'])
                                                      for i in (data['StandardPricing']))
        dst[parameter['Category']] = data['LimitedTaxonomy']['Children'][0]['Value']
        dst[parameter['RohsInfo']] = data['RoHSStatus']
        for e in data['Parameters']:
            try:
                dst[parameter[e['Parameter']]] = e['Value']
            except KeyError:
                dst[e['Parameter']] = e['Value']

        # Exceptions
        dst[parameter['PrimaryDatasheet']] = data['PrimaryDatasheet']
        dst[parameter['ManufacturerPartNumber']] = data['ManufacturerPartNumber']
        dst[parameter['DigiKeyPartNumber']] = data['DigiKeyPartNumber']
        dst[parameter['ProductDescription']] = data['ProductDescription']
        dst[parameter['ManufacturerName']] = data['Manufacturer']['Value']
        dst[parameter['QuantityOnHand']] = data['QuantityAvailable']
        dst["Supplier 1"] = "Digi-Key"
        alt_package = {}
        for item in data['AlternatePackaging']:
            min_quantity = item['MinimumOrderQuantity']
            packaging = item['Packaging']['Value']
            spn = item['DigiKeyPartNumber']
            if 'Digi-Reel' in packaging:
                dst[parameter['CustomPackaging']] = spn
            elif min_quantity > 1:
                alt_package[spn + " " + packaging + " (" + str(min_quantity) + ")"] = spn
        hidden['MinimumOrderQuantity'] = data['MinimumOrderQuantity']
        hidden['Packaging'] = data['Packaging']['Value']
        if len(alt_package) > 0:
            dst[parameter['VolumePackaging']] = alt_package[[*alt_package.keys()][0]]
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
            indirect_match = re.match(indirect_form, ref)
            if indirect_match is not None:
                dst["Library Ref"] = dst[indirect_match.group(1)]
            else:
                dst["Library Ref"] = ref
        dst["Base Part Number"] = data['ManufacturerPartNumber']
        for ex in exclude:
            if ex in dst.keys():
                del dst[ex]
        for incl in include:
            dst[incl] = include[incl]
    except KeyError as e:
        raise Exception("Failed to load all part fields."+str(e))
    return dst, table_name, alt_package, hidden
