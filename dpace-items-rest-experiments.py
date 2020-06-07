import json, requests
import string
import uuid


class Items:
    
    def __init__(self, api_entry_point, header):
        self.aep    = api_entry_point
        self.h      = header

    def relationships (self):
        example = {
            "id": 1,
            "leftwardType": "isAuthorOfPublication",
            "rightwardType": "isPublicationOfAuthor",
            "copyToLeft": True,
            "copyToRight": True,
            "leftMinCardinality": 0,
            "leftMaxCardinality": None,
            "rightMinCardinality": 0,
            "rightMaxCardinality": None,
            "type": "relationshiptype",
        }

        relationships = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/relationshiptypes?page=' + str(page)
            r = requests.get(url, headers = h)
            halrespone = json.loads(r.content)
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']
            if  '_embedded' in halrespone.keys(): 
                for mds in halrespone['_embedded']['relationshiptypes']:
                    del mds ["_links"]
                    relationships.append (mds)
            page = page + 1
            if (page  >= totalPages):
                stillPagesToRead = False
        return relationships

    def relationshipsID (self, rightwardType, leftwardType):
        rel = self.relationships()
        id = -1
        for r in rel:
            if rightwardType == r['rightwardType'] and leftwardType == r['leftwardType'] : 
                id = r['id']
        return id

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

    def createItem (self, collection_uiid, item):
        url = self.aep + 'core/items?owningCollection=' + collection_uiid
        r = requests.post(url, headers = h, json = item)   
        status = r.status_code
        createrespone = json.loads(r.content)
        print(json.dumps(createrespone,  indent=4, sort_keys=True))
        return (status, createrespone['id'] )


    def deleteItem (self, item_uiid):
        url = self.aep + 'core/items/' + item_uiid        
        r = requests.delete (url, headers = h)
        print (url, " DELETED ", r.status_code )


    def createRelationship (self, reltypeID, leftID, rightID):
        url = self.aep + 'core/relationships?relationshipType=' + str(reltypeID)
        uriListBody  = self.aep + 'core/items/' + leftID + ' \n ' + self.aep + 'core/items/' + rightID
        h2 = h 
        h2['Content-Type'] = 'text/uri-list' 
        #print (url)
        #print (uriListBody)
        r = requests.post(url, headers = h2, data = uriListBody)   
        status = r.status_code
        createRespone = json.loads(r.content)
        #print(json.dumps(createRespone,  indent=4, sort_keys=True))
        return (status, createRespone['id'] )

    def metadataarray (self, values):
        ma = []
        for v in values:
            ma.append ({ "value":v, "language": "en", "authority": None,"confidence": -1 })
        return ma

    def metadataarrayneutral (self, values):
        ma = []
        for v in values:
            ma.append ({ "value":v, "authority": None,"confidence": -1 })
        return ma


    def dummySlide (self):
        slideUUID = slideuuid = str(uuid.uuid4())
        slidemetadata = {
            "dc.contributor.author":      self.metadataarrayneutral (["Plass, Markus", "Müller, Heimo"]),
            "dc.title":                   self.metadataarray ([slideUUID]),
            "slide.identifier.label":     self.metadataarrayneutral (["histoNR"]),
            "slide.identifier.uuidslide": self.metadataarrayneutral ([slideUUID]),
            "slide.dimension.width":      self.metadataarrayneutral (["25"]),
            "slide.dimension.height":     self.metadataarrayneutral (["75"]),
            "dc.type":                    self.metadataarrayneutral (["slide"]),
            "relationship.type":          self.metadataarrayneutral (["Slide"]),
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
            "relation.isScanOfSlide":     self.metadataarray ([slideid])
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

runningEnv = 'bibbox'

if runningEnv == 'bibbox':
    params = {'user':'v@bibbox.org', 'password':'vendetta'}
    serverurlprefix  = 'http://rest.dspace.bibbox.org'
    MUGtestcollection = '5b655b1e-1855-42f5-b720-da7ad31e2fa5'


if runningEnv == 'silicolab':
    params = {'user':'v@bibbox.org', 'password':'vendetta'}
    serverurlprefix  = 'http://dspace-rest.silicolab.bibbox.org'
    MUGtestcollection = 'eb6be443-f55e-466c-b2b3-aa6bae97686d'

if runningEnv == 'dspace':
    params = {'user':'dspacedemo+admin@gmail.com', 'password':'dspace'}
    serverurlprefix  = 'https://dspace7.4science.cloud'
    MUGtestcollection = '865f143a-cb9e-43cb-8a0d-9237df935ce0'

if runningEnv == 'localhost':
    params = {'user':'v@bibbox.org', 'password':'vendetta'}
    serverurlprefix  = 'http://localhost:8080'
    MUGtestcollection = 'ca5c1bb5-7886-40a1-8ead-65d9f5733785'


r = requests.post(serverurlprefix + '/server/api/authn/login', params = params) 
h = {'Authorization':r.headers['Authorization']}

items =  Items (serverurlprefix + '/server/api/', h)

founditems = items.itemsInScope(MUGtestcollection)

relships = items.relationships()

RelID = items.relationshipsID ("isSlideOfScan", "isScanOfSlide")

# print(json.dumps(relships,  indent=4, sort_keys=True))
#print(RelID)

for i in founditems:
    print (i['id'], i['metadata']['relationship.type'][0]['value'])

for i in founditems:
    items.deleteItem (i['id'])

for i in range (1,2):
    print (i)
    status, slideid = items.createItem(MUGtestcollection, items.dummySlide())
    status, scanid1 = items.createItem(MUGtestcollection, items.dummyScan(slideid))
    status, scanid2 = items.createItem(MUGtestcollection, items.dummyScan(slideid))
    status, scanid3 = items.createItem(MUGtestcollection, items.dummyScan(slideid))
    items.createRelationship (RelID, slideid, scanid1)
    items.createRelationship (RelID, slideid, scanid2)
    items.createRelationship (RelID, slideid, scanid3)
    print (slideid, scanid1, scanid2, scanid3)

