from os import listdir
from os.path import isfile, join, splitext
import json
import requests

def xsrf_token_check (response, session):
    if not len(response.cookies.keys()):
        #print('no changes to token')
        return

    #print('Token Check - Response Keys:', response.cookies.keys())
    #print('Token Check - Response Values:', response.cookies.values())

    xsrfTokenIndex = 0

    for index, value in enumerate(response.cookies.keys()):
        if value == 'DSPACE-XSRF-COOKIE':
            xsrfTokenIndex = index
            break

    print('DSPACE-XSRF-TOKEN : ', response.cookies.values()[xsrfTokenIndex])
    session.headers.update({'X-XSRF-TOKEN': response.cookies.values()[xsrfTokenIndex]})

class MetadataFields:
    def __init__(self, api_entry_point):
        self.aep    = api_entry_point


    def  schemas (self):
        example = {
            "id": 1,
            "namespace": "http://dublincore.org/documents/dcmi-terms/",
            "prefix": "dc",
            "type": "metadataschema"
        }

        metadataschemas = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/metadataschemas?page=' + str(page)
            r = s.get(url)
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

    def schemaID (self, prefix):
        schemas = self.schemas()
        lookuptable = {}
        id = -1
        for s in schemas:
            if prefix == s['prefix']: 
                id = s['id']
#        print (id)
        return id

    def  deleteSchema (self, prefix):
        id = self.schemaID(prefix)
        status = -1
        if id > 0:
            url = self.aep + 'core/metadataschemas/' + str(id)  
            r = s.delete(url)
            status = r.status_code
        return (status)

    def createSchema (self, prefix, namespace):
        url = self.aep + 'core/metadataschemas'          
        r = s.post(url, json = {"prefix": prefix, "namespace": namespace, "type": "metadataschema"})
        return (r.status_code)

    def metadataFieldsForSchema (self, schema):
        example = {
            "id": 434,
            "element": "quality",
            "qualifier": None,
            "scopeNote": "Q of the p slide",
            "type": "metadatafield"
        }
        metadatafields = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/metadatafields/search/bySchema?schema=' + schema +'&page=' + str(page)
            r = s.get(url)
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
    
    def createMetadataField (self, prefix, mdf):
        id = self.schemaID(prefix)
        status = -1
        if id > 0:
            url = self.aep + 'core/metadatafields?schemaId=' + str(id)  
            r = s.post(url, json = mdf)
            status = r.status_code
        return (status)

    def deleteMetadataField (self, id):
        url = self.aep + 'core/metadatafields/' + str(id)  
        r = s.delete(url)
        status = r.status_code
        return (status)

    def printMetadataFields (self, prefix, metadatafields):
        i = 1
        for mf in metadatafields:
            infostring = str(i) + ':  ' + prefix + '.' + mf['element']
            if ( type (mf['qualifier']) == str):
                if len (mf['qualifier'])  > 0:
                    infostring = infostring + '.'+ mf['qualifier']
            if ( type (mf['scopeNote']) == str):
                scopeNote = mf['scopeNote'].replace('\n', '')
                infostring = infostring + ',   ' + scopeNote

            print (infostring)
            i = i+1
    
    def itemsInScope (self, scope):
        example = {
            "discoverable": True,
            "handle": "123456789/504",
            "id": "728afa5e-b330-4030-8007-eb14174dbd0e",
            "inArchive": True,
            "lastModified": "2020-04-27T12:17:29.339+0000",
            "metadata": {}
        }

        items = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'discover/search/objects?scope=' + scope +'&page=' + str(page)
            r = s.get(url)
            halrespone = json.loads(r.content)
            totalPages = 1
            #print(json.dumps(halrespone,  indent=4, sort_keys=True))
            if  '_embedded' in halrespone.keys():
                totalPages = halrespone ['_embedded']['searchResult']['page']['totalPages']
                pageNumber = halrespone ['_embedded']['searchResult']['page']['number']
                for objects in halrespone['_embedded']['searchResult']['_embedded']['objects']:
                        io = objects['_embedded']['indexableObject']
                        del io ["_links"]
                        #del io ["_embedded"]
                        items.append (io)
                page = page + 1
                if (page  >= totalPages):
                    stillPagesToRead = False
        return items


    def deleteItem (self, item_uiid):
        url = self.aep + 'core/items/' + item_uiid
        r = s.delete (url)
        print (url, " DELETED ", r.status_code )

    def createRelationMetadatafield (self, relationMetadataField):
        description = {
            "element": relationMetadataField,
            "qualifier": None,
            "scopeNote": "",
            "type": "metadatafield"
                }
        status = mf.createMetadataField ("relation", description)
        return status


