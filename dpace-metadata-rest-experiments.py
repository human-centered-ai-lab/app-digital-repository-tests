import json, requests
import string
from restnavigator import Navigator

class MetadataFields:
    def __init__(self, api_entry_point, header):
        self.aep    = api_entry_point
        self.h      = header

    def  getSchemas (self):
        pass

    def  getMetadataFieldsForSchema (self, schema):
        metadatafields = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/metadatafields/search/bySchema?schema=' + schema +'&page=' + str(page)
            r = requests.get(url, headers = h)
            halrespone = json.loads(r.content)
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']
            if  '_embedded' in halrespone.keys(): 
                mdfs = halrespone['_embedded']['metadatafields']
                for mdf in halrespone['_embedded']['metadatafields']:
                    del mdf ["_links"]
                    del mdf ["_embedded"]
                    metadatafields.append (mdf)
            page = page + 1
            if (page  >= totalPages):
                stillPagesToRead = False
        return metadatafields

r = requests.post('http://dspace-rest.silicolab.bibbox.org/server/api/authn/login?user=v@bibbox.org&password=vendetta') 
bearer_token = r.headers['Authorization']

h = {'Authorization':r.headers['Authorization']}

mf =  MetadataFields ('http://dspace-rest.silicolab.bibbox.org/server/api/', h)

mf.getSchemas()
metadatafields = mf.getMetadataFieldsForSchema('slide')
schema = 'dc'
metadatafields = mf.getMetadataFieldsForSchema(schema)

for mf in metadatafields:
    infostring = schema + '.' + mf['element']
    if ( type (mf['qualifier']) == str):
        infostring = infostring + '.'+ mf['qualifier']
    if ( type (mf['scopeNote']) == str):
        scopeNote = mf['scopeNote'].replace('\n', '')
        infostring = infostring + ',   ' + scopeNote

    print (infostring)

