from os import listdir
from os.path import isfile, join, splitext
import json, requests
import string

class MetadataFields:
    '''
    Object handling Metadata creation slots and
    '''
    def __init__(self, api_entry_point, header):

        self.aep = api_entry_point
        self.h = header

    def schemas (self):
        # example = {
        #     "id": 1,
        #     "namespace": "http://dublincore.org/documents/dcmi-terms/",
        #     "prefix": "dc",
        #     "type": "metadataschema"
        # }

        metadataschemas = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/metadataschemas?page=' + str(page)
            r = requests.get(url, headers=h)
            halrespone = json.loads(r.content)
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']

            if '_embedded' in halrespone.keys():
                for mds in halrespone['_embedded']['metadataschemas']:
                    del mds["_links"]
                    metadataschemas.append (mds)
            page = page + 1
            if (page  >= totalPages):
                stillPagesToRead = False
        return metadataschemas

    def schemaID (self, prefix):
        schemas = self.schemas()

        lookuptable = {}

        id = -1
        for s in schemas:
            if prefix == s['prefix']: 
                id = s['id']
#        print (id)
        return id

    def deleteSchema (self, prefix):
        id = self.schemaID(prefix)
        status = -1
        if id > 0:
            url = self.aep + 'core/metadataschemas/' + str(id)  
            r = requests.delete(url, headers=h)
            status = r.status_code
        return (status)

    def createSchema (self, prefix, namespace):
        url = self.aep + 'core/metadataschemas'          
        r = requests.post(url, headers=h, json={"prefix": prefix, "namespace": namespace, "type": "metadataschema"})
        return (r.status_code)

    def metadataFieldsForSchema (self, schema):

        # example = {
        #     "id": 434,
        #     "element": "quality",
        #     "qualifier": None,
        #     "scopeNote": "Q of the p slide",
        #     "type": "metadatafield"
        # }

        metadatafields = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/metadatafields/search/bySchema?schema=' + schema +'&page=' + str(page)
            r = requests.get(url, headers=h)
            halrespone = json.loads(r.content)
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']
            if '_embedded' in halrespone.keys():
                for mdf in halrespone['_embedded']['metadatafields']:
                    del mdf["_links"]
                    del mdf["_embedded"]
                    metadatafields.append (mdf)
            page = page + 1
            if page  >= totalPages:
                stillPagesToRead = False
        return metadatafields
    
    def createMetadataField (self, prefix, mdf):
        id = self.schemaID(prefix)
        status = -1
        if id > 0:
            url = self.aep + 'core/metadatafields?schemaId=' + str(id)  
            r = requests.post(url, headers=h, json=mdf)
            status = r.status_code
        return (status)

    def deleteMetadataField (self, id):
        url = self.aep + 'core/metadatafields/' + str(id)  
        r = requests.delete(url, headers=h)
        status = r.status_code
        return (status)

    def printMetadataFields (self, prefix, metadatafields):
        i = 1
        for mf in metadatafields:
            infostring = str(i) + ':' + prefix + '.' + mf['element']
            if (type(mf['qualifier']) == str):
                if len (mf['qualifier']) > 0:
                    infostring = infostring + '.' + mf['qualifier']
            if (type(mf['scopeNote']) == str):
                scopeNote = mf['scopeNote'].replace('\n', '')
                infostring = infostring + ',' + scopeNote

            print (infostring)
            i = i+1
    
    def itemsInScope (self, scope):

        # example = {
        #     "discoverable": True,
        #     "handle": "123456789/504",
        #     "id": "728afa5e-b330-4030-8007-eb14174dbd0e",
        #     "inArchive": True,
        #     "lastModified": "2020-04-27T12:17:29.339+0000",
        #     "metadata": {}
        # }

        items = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'discover/search/objects?scope=' + scope +'&page=' + str(page)
            r = requests.get(url, headers = h)
            halrespone = json.loads(r.content)
            totalPages = 1
            #print(json.dumps(halrespone,  indent=4, sort_keys=True))
            if '_embedded' in halrespone.keys():
                totalPages = halrespone ['_embedded']['searchResult']['page']['totalPages']
                pageNumber = halrespone ['_embedded']['searchResult']['page']['number']
                for objects in halrespone['_embedded']['searchResult']['_embedded']['objects']:
                        io = objects['_embedded']['indexableObject']
                        del io["_links"]
                        #del io ["_embedded"]
                        items.append (io)
                page = page + 1
                if (page  >= totalPages):
                    stillPagesToRead = False
        return items


    def deleteItem (self, item_uiid):
        url = self.aep + 'core/items/' + item_uiid
        r = requests.delete(url, headers=h)
        print(url, " DELETED ", r.status_code)


