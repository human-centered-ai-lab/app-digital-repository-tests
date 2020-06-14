import json, requests
import string
import uuid
import random
from datetime import date


class Communities:
    def __init__(self, api_entry_point, header):
        self.aep    = api_entry_point
        self.h      = header

    def communities (self):
        example = {
            "id": "579d7e3b-bf70-4f7c-8bdc-9c5c517bdce9",
            "uuid": "579d7e3b-bf70-4f7c-8bdc-9c5c517bdce9",
            "name": "Medical University of Graz",
            "handle": "123456789/1",
            "metadata" : {}
        }

        communities = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/communities/search/top?page=' + str(page)
            r = requests.get(url, headers = self.h )
            halrespone = json.loads(r.content)
            #print(json.dumps(halrespone,  indent=4, sort_keys=True))
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']
            if  '_embedded' in halrespone.keys(): 
                for mds in halrespone['_embedded']['communities']:
                    del mds ["_links"]
                    communities.append (mds)
            page = page + 1
            if (page  >= totalPages):
                stillPagesToRead = False
        return communities

    def subcommunities (self, parent):
        example = {
            "id": "579d7e3b-bf70-4f7c-8bdc-9c5c517bdce9",
            "uuid": "579d7e3b-bf70-4f7c-8bdc-9c5c517bdce9",
            "name": "Medical University of Graz",
            "handle": "123456789/1",
            "metadata" : {}
        }

        subcommunities = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/communities/' + str(parent) + '/subcommunities?page=' + str(page)
            r = requests.get(url, headers = self.h )
            halrespone = json.loads(r.content)
            #print (url)
            #print(json.dumps(halrespone,  indent=4, sort_keys=True))
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']
            if  '_embedded' in halrespone.keys(): 
                for mds in halrespone['_embedded']['subcommunities']:
                    del mds ["_links"]
                    subcommunities.append (mds)
            page = page + 1
            if (page  >= totalPages):
                stillPagesToRead = False
        return subcommunities

    def collections (self, parent):
        example = {
            "id": "579d7e3b-bf70-4f7c-8bdc-9c5c517bdce9",
            "uuid": "579d7e3b-bf70-4f7c-8bdc-9c5c517bdce9",
            "name": "Medical University of Graz",
            "handle": "123456789/1",
            "metadata" : {}
        }

        collections = []
        stillPagesToRead = True
        page = 0
        while stillPagesToRead:
            url = self.aep + 'core/communities/' + str(parent) + '/collections?page=' + str(page)
            r = requests.get(url, headers = self.h )
            halrespone = json.loads(r.content)
            #print(json.dumps(halrespone,  indent=4, sort_keys=True))
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']
            if  '_embedded' in halrespone.keys(): 
                for mds in halrespone['_embedded']['collections']:
                    del mds ["_links"]
                    collections.append (mds)
            page = page + 1
            if (page  >= totalPages):
                stillPagesToRead = False
        return collections    

    def topCommunityID (self, name):
        com = self.communities()
        id = -1
        for c in com:
            if name == c['name']: 
                id = c['id']
        return id

    def communityID (self, name, parent):
        com = self.subcommunities(parent)
        id = -1
        for c in com:
            if name == c['name']: 
                id = c['id']
        return id

    def collectionID (self, name, parent):
        com = self.collections(parent)
        id = -1
        for c in com:
            if name == c['name']: 
                id = c['id']
        return id


    def createCommunity(self, name):

        payload = {"type":{"value":"community"},
                   "metadata":{"dc.title":[{"language":None,"value":name}],
                            "dc.description":[{"language":None}],
                            "dc.description.abstract":[{"language":None}],
                            "dc.rights":[{"language":None}],
                            "dc.description.tableofcontents":[{"language":None}]}}

        url = self.aep + 'core/communities'
        r = requests.post(url, headers = self.h , json = payload)   
        status = r.status_code
        createrespone = json.loads(r.content)
        print (url, " CREATED ", r.status_code)
        #print(json.dumps(item,  indent=4, sort_keys=True))
        #print(json.dumps(createrespone,  indent=4, sort_keys=True))
        return (status, createrespone['id'] )

    def createSubCommunity(self, name, parent):

        payload = {"type":{"value":"community"},
                   "metadata":{"dc.title":[{"language":None,"value":name}],
                            "dc.description":[{"language":None}],
                            "dc.description.abstract":[{"language":None}],
                            "dc.rights":[{"language":None}],
                            "dc.description.tableofcontents":[{"language":None}]}}

        url = self.aep + 'core/communities?parent='+str(parent)
        r = requests.post(url, headers = self.h , json = payload)   
        status = r.status_code
        createrespone = json.loads(r.content)
        #print (url, " CREATED ", r.status_code)
        #print(json.dumps(createrespone,  indent=4, sort_keys=True))
        return (status, createrespone['id'] )

    def createCollection(self, name, parent):

        payload = {"type":{"value":"community"},
                   "metadata":{"dc.title":[{"language":None,"value":name}],
                            "dc.description":[{"language":None}],
                            "dc.description.abstract":[{"language":None}],
                            "dc.rights":[{"language":None}],
                            "dc.description.provenance":[{"language":None}],
                            "dc.description.tableofcontents":[{"language":None}]}}

        url = self.aep + 'core/collections?parent=' + str(parent)
        r = requests.post(url, headers = self.h , json = payload)   
        status = r.status_code
        createrespone = json.loads(r.content)
        print (url, " CREATED ", r.status_code)
        #print(json.dumps(item,  indent=4, sort_keys=True))
        #print(json.dumps(createrespone,  indent=4, sort_keys=True))
        return (status, createrespone['id'] )

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
            r = requests.get(url, headers = self.h )
            halrespone = json.loads(r.content)
            #print(json.dumps(halrespone,  indent=4, sort_keys=True))
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
            r = requests.get(url, headers = self.h )
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
        r = requests.post(url, headers = self.h , json = item)   
        status = r.status_code
        createrespone = json.loads(r.content)
        print (url, " CREATED ", r.status_code)
        #print(json.dumps(item,  indent=4, sort_keys=True))
        #print(json.dumps(createrespone,  indent=4, sort_keys=True))
        return (status, createrespone['id'] )


    def deleteItem (self, item_uiid):
        url = self.aep + 'core/items/' + item_uiid        
        r = requests.delete (url, headers = self.h )
        print (url, " DELETED ", r.status_code )


    def createRelationship (self, reltypeID, leftID, rightID):
        url = self.aep + 'core/relationships?relationshipType=' + str(reltypeID)
        uriListBody  = self.aep + 'core/items/' + leftID + ' \n ' + self.aep + 'core/items/' + rightID
        h2 = self.h.copy() 
        h2['Content-Type'] = 'text/uri-list' 
        #print (url)
        #print (uriListBody)
        r = requests.post(url, headers = h2, data = uriListBody)   
        status = r.status_code
        print (url, " CREATED ", r.status_code)
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
        slideUUID = str(uuid.uuid4())
        
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

    def dummyWSI (self, primary, slideid, scanid):
        wsiUUID = str(uuid.uuid4())
        now = date.today().isoformat()
        author = random.choice (["Plass, Markus", "Heimo Müller", "Robert Reihs", "Simon Streit"]) 
        wsiformat = random.choice (["MIRAX", "SVS", "TIFF", "DICOM"])
        compression = random.choice (["JPEG", "JPEG2000", "UNCOMPRESSED"])
        size =   random.randint(4000000000,12000000000)
        sizeGB = str (int (10 * size / 1024 / 1024 / 1024 ) / 10) + " GByte"
        usage =  random.choice (["Archive", "Processing", "Viewing", "ML"])
        col = random.randint(10000,20000)
        row = random.randint(5000,10000)
        x = random.randint(2000,100000)
        y = random.randint(30000,500000)
        xstr = str (x / 10000)
        ystr = str (y / 10000)
        resolution = random.choice (["0.25", "0.125", "0.5"])
        if (resolution == "0.125"):
            col = 4 * col
            row = 4 * row
            mag = "80x"
        if (resolution == "0.25"):
            col = 2 * col
            row = 2 * row
            mag = "40x"
        if (resolution == "0.5"):
            mag = "20x"

        wsiTitle = wsiformat + ", " + mag + ", " + str(col) + "x" + str(row) + ", " + sizeGB
        wsimetadata = {
            "dc.contributor.author":      self.metadataarrayneutral ([author]),
            "dc.title":                   self.metadataarrayneutral ([wsiTitle]),
            "wsi.size": self.metadataarrayneutral ([str(size)]),
            "wsi.imagesize.columns": self.metadataarrayneutral ([str(col)]),
            "wsi.imagesize.rows":    self.metadataarrayneutral ([str(row)]),  
            "wsi.imagesize.spatial-resolution":     self.metadataarrayneutral ([resolution]),
            "wsi.image-matrix-origin.x":     self.metadataarrayneutral ([xstr]),
            "wsi.image-matrix-origin.y":     self.metadataarrayneutral ([ystr]),
            "wsi.image-matrix-origin.z":   self.metadataarrayneutral (["0.000"]),   
            "wsi.primary":      self.metadataarrayneutral ([primary]),
            "wsi.format.type":      self.metadataarrayneutral ([wsiformat]),
            "wsi.format.version":   self.metadataarrayneutral (["1.0"]),  
            "wsi.MD5Checksum":     self.metadataarrayneutral (["aca28a846e26ffd9234212f9ceb4536f"]),
            "wsi.compression.type":     self.metadataarrayneutral ([compression]),
            "wsi.contains.previewimage":    self.metadataarrayneutral ([random.choice (["YES", "NO"])]), 
            "wsi.contains.anonymized-label":  self.metadataarrayneutral ([random.choice (["YES", "NO"])]),   
            "wsi.contains.label":     self.metadataarrayneutral ([random.choice (["YES", "NO"])]),  
            "dc.type":                    self.metadataarrayneutral (["Wsi"]),
            "relationship.type":          self.metadataarrayneutral (["Wsi"])
        }

        wsi = {
            "name": wsiUUID,
            "inArchive": True,
            "discoverable": True,
            "withdrawn": False,
            "type": "Wsi",
            "metadata": wsimetadata
            }

        #print(json.dumps(wsimetadata,  indent=4, sort_keys=True))

        return wsi         

    def dummyScan (self, slideid):
        scanUUID = str(uuid.uuid4())
        now = date.today().isoformat()
 
        manufacturer = random.choice (["3D Histech", "Leica"])

        resolution = random.choice (["0.25", "0.125", "0.5"])
        if (resolution == "0.125"):
            mag = "80x"
        if (resolution == "0.25"):
            mag = "40x"
        if (resolution == "0.5"):
            mag = "20x"

        manufacturer = random.choice (["3D Histech", "Leica"])
        if (manufacturer == "3D Histech"):
            scannerType = random.choice (["P1000", "P250"])
        if (manufacturer == "Leica"):
            scannerType = random.choice (["AT2", "GT450"])

        scanTitle = str(now) + ", " + manufacturer + " " + scannerType +", " + mag
        scanmetadata = {
            "dc.contributor.author":      self.metadataarrayneutral (["Plass, Markus", "Müller, Heimo"]),
            "dc.title":                   self.metadataarrayneutral ([scanTitle]),
            "scan.scanner.type":          self.metadataarrayneutral (["P1000"]),
            "scan.scanner.manufacturer":  self.metadataarrayneutral (["3D Histech"]),
            "scan.scanner.serial-number": self.metadataarrayneutral (["2991-99201-9919919"]),
            "scan.operator":              self.metadataarrayneutral (["Plass, Markus"]),
            "scan.date":                  self.metadataarrayneutral ([str(now)]),
            "scan.resolution":            self.metadataarrayneutral (resolution),  
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

if runningEnv == 'silicolab':
    params = {'user':'v@bibbox.org', 'password':'vendetta'}
    serverurlprefix  = 'http://dspace-rest.silicolab.bibbox.org'

if runningEnv == 'dspace':
    params = {'user':'dspacedemo+admin@gmail.com', 'password':'dspace'}
    serverurlprefix  = 'https://dspace7.4science.cloud'

if runningEnv == 'localhost':
    params = {'user':'v@bibbox.org', 'password':'vendetta'}
    serverurlprefix  = 'http://localhost:8080'
    
r = requests.post(serverurlprefix + '/server/api/authn/login', params = params) 
h = {'Authorization':r.headers['Authorization']}

com =  Communities (serverurlprefix + '/server/api/', h)
createCommunities = False

if (createCommunities):
    status, mugid   = com.createCommunity ("Medical University of Graz, Digital Assets")
    status, pathoid = com.createSubCommunity ("Institut of Pathology",mugid)
    status, scanid  = com.createCollection ("Scans", pathoid)
    status, slideid = com.createCollection ("Slides", pathoid)
    status, wsiid   = com.createCollection ("Whole Slide Images", pathoid)

mugcolid = com.topCommunityID ("Medical University of Graz, Digital Assets")
pathocolid = com.communityID ("Institut of Pathology",mugcolid)
scancolid = com.collectionID ("Scans", pathocolid)
slidecolid = com.collectionID ("Slides", pathocolid)
wsicolid = com.collectionID ("Whole Slide Images", pathocolid)

print ("COLLECTIONS")
print (mugcolid, pathocolid, scancolid, slidecolid, wsicolid)

items =  Items (serverurlprefix + '/server/api/', h)


relships = items.relationships()
RelIDSlide2Scan = items.relationshipsID ("isSlideOfScan", "isScanOfSlide")
RelIDScan2WSI = items.relationshipsID ("isScanOfWsi", "isWsiOfScan")
RelIDSlide2WSI = items.relationshipsID ("isSlideOfWsi", "isWsiOfSlide")
RelIDTransf2WSI = items.relationshipsID ("isTransformOfWsi", "isWsiOfTransform")

#print(json.dumps(relships,  indent=4, sort_keys=True))
print ("RELATIONSHIPS")
print(RelIDSlide2Scan, RelIDScan2WSI, RelIDSlide2WSI, RelIDTransf2WSI)

for i in items.itemsInScope(slidecolid):
    items.deleteItem (i['id'])
for i in items.itemsInScope(scancolid):
    items.deleteItem (i['id'])
for i in items.itemsInScope(wsicolid):
    items.deleteItem (i['id'])


for i in range (1,5):
    print (i)
    status, slideid = items.createItem(slidecolid, items.dummySlide())
    status, scanid1 = items.createItem(scancolid, items.dummyScan(slideid))
    status, wsiid1  = items.createItem(wsicolid, items.dummyWSI("YES", slideid, scanid1))
    status, wsiid2  = items.createItem(wsicolid, items.dummyWSI("NO", slideid, scanid1))
    status, wsiid3  = items.createItem(wsicolid, items.dummyWSI("NO", slideid, scanid1))
    status, scanid2 = items.createItem(scancolid, items.dummyScan(slideid))
    status, wsiid4  = items.createItem(wsicolid, items.dummyWSI("YES", slideid, scanid2))

    items.createRelationship (RelIDSlide2Scan, slideid, scanid1)
    items.createRelationship (RelIDSlide2Scan, slideid, scanid2)

    items.createRelationship (RelIDScan2WSI,  scanid1, wsiid1)
    items.createRelationship (RelIDScan2WSI,  scanid1, wsiid2)
    items.createRelationship (RelIDScan2WSI,  scanid1, wsiid3)

    items.createRelationship (RelIDScan2WSI,  scanid2, wsiid4)

    items.createRelationship (RelIDSlide2WSI, slideid, wsiid1)
    items.createRelationship (RelIDSlide2WSI, slideid, wsiid2)
    items.createRelationship (RelIDSlide2WSI, slideid, wsiid3)
    items.createRelationship (RelIDSlide2WSI, slideid, wsiid4)

