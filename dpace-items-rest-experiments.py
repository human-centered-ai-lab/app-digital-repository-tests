import json, requests
import string
import uuid


class MetadataFields:
    '''
    Object handling Metadata creation slots and
    '''

    def __init__(self, api_entry_point, header):

        self.aep = api_entry_point
        self.h = header

    def schemas(self):
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
                    metadataschemas.append(mds)
            page = page + 1
            if (page >= totalPages):
                stillPagesToRead = False
        return metadataschemas

    def schemaID(self, prefix):
        schemas = self.schemas()

        lookuptable = {}

        id = -1
        for s in schemas:
            if prefix == s['prefix']:
                id = s['id']
        #        print (id)
        return id

    def deleteSchema(self, prefix):
        id = self.schemaID(prefix)
        status = -1
        if id > 0:
            url = self.aep + 'core/metadataschemas/' + str(id)
            r = requests.delete(url, headers=h)
            status = r.status_code
        return (status)

    def createSchema(self, prefix, namespace):
        url = self.aep + 'core/metadataschemas'
        r = requests.post(url, headers=h, json={"prefix": prefix, "namespace": namespace, "type": "metadataschema"})
        return (r.status_code)

    def metadataFieldsForSchema(self, schema):

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
            url = self.aep + 'core/metadatafields/search/bySchema?schema=' + schema + '&page=' + str(page)
            r = requests.get(url, headers=h)
            halrespone = json.loads(r.content)
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']
            if '_embedded' in halrespone.keys():
                for mdf in halrespone['_embedded']['metadatafields']:
                    del mdf["_links"]
                    del mdf["_embedded"]
                    metadatafields.append(mdf)
            page = page + 1
            if page >= totalPages:
                stillPagesToRead = False
        return metadatafields

    def createMetadataField(self, prefix, mdf):
        id = self.schemaID(prefix)
        status = -1
        if id > 0:
            url = self.aep + 'core/metadatafields?schemaId=' + str(id)
            r = requests.post(url, headers=h, json=mdf)
            status = r.status_code
        return (status)

    def deleteMetadataField(self, id):
        url = self.aep + 'core/metadatafields/' + str(id)
        r = requests.delete(url, headers=h)
        status = r.status_code
        return (status)

    def printMetadataFields(self, prefix, metadatafields):
        i = 1
        for mf in metadatafields:
            infostring = str(i) + ':' + prefix + '.' + mf['element']
            if (type(mf['qualifier']) == str):
                if len(mf['qualifier']) > 0:
                    infostring = infostring + '.' + mf['qualifier']
            if (type(mf['scopeNote']) == str):
                scopeNote = mf['scopeNote'].replace('\n', '')
                infostring = infostring + ',' + scopeNote

            print(infostring)
            i = i + 1

    def itemsInScope(self, scope):

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
            url = self.aep + 'discover/search/objects?scope=' + scope + '&page=' + str(page)
            r = requests.get(url, headers=h)
            halrespone = json.loads(r.content)
            totalPages = 1
            # print(json.dumps(halrespone,  indent=4, sort_keys=True))
            if '_embedded' in halrespone.keys():
                totalPages = halrespone['_embedded']['searchResult']['page']['totalPages']
                pageNumber = halrespone['_embedded']['searchResult']['page']['number']
                for objects in halrespone['_embedded']['searchResult']['_embedded']['objects']:
                    io = objects['_embedded']['indexableObject']
                    del io["_links"]
                    # del io ["_embedded"]
                    items.append(io)
                page = page + 1
                if (page >= totalPages):
                    stillPagesToRead = False
        return items

    def deleteItem(self, item_uiid):
        url = self.aep + 'core/items/' + item_uiid
        r = requests.delete(url, headers=h)
        print(url, " DELETED ", r.status_code)

