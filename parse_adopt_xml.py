import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import uuid
from xml.etree.ElementTree import QName
from parser import *
import subprocess
import json
import pandas
import requests


class Parse_file:

    def __init__(self, *args, **kwargs):
        self.xml_file = args[0]
        self.csv_file = args[1]
        self.metadata_dict = args[2]

    def parse_xml(self):
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        for child in root:
            print(child)

    def parse_csv(self):

        # with open(self.csv_file, "r") as fp:
        #     for i, line in enumerate(fp.readlines()):
        #         print(line.strip("\n").split(";"))
        #         input()

        pandas_csv = pandas.read_csv(self.csv_file, sep=";")
        print(pandas_csv)

        for item in pandas_csv.items():
            print(item)
            #input()


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
        self.aep = api_entry_point
        self.h = header

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
                if page >= totalPages:
                    stillPagesToRead = False
        return items

    def createItem(self, collection_uiid, item):
        url = self.aep + 'core/items?owningCollection=' + collection_uiid
        r = requests.post(url, headers=h, json=item)
        status = r.status_code
        createresponse = json.loads(r.content)
        print(json.dumps(createrespone, indent=4, sort_keys=True))
        return status, createresponse['id']

    def deleteItem(self, item_uiid):
        url = self.aep + 'core/items/' + item_uiid
        r = requests.delete(url, headers=h)
        print(url, " DELETED ", r.status_code)

    def createBundle(self, item_uiid, bundle):
        url = self.aep + 'api/core/items/' + item_uiid + '/bundles'
        r = requests.post(url, headers=h, json=bundle)
        status = r.status_code
        createresponse = json.loads(r.content)
        print(json.dumps(createrespone, indent=4, sort_keys=True))
        return status, createresponse['id']

    def deleteBundle(self, item_uiid):
        url = self.aep + 'core/items/' + item_uiid
        r = requests.delete(url, headers=h)
        print(url, " DELETED ", r.status_code)

    def metadataarray(self, values):
        ma = []
        for v in values:
            ma.append({"value": v, "language": "en", "authority": None, "confidence": -1})
        return ma

    def metadataarrayneutral(self, values):
        ma = []
        for v in values:
            ma.append({"value": v, "authority": None, "confidence": -1})
        return ma

    def dummySlide(self):
        slideUUID = slideuuid = str(uuid.uuid4())
        slidemetadata = {
            "dc.contributor.author": self.metadataarrayneutral(["Plass, Markus", "Müller, Heimo"]),
            "dc.title": self.metadataarray([slideUUID]),
            "slide.identifier.label": self.metadataarrayneutral(["histoNR"]),
            "slide.identifier.uuidslide": self.metadataarrayneutral([slideUUID]),
            "slide.dimension.width": self.metadataarrayneutral(["25"]),
            "slide.dimension.height": self.metadataarrayneutral(["75"]),
            "dc.type": self.metadataarrayneutral(["slide"]),
            "relationship.type": self.metadataarrayneutral(["Slide"])
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

    def dummyScan(self, slideid):
        scanUUID = slideuuid = str(uuid.uuid4())
        scanmetadata = {
            "dc.contributor.author": self.metadataarrayneutral(["Plass, Markus", "Müller, Heimo"]),
            "dc.title": self.metadataarrayneutral([scanUUID]),
            "scan.scanner.type": self.metadataarrayneutral(["P1000"]),
            "scan.scanner.manufacturer": self.metadataarrayneutral(["3D Histech"]),
            "scan.scanner.serial-number": self.metadataarrayneutral(["2991-99201-9919919"]),
            "scan.operator": self.metadataarrayneutral(["Plass, Markus"]),
            "dc.type": self.metadataarrayneutral(["scan"]),
            "relationship.type": self.metadataarrayneutral(["Scan"]),
            "relation.isScanOfSlide": self.metadataarray([slideid])
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

    def dummy_wsi(self, wsi_id):
        pass


    def dummyBundle(self):

        bundle = {
            "name": "ORIGINAL",
            "metadata": {}
        }


if __name__ == "__main__":

    # parser = Parse_file("/home/simon/Documents/Arbeit_med_Uni/app-digital-repository-tests/ADOPT-Graz.xml",
    #                     "/home/simon/Documents/Arbeit_med_Uni/app-digital-repository-tests/CSV_Scanns.csv")
    #
    # parser.parse_xml()
    # parser.parse_csv()

    runningEnv = 'silicolab'

    if runningEnv == 'silicolab':
        params = {'user': 'v@bibbox.org', 'password': 'vendetta'}
        serverurlprefix  = 'http://dspace-rest.silicolab.bibbox.org'
        MUGtestcollection = '2d91da67-e0de-4c29-9888-8f374a0924ac'

    if runningEnv == 'dspace':
        params = {'user': 'dspacedemo+admin@gmail.com', 'password': 'dspace'}
        serverurlprefix  = 'https://dspace7.4science.cloud'
        MUGtestcollection = '865f143a-cb9e-43cb-8a0d-9237df935ce0'

    r = requests.post(serverurlprefix + '/server/api/authn/login', params=params)
    h = {'Authorization': r.headers['Authorization']}


    mf = MetadataFields(serverurlprefix + '/server/api/', h)

    schemas = mf.schemas()
    print(json.dumps(schemas, indent=4, sort_keys=True))
    print(h)
    input()


    # for s in schemas:
    #    prefix = s['prefix']
    #    metadatafields = mf.metadataFieldsForSchema(prefix)
    #    print ('=================== ' + prefix + ' ='+ '='*(25-len(prefix)) + ' ' + str(len(metadatafields)))
    #    mf.printMetadataFields (prefix, metadatafields)
    save = False
    schemes = ["slide", "scan", "wsi"]
    field_keys = ["id", "element", "qualifier", "scopeNote", "type"]
    csv_header = ['Patient-ID', 'Case-ID', 'Block-ID', 'Slide-ID', 'Scan-ID', 'Barcode', 'Pfad', 'Staining', 'WSI-ID', 'DSPACE-URL']

    standart_values = ["80%", "jpg", "scanable", "cleaned", "Semi-Automated", "Layer", "Fakelman", "Colon", "8", "RGB", "P1000", "DS", "FFPE",
                       "ADOPT", "True", "MRXS", "Human", "Operational"]
    replace_csv = [["NA1",  "slide.caseUUID", "NA3", "slide.identifier.uuidslide", "NA4",
                   ['slide.label.normalized', 'slide.label.transcribed', 'slide.identifier.label'], "NA2", "slide.staining",
                    "NA5", "NA6"],
                   ["relation.isScanOfSlide", "scan.file", "scan.identifier"],
                   ["wsi.identifier"]]

    scan_additional_fields = []
    phil_insert_keys = []
    metadata_dicts = [{}, {}, {}]
    for n, schema in enumerate(schemes):
        dict_curr = metadata_dicts[n]
        with open(schema +".txt", "r") as fp:
            for line in fp.readlines():
                print(line.strip("\n"))
                print(line.strip("\n").split(" ")[0])
                print(line.strip("\n").split(" ")[-1])
                if line.strip("\n").split(" ")[0] in replace_csv[n]:
                    pass
                elif line.strip("\n").split(" ")[-1] in standart_values:
                    print(line.strip("\n").split(" ")[0])
                    print(line.strip("\n").split(" ")[-1])
                    if line.strip("\n").split(" ")[-1] == "Layer" or line.strip("\n").split(" ")[-1] == "Fakelman" or \
                        line.strip("\n").split(" ")[-1] == "P1000":
                        insert_val = line.strip("\n").split(" ")[-2] + " " +  line.strip("\n").split(" ")[-1]
                        dict_curr.update({line.strip("\n").split(" ")[0]: insert_val})
                    else:
                        dict_curr.update({line.strip("\n").split(" ")[0]:line.strip("\n").split(" ")[-1]})

                elif not line.strip("\n").split(" ")[-1].lower() == "leer":
                    phil_insert_keys.append(line.strip("\n").split(" ")[0])

        print(phil_insert_keys)
        print(dict_curr)
        input()
        metadatafields = mf.metadataFieldsForSchema(schema)
        print(json.dumps(metadatafields, indent=4, sort_keys=True))
        for field in metadatafields:
            metadata_key = schema + "."
            for i, key in enumerate(field.keys()):
                if i == 1 and not (field[key] is None):
                    metadata_key += (field[key])
                elif i == 2 and not (field[key] is None):
                    metadata_key += ("." + field[key])
            if not dict_curr.get(metadata_key, False):
                dict_curr.update({metadata_key: None})

        print(dict_curr)
        print(json.dumps(dict_curr, indent=4, sort_keys=True))
        print(len(dict_curr))
        print(len(metadatafields))
        input()
        if save:
            with open(schema + "metadata_dict.json", "w") as fp:
                json.dump(dict_curr, fp)
    for item in metadata_dicts:
        parser = Parse_file("/home/simon/Documents/Arbeit_med_Uni/app-digital-repository-tests/ADOPT-Graz.xml",
                            "/home/simon/Documents/Arbeit_med_Uni/app-digital-repository-tests/CSV_Scanns.csv",
                            item)

        parser.parse_csv()


    with open("scanmetadata_dict.json", "r") as fp:
        scanmeta_dict = json.load(fp)

    for item in scanmeta_dict.keys():
        print("{}:{}".format(item, scanmeta_dict[item]))

    test = json.load()
    items = Items(serverurlprefix + '/server/api/', h)

    headers = {
        'Content-Type': 'multipart/form-data',
        'Authorization': 'Bearer eyJhbGciOiJI...',
    }

    files = {
        'file': ('Downloads/test.html', open('Downloads/test.html', 'rb')),
        'properties': (None,
                       '{ "name": "test.html", "metadata": { "dc.description": [ { "value": "example file", "language": null, "authority": null, "confidence": -1, "place": 0 } ]}, "bundleName": "ORIGINAL" };type'),
    }

    response = requests.post(
        'https://dspace7.4science.cloud/dspace-spring-rest/api/core/bundles/d3599177-0408-403b-9f8d-d300edd79edb/bitstreams',
        headers=headers, files=files)