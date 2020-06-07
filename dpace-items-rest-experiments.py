import json, requests
import string
import uuid


class Items:
    
    def __init__(self, api_entry_point, header):
        self.aep    = api_entry_point
        self.h      = header

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
for i in founditems:
    items.deleteItem (i['id'])


for i in range (1,2):
    print (i)
    status, slideid = items.createItem(MUGtestcollection, items.dummySlide())
    status, scanid1 = items.createItem(MUGtestcollection, items.dummyScan(slideid))
    status, scanid2 = items.createItem(MUGtestcollection, items.dummyScan(slideid))
    print (slideid, scanid1, scanid2)