class Items:
    
    def __init__(self, api_entry_point, header):
        self.aep    = api_entry_point
        self.h      = header

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
                if page >= totalPages:
                    stillPagesToRead = False
        return items

    def createItem (self, collection_uiid, item):
        url = self.aep + 'core/items?owningCollection=' + collection_uiid
        r = requests.post(url, headers=h, json=item)
        status = r.status_code
        createrespone = json.loads(r.content)
        print(json.dumps(createrespone,  indent=4, sort_keys=True))
        return status, createrespone['id']


    def deleteItem (self, item_uiid):
        url = self.aep + 'core/items/' + item_uiid        
        r = requests.delete (url, headers=h)
        print(url, " DELETED ", r.status_code)

    def metadataarray (self, values):
        ma = []
        for v in values:
            ma.append({"value": v, "language": "en", "authority": None, "confidence": -1})
        return ma

    def metadataarrayneutral (self, values):
        ma = []
        for v in values:
            ma.append({"value": v, "authority": None, "confidence": -1})
        return ma


    def dummySlide (self):
        slideUUID = slideuuid = str(uuid.uuid4())
        slidemetadata = {
            "dc.contributor.author":      self.metadataarrayneutral(["Plass, Markus", "Müller, Heimo"]),
            "dc.title":                   self.metadataarray([slideUUID]),
            "slide.identifier.label":     self.metadataarrayneutral(["histoNR"]),
            "slide.identifier.uuidslide": self.metadataarrayneutral([slideUUID]),
            "slide.dimension.width":      self.metadataarrayneutral(["25"]),
            "slide.dimension.height":     self.metadataarrayneutral(["75"]),
            "dc.type":                    self.metadataarrayneutral(["slide"]),
            "relationship.type":          self.metadataarrayneutral(["Slide"])
        }


        slide = {
            "name": slideUUID,
            "inArchive": True,
            "discoverable": True,
            "withdrawn": False,
            "type": "Slide",
            "metadata": slidemetadata
            }

        return slide

    def dummyScan (self, slideid):
        scanUUID = slideuuid = str(uuid.uuid4())
        scanmetadata = {
            "dc.contributor.author":      self.metadataarrayneutral (["Plass, Markus", "Müller, Heimo"]),
            "dc.title":                   self.metadataarrayneutral ([scanUUID]),
            "scan.scanner.type":          self.metadataarrayneutral (["P1000"]),
            "scan.scanner.manufacturer":  self.metadataarrayneutral (["3D Histech"]),
            "scan.scanner.serial-number": self.metadataarrayneutral (["2991-99201-9919919"]),
            "scan.operator":              self.metadataarrayneutral (["Plass, Markus"]),
            "dc.type":                    self.metadataarrayneutral (["scan"]),
            "relationship.type":          self.metadataarrayneutral (["Scan"]),
            "relation.isScanOfSlide":     self.metadataarray([slideid])
        }

        scan = {
            "name": scanUUID,
            "inArchive": True,
            "discoverable": True,
            "withdrawn": False,
            "type": "Scan",
            "metadata": scanmetadata
            }

        return scan



runningEnv = 'silicolab'

if runningEnv == 'silicolab':
    params = {'user': 'v@bibbox.org', 'password': 'vendetta'}
    serverurlprefix  = 'http://dspace-rest.silicolab.bibbox.org'
    MUGtestcollection = '2d91da67-e0de-4c29-9888-8f374a0924ac'

if runningEnv == 'dspace':
    params = {'user': 'dspacedemo+admin@gmail.com', 'password': 'dspace'}
    serverurlprefix  = 'https://dspace7.4science.cloud'
    MUGtestcollection = '865f143a-cb9e-43cb-8a0d-9237df935ce0'


if runningEnv == 'localhost':
    params = {'user': 'v@bibbox.org', 'password': 'vendetta'}
    serverurlprefix  = 'http://localhost:8080'
    MUGtestcollection = 'ca5c1bb5-7886-40a1-8ead-65d9f5733785'


r = requests.post(serverurlprefix + '/server/api/authn/login', params=params)
h = {'Authorization': r.headers['Authorization']}

print(h)
input()

items = Items(serverurlprefix + '/server/api/', h)



founditems = items.itemsInScope(MUGtestcollection)
for i in founditems:
    items.deleteItem(i['id'])

for i in range(1, 2):
    print(i)
    status, slideid = items.createItem(MUGtestcollection, items.dummySlide())
    print(slideid)
    input()
    status, scanid1 = items.createItem(MUGtestcollection, items.dummyScan(slideid))
    status, scanid2 = items.createItem(MUGtestcollection, items.dummyScan(slideid))
    print(slideid, scanid1, scanid2)


