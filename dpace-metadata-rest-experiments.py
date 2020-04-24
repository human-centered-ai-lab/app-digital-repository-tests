import json, requests
import string
from restnavigator import Navigator

class MetadataFields:
    def __init__(self, api_entry_point, header):
        self.aep    = api_entry_point
        self.h      = header

    def  schemas (self):
        metadataschemas = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/metadataschemas?page=' + str(page)
            r = requests.get(url, headers = h)
            halrespone = json.loads(r.content)
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']
            if  '_embedded' in halrespone.keys(): 
                for mds in halrespone['_embedded']['metadataschemas']:
                    del mds ["_links"]
                    metadataschemas.append (mds)
            page = page + 1
            if (page  >= totalPages):
                stillPagesToRead = False
        return metadataschemas

    def metadataFieldsForSchema (self, schema):
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
                for mdf in halrespone['_embedded']['metadatafields']:
                    del mdf ["_links"]
                    del mdf ["_embedded"]
                    metadatafields.append (mdf)
            page = page + 1
            if (page  >= totalPages):
                stillPagesToRead = False
        return metadatafields

    def printMetadataFields (self, schema, metadatafields):
        i = 1
        for mf in metadatafields:
            infostring = str(i) + ':  ' + schema + '.' + mf['element']
            if ( type (mf['qualifier']) == str):
                if len (mf['qualifier'])  > 0:
                    infostring = infostring + '.'+ mf['qualifier']
            if ( type (mf['scopeNote']) == str):
                scopeNote = mf['scopeNote'].replace('\n', '')
                infostring = infostring + ',   ' + scopeNote

            print (infostring)
            i = i+1
    

r = requests.post('http://dspace-rest.silicolab.bibbox.org/server/api/authn/login?user=v@bibbox.org&password=vendetta') 
bearer_token = r.headers['Authorization']

h = {'Authorization':r.headers['Authorization']}

mf =  MetadataFields ('http://dspace-rest.silicolab.bibbox.org/server/api/', h)

schemas = mf.schemas()
print(json.dumps(schemas, indent=4, sort_keys=True))

for s in schemas:
    prefix = s['prefix']
    metadatafields = mf.metadataFieldsForSchema(prefix)
    print ('=================== ' + prefix + ' ='+ '='*(25-len(prefix)) + ' ' + str(len(metadatafields)))
    mf.printMetadataFields (prefix, metadatafields)


#schema = 'slide'
#metadatafields = mf.metadataFieldsForSchema(schema)
#mf.printMetadataFields (schema, metadatafields)
#print(json.dumps(metadatafields, indent=4, sort_keys=True))

