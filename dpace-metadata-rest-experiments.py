import json, requests
import string

class MetadataFields:
    def __init__(self, api_entry_point, header):
        self.aep    = api_entry_point
        self.h      = header

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

    def schemaID (self, prefix):
        schemas = self.schemas()
        lookuptable = {}
        id = -1
        for s in schemas:
            if prefix == s['prefix']: 
                id = s['id']
        print (id)
        return id

    def  deleteSchema (self, prefix):
        id = self.schemaID(prefix)
        status = -1
        if id > 0:
            url = self.aep + 'core/metadataschemas/' + str(id)  
            r = requests.delete(url, headers = h)   
            status = r.status_code
        return (status)

    def createSchema (self, prefix, namespace):
        url = self.aep + 'core/metadataschemas'          
        r = requests.post(url, headers = h, json = {"prefix": prefix, "namespace": namespace, "type": "metadataschema"})        
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
            r = requests.get(url, headers = h)
            halrespone = json.loads(r.content)
            totalPages = 1
            print(json.dumps(halrespone,  indent=4, sort_keys=True))
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
        r = requests.delete (url, headers = h)
        print (url, " DELETED ", r.status_code )



r = requests.post('http://dspace-rest.silicolab.bibbox.org/server/api/authn/login?user=v@bibbox.org&password=vendetta') 
h = {'Authorization':r.headers['Authorization']}

mf =  MetadataFields ('http://dspace-rest.silicolab.bibbox.org/server/api/', h)

#print(json.dumps(schemas, indent=4, sort_keys=True))

#schemas = mf.schemas()
#for s in schemas:
#    prefix = s['prefix']
#    metadatafields = mf.metadataFieldsForSchema(prefix)
#    print ('=================== ' + prefix + ' ='+ '='*(25-len(prefix)) + ' ' + str(len(metadatafields)))
#    mf.printMetadataFields (prefix, metadatafields)


schema = 'project'
metadatafields = mf.metadataFieldsForSchema(schema)
#mf.printMetadataFields (schema, metadatafields)
print(json.dumps(metadatafields, indent=4, sort_keys=True))

#MUGtestcollection = 'eb6be443-f55e-466c-b2b3-aa6bae97686d'
#items = mf.itemsInScope(MUGtestcollection)
#print(json.dumps(items, indent=4, sort_keys=True))

#for i in items:
#    mf.deleteItem (i['id'])

r = mf.deleteSchema ('slide')
r = mf.deleteSchema ('scan')
r = mf.deleteSchema ('wsi')
r = mf.createSchema ('slide', "htttp://bbmri-eric.eu/schemas/slide",)
r = mf.createSchema ('scan', "htttp://bbmri-eric.eu/schemas/scan",)
r = mf.createSchema ('wsi', "htttp://bbmri-eric.eu/schemas/wsi",)