#865f143a-cb9e-43cb-8a0d-9237df935ce0

runningEnv = 'localhost'

if runningEnv == 'silicolab':
    params = {'user': 'v@bibbox.org', 'password': 'vendetta'}
    serverurlprefix  = 'http://dspace-rest.silicolab.bibbox.org'
if runningEnv == 'dspace':
    params = {'user': 'dspacedemo+admin@gmail.com', 'password':'dspace'}
    serverurlprefix = 'https://dspace7.4science.cloud'
if runningEnv == 'localhost':
    params = {'user': 'test@test.edu', 'password':'admin'}
    serverurlprefix = 'http://localhost:8080'

r = requests.post(serverurlprefix + '/server/api/authn/login', params=params)
h = {'Authorization': r.headers['Authorization']}

# object definition metadata object

mf = MetadataFields(serverurlprefix + '/server/api/', h)


#schemas = mf.schemas()
#print(json.dumps(schemas, indent=4, sort_keys=True))

#for s in schemas:
#    prefix = s['prefix']
#    metadatafields = mf.metadataFieldsForSchema(prefix)
#    print ('=================== ' + prefix + ' ='+ '='*(25-len(prefix)) + ' ' + str(len(metadatafields)))
#    mf.printMetadataFields (prefix, metadatafields)

schema = 'wsi'
metadatafields = mf.metadataFieldsForSchema(schema)
print(json.dumps(metadatafields, indent=4, sort_keys=True))
input()

scanOfSlide = {
            "element": "isScanOfSlide",
            "qualifier": None,
            "scopeNote": "",
            "type": "metadatafield"
                }

slideOfScan = {
            "element": "isSlideOfScan",
            "qualifier": None,
            "scopeNote": "",
            "type": "metadatafield"
                }

WsiOfScan = {
            "element": "isWsiOfScan",
            "qualifier": None,
            "scopeNote": "",
            "type": "metadatafield"
                }

scanOfWsi = {
            "element": "isScanOfWsi",
            "qualifier": None,
            "scopeNote": "",
            "type": "metadatafield"
                }

slideOfWsi = {
            "element": "isSlideOfWsi",
            "qualifier": None,
            "scopeNote": "",
            "type": "metadatafield"
                }
WsiOfslide = {
            "element": "isWsiOfSlide",
            "qualifier": None,
            "scopeNote": "",
            "type": "metadatafield"
                }

status = mf.createMetadataField ("relation", scanOfSlide)
status = mf.createMetadataField ("relation", slideOfScan)
status = mf.createMetadataField ("relation", scanOfWsi)
status = mf.createMetadataField ("relation", WsiOfScan)
status = mf.createMetadataField ("relation", slideOfWsi)
status = mf.createMetadataField ("relation", WsiOfslide)


path = 'metadatafields'
schemafiles = [f for f in listdir(path) if isfile(join(path, f))]

for sf in schemafiles:
    schema = splitext(sf)[0]
    filename = join(path, sf)
    print(schema, filename)

    with open(filename) as f:
        schemadata = json.load(f)

    #print(json.dumps(schemadata, indent=4, sort_keys=True))

    status = mf.createSchema(schema, "htttp://bbmri-eric.eu/schemas/"+schema)
    print(status)

    metadatafields = mf.metadataFieldsForSchema(schema)
    print(json.dumps(metadatafields, indent=4, sort_keys=True))

    for mdf in metadatafields:
        status = mf.deleteMetadataField(mdf['id'])

    for mdf in schemadata:
        status = mf.createMetadataField(schema, mdf)

    metadatafields = mf.metadataFieldsForSchema(schema)
    #print(json.dumps(metadatafields, indent=4, sort_keys=True))