# ----------------------------------------------------------
# ~~ Enter running environment and admin-account login data
runningEnv = 'localhost'

if runningEnv == 'bibbox':
    params = {'user':'v@bibbox.org', 'password':'vendetta'}
    serverurlprefix  = 'http://rest.dspace.bibbox.org'
if runningEnv == 'silicolab':
    params = {'user':'v@bibbox.org', 'password':'vendetta'}
    serverurlprefix  = 'http://dspace-rest.silicolab.bibbox.org'
if runningEnv == 'dspace':
    params = {'user':'dspacedemo+admin@gmail.com', 'password':'dspace'}
    serverurlprefix  = 'https://dspace7.4science.cloud'
if runningEnv == 'localhost':
    params = {'user':'test@test.edu', 'password':'admin'}
    serverurlprefix  = 'http://localhost:8080'

# ~~ LOGIN
s = requests.Session()
r = s.get(serverurlprefix + '/server/api/authn/status')
xsrf_token_check(r, s)


r = s.post(serverurlprefix + '/server/api/authn/login', params = params)
xsrf_token_check(r, s)
s.headers.update({'Authorization': r.headers['Authorization']})

r = s.get(serverurlprefix + '/server/api/authn/status')
xsrf_token_check(r, s)
print('Status after Login', r, ', ', r.content)

mf =  MetadataFields (serverurlprefix + '/server/api/')

#schemas = mf.schemas()
#print(json.dumps(schemas, indent=4, sort_keys=True))

#for s in schemas:
#    prefix = s['prefix']
#    metadatafields = mf.metadataFieldsForSchema(prefix)
#    print ('=================== ' + prefix + ' ='+ '='*(25-len(prefix)) + ' ' + str(len(metadatafields)))
#    mf.printMetadataFields (prefix, metadatafields)



schema = 'project'
metadatafields = mf.metadataFieldsForSchema(schema)
print(json.dumps(metadatafields, indent=4, sort_keys=True))

mf.createRelationMetadatafield ("isScanOfSlide")
mf.createRelationMetadatafield ("isSlideOfScan")

mf.createRelationMetadatafield ("isScanOfWsi")
mf.createRelationMetadatafield ("isWsiOfScan")

mf.createRelationMetadatafield ("isTransformOfWsi")
mf.createRelationMetadatafield ("isWsiOfTransform")

mf.createRelationMetadatafield ("isWsiofSlide")
mf.createRelationMetadatafield ("isSlideofWsi")

path = 'metadatafields'
schemafiles = [f for f in listdir(path) if isfile(join(path, f))]


for sf in schemafiles:
    schema = splitext(sf)[0]
    filename = join(path, sf)
    print (schema, filename)

    with open(filename) as f:
        schemadata = json.load(f)

    print(json.dumps(schemadata, indent=4, sort_keys=True))

    status = mf.createSchema (schema, "htttp://bbmri-eric.eu/schemas/"+schema)
    print (status)

    metadatafields = mf.metadataFieldsForSchema(schema)
    print(json.dumps(metadatafields, indent=4, sort_keys=True))

    for mdf in metadatafields:
        status = mf.deleteMetadataField (mdf['id'])

    for mdf in schemadata:
        status = mf.createMetadataField (schema, mdf)

    metadatafields = mf.metadataFieldsForSchema(schema)
    print(json.dumps(metadatafields, indent=4, sort_keys=True))


