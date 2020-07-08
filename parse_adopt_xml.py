import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import uuid
from xml.etree.ElementTree import QName
from parser import *
import subprocess
import tqdm
import json
import pandas
import requests
import os
import time


class Parse_file:

    def __init__(self, *args, **kwargs):
        self.xml_file = args[0]
        self.scan_csv_file = args[1]
        self.db_csv_file = args[2]

    def parse_xml(self):
        tree = ET.parse(self.xml_file)
        root = tree.getroot()

    def parse_csv(self):

        pandas_csv_scan = pandas.read_csv(self.scan_csv_file, sep=";")
        pandas_csv_db = pandas.read_csv(self.db_csv_file, sep=";")

        return pandas_csv_scan, pandas_csv_db

class MetadataFields:
    '''
    Object handling Metadata scheme and field creation creation and
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
        return status

    def deleteMetadataField(self, id):
        url = self.aep + 'core/metadatafields/' + str(id)
        r = requests.delete(url, headers=h)
        status = r.status_code
        return status

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
            print(url)
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

    def get_item(self, item_uuid):
        url = self.aep + "core/items/" + item_uuid
        r = requests.get(url, headers=h)
        status = r.status_code
        createresponse = json.loads(r.content)
        #print(json.dumps(createresponse, indent=4, sort_keys=True))
        return status, createresponse['id']

    def createItem(self, collection_uiid, item):
        url = self.aep + 'core/items?owningCollection=' + collection_uiid
        r = requests.post(url, headers=h, json=item)
        status = r.status_code
        createresponse = json.loads(r.content)
        print(json.dumps(createresponse, indent=4, sort_keys=True))
        return status, createresponse['id']

    def deleteItem(self, item_uiid):
        url = self.aep + 'core/items/' + item_uiid
        r = requests.delete(url, headers=h)
        print(url, " DELETED ", r.status_code)

    def get_item_bundles(self, items):
            pass

    def get_item_bitsreams(self, items):
            pass

    def createBundle(self, item_uiid, bundle):
        url = self.aep + 'core/items/' + item_uiid + '/bundles'
        r = requests.post(url, headers=h, json=bundle)
        status = r.status_code
        createresponse = json.loads(r.content)
        #print(json.dumps(createresponse, indent=4, sort_keys=True))
        return status, createresponse['uuid']

    def deleteBundle(self, bundle_uiids):
        url = self.aep + 'core/bundles/' + bundle_uiid
        r = requests.delete(url, headers=h)
        print(url, " DELETED ", r.status_code)

    def createBitstream(self, bundle_uuid, files, bitstream):
        url = self.aep + 'core/bundles/' + bundle_uuid + '/bitstreams'
        # if u use files in python requests it automatically sets Content-Type:multipart/form
        r = requests.post(url, headers=h, files=files, json=bitstream)
        status = r.status_code
        #print(status)
        createresponse = json.loads(r.content)
        print(json.dumps(createresponse, indent=4, sort_keys=True))
        return status, createresponse['id']

    def deleteBitsream(self, uuid):
        pass

    def relationships(self):
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
            r = requests.get(url, headers=h)
            halrespone = json.loads(r.content)
            totalPages = halrespone['page']['totalPages']
            pageNumber = halrespone['page']['number']
            if '_embedded' in halrespone.keys():
                for mds in halrespone['_embedded']['relationshiptypes']:
                    del mds["_links"]
                    relationships.append(mds)
            page = page + 1
            if (page >= totalPages):
                stillPagesToRead = False
        return relationships

    def relationshipsID(self, rightwardType, leftwardType):
        rel = self.relationships()
        id = -1
        for r in rel:
            if rightwardType == r['rightwardType'] and leftwardType == r['leftwardType']:
                id = r['id']
        return id

    def createRelationship(self, reltypeID, leftID, rightID):
        url = self.aep + 'core/relationships?relationshipType=' + str(reltypeID)
        uriListBody = self.aep + 'core/items/' + leftID + ' \n ' + self.aep + 'core/items/' + rightID
        h2 = h.copy()
        h2['Content-Type'] = 'text/uri-list'
        # print (url)
        # print (uriListBody)
        r = requests.post(url, headers=h2, data=uriListBody)
        status = r.status_code
        print(url, " CREATED ", r.status_code)
        createRespone = json.loads(r.content)
        print(json.dumps(createRespone,  indent=4, sort_keys=True))
        return (status, createRespone['id'])

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

    def merge_values(self, val1, val2):
        if val1 is None:
            return self.metadataarrayneutral([val2])
        elif val2 is None:
            return val1
        else:
            return self.metadataarrayneutral([val2])

    def merge_values_neut(self, val1, val2):
        if val1 is None:
            return val2
        elif val2 is None:
            return val1
        else:
            return val2

    def dummySlide(self, add_metadata_dict, slideUUID, root, folders, current_id):

        #System metadata slide
        slidemetadata = {
            "dc.contributor.author": self.metadataarrayneutral(["Plass, Markus", "Müller, Heimo"]),
            "dc.title": self.metadataarray([slideUUID]),
            "slide.identifier.label": self.metadataarrayneutral(["histoNR"]),
            "slide.identifier.uuidslide": self.metadataarrayneutral([slideUUID]),
            "slide.dimension.width": self.metadataarrayneutral(["25"]),
            "slide.dimension.height": self.metadataarrayneutral(["75"]),
            "dc.type": self.metadataarrayneutral(["slide"]),
            "relationship.type": self.metadataarrayneutral(["Slide"]),
        }
        # print(folders)
        match = False
        for item in folders:
            # print(item)
            # print(current_id)
            if item == current_id:
                filepath_curr = os.path.join(root, item)
                for file in os.listdir(filepath_curr):
                    if "slide_meta" in file:
                        with open(os.path.join(filepath_curr, file), "r") as fp:
                            add_dict_phil = json.load(fp)
                            add_metadata_dict = {
                                field: self.merge_values_neut(add_metadata_dict.get(field), add_dict_phil.get(field))
                                for field in set(add_metadata_dict).union(add_dict_phil)}

        # add additional data fields

        slidemetadata = {field: self.merge_values(slidemetadata.get(field), add_metadata_dict.get(field))
        for field in set(slidemetadata).union(add_metadata_dict)}

        slide = {
            "name": slideUUID,
            "inArchive": True,
            "discoverable": True,
            "withdrawn": False,
            "type": "Slide",
            "metadata": slidemetadata
        }

        return slide,

    def dummyScan(self, slideid, add_metadata_dict, scanUUID, root, folders, current_id):
        #System metadata Scan
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

        for item in folders:
            if item == current_id:
                filepath_curr = os.path.join(root, item)
                match = True
                for file in os.listdir(filepath_curr):
                    if "scan_meta" in file:
                        #print(file)
                        with open(os.path.join(filepath_curr, file), "r") as fp:
                            add_dict_phil = json.load(fp)
                            add_metadata_dict = {
                                field: self.merge_values_neut(add_metadata_dict.get(field), add_dict_phil.get(field))
                                for field in set(add_metadata_dict).union(add_dict_phil)}
                        # print(json.dumps(add_dict_phil, indent=4, sort_keys=True))
                        # print(json.dumps(add_metadata_dict, indent=4, sort_keys=True))

        scanmetadata = {field: self.merge_values(scanmetadata.get(field), add_metadata_dict.get(field))
                         for field in set(scanmetadata).union(add_metadata_dict)}

        # Todo fix this
        scanmetadata["relation.isScanOfSlide"] = self.metadataarrayneutral([slideid])
        scanmetadata["scan.identifier"] = self.metadataarrayneutral([scanUUID])

        scan = {
            "name": scanUUID,
            "inArchive": True,
            "discoverable": True,
            "withdrawn": False,
            "type": "Scan",
            "metadata": scanmetadata
        }

        return scan

    def dummyWSI(self, add_metadata_dict, wsiUUID, root, folders, current_id):

        wsimetadata = {
            "dc.contributor.author": self.metadataarrayneutral(["Plass, Markus", "Müller, Heimo"]),
            "dc.title": self.metadataarrayneutral([wsiUUID]),
            "dc.type": self.metadataarrayneutral(["Wsi"]),
            "relationship.type": self.metadataarrayneutral(["Wsi"]),
            "relation.isWsiOfScan": self.metadataarrayneutral([scanid])
        }

        match = False
        for item in folders:
            if item == current_id:
                filepath_curr = os.path.join(root, item)
                match = True
                for file in os.listdir(filepath_curr):
                    if "wsi_meta" in file:
                        with open(os.path.join(filepath_curr, file), "r") as fp:
                            add_dict_phil = json.load(fp)
                            add_metadata_dict = {
                                field: self.merge_values_neut(add_metadata_dict.get(field), add_dict_phil.get(field))
                                for field in set(add_metadata_dict).union(add_dict_phil)}
                        #print(json.dumps(add_dict_phil, indent=4, sort_keys=True))
                        #print(json.dumps(add_metadata_dict, indent=4, sort_keys=True))

        wsimetadata = {field: self.merge_values(wsimetadata.get(field), add_metadata_dict.get(field))
                        for field in set(wsimetadata).union(add_metadata_dict)}

        wsi = {
            "name": wsiUUID,
            "inArchive": True,
            "discoverable": True,
            "withdrawn": False,
            "type": "Wsi",
            "metadata": wsimetadata
        }

        return wsi

    def dummyBundle(self, bundle_name):

        bundle = {
            "name": bundle_name,
            "metadata": {}
        }
        return bundle

    def dummyBitsteam(self, filepath):

        bitstream_metadata = {
            "dc.title": self.metadataarray([filepath.split("/")[-1]]),
            "dc.description": [
            {
                "value": "example file",
                "language": None,
                "authority": None,
                "confidence": -1,
            }]
        }

        bitstream = {
                "name": filepath.split("/")[-1],
                "metadata": bitstream_metadata
        }

        files = {
            'file': (filepath.split("/")[-1],
                     open(filepath, 'rb'))
        }

        return(files, bitstream)

if __name__ == "__main__":

    file_dir = "/home/simon/Documents/Arbeit_med_Uni/app-digital-repository-tests/histoqc_output_20200625-124747"
    runningEnv = 'localhost'

    if runningEnv == 'silicolab':
        params = {'user': 'v@bibbox.org', 'password': 'vendetta'}
        serverurlprefix  = 'http://dspace-rest.silicolab.bibbox.org'

        scan_coll_id = "dbc075f7-449f-499d-b45b-65f019ff05c2"
        slide_coll_id = "a4f79444-48e2-4a78-b3bc-e07c047a0230"
        wsi_collection_id = "a5e921fa-0295-4b79-867a-c4601b2a78c3"
        collections = [slide_coll_id, scan_coll_id, wsi_collection_id]

    if runningEnv == 'dspace':
        params = {'user': 'dspacedemo+admin@gmail.com', 'password': 'dspace'}
        serverurlprefix  = 'https://dspace7.4science.cloud'

    if runningEnv == 'localhost':
        params = {'user': 'test@test.edu', 'password': 'admin'}
        serverurlprefix = 'http://localhost:8080'

        scan_coll_id = "6184e732-4331-4091-8dde-5c67d11d1938"
        slide_coll_id = "b9616f72-0d08-4617-b30e-c49e73ce8a1a"
        wsi_collection_id = "4078eb23-7f26-4b45-9826-67a28c93b4b4"
        collections = [slide_coll_id, scan_coll_id, wsi_collection_id]

    r = requests.post(serverurlprefix + '/server/api/authn/login', params=params)
    h = {'Authorization': r.headers['Authorization']}


    mf = MetadataFields(serverurlprefix + '/server/api/', h)
    items = Items(serverurlprefix + '/server/api/', h)

    # collections = ["dbc075f7-449f-499d-b45b-65f019ff05c2",
    #                "a4f79444-48e2-4a78-b3bc-e07c047a0230", "a5e921fa-0295-4b79-867a-c4601b2a78c3"]

    RelIDSlide2Scan = items.relationshipsID("isSlideOfScan", "isScanOfSlide")
    RelIDScan2WSI = items.relationshipsID("isScanOfWsi", "isWsiOfScan")
    RelIDSlide2WSI = items.relationshipsID("isSlideOfWsi", "isWsiOfSlide")

    schemes = ["slide", "scan", "wsi"]

    field_keys = ["id", "element", "qualifier", "scopeNote", "type"]
    csv_header = ['Patient-ID', 'Case-ID', 'Block-ID', 'Slide-ID', 'Scan-ID', 'Barcode', 'Pfad', 'Staining', 'WSI-ID',
                  'MRXSID', 'DSPACE-URL']

    standart_values = ["80%", "jpg", "scanable", "cleaned", "Semi-Automated", "Layer", "Fakelman", "Colon", "8", "RGB",
                       "P1000", "DS", "FFPE", "ADOPT", "True", "MRXS", "Human", "Operational"]

    # replace and insert values for scan csv
    replace_csv = [["NA1", "slide.caseUUID", "NA2", "slide.identifier.uuidslide", "NA3",
                    'slide.identifier.label', "NA4", "slide.staining",
                    "NA5", "int_id", "NA11"],
                   ["NA1", "NA2", "NA3", "relation.isScanOfSlide", "scan.identifier", "NA4", "scan.file", "NA5", "NA6",
                    "int_id", "NA11"],
                   ["NA1", "NA2", "NA3", "NA4", "NA5", "NA6", "NA7", "NA8", "wsi.identifier", "int_id", "NA11"]]
    db_csv_fields = ["slide.source.sourcetags"]
    match_fields_metadata = ["Age"]
    same_val_fields = ['slide.label.normalized', 'slide.label.transcribed', 'slide.identifier.label']

    # print(items.get_item("b8500898-53a2-425c-bbe5-ace5b1d8adc0"))
    # print("test")
    # input()
    upload_time = time.time()
    delete_time = time.time()
    items_tot = 0
    ## Start Upload
    # Delete current items:
    for coll in collections:
        founditems = items.itemsInScope(coll)
        items_tot += len(founditems)
        for item in founditems:
            items.deleteItem(item['id'])
    delete_time_end = time.time()
    delete_time = (delete_time_end-delete_time)
    print("Total delete time {} s (API only)".format(delete_time))
    #print("Time per item {} s (N = {}".format(delete_time/items_tot, items_tot))
    parser = Parse_file("/home/simon/Documents/Arbeit_med_Uni/app-digital-repository-tests/ADOPT-Graz.xml",
                        "/home/simon/Documents/Arbeit_med_Uni/app-digital-repository-tests/CSV_Scans.csv",
                        "/home/simon/Documents/Arbeit_med_Uni/app-digital-repository-tests/db_export_new.csv")

    pandas_csv_scan, pandas_csv_db = parser.parse_csv()
    pandas_csv_scan_orig, pandas_csv_db_orig = parser.parse_csv()
    batch_size = 5
    i_lower = 0
    i_upper = i_lower + batch_size
    done = False
    ex_flag = False
    bundle_names = ["ORIGINAL"]
    scan_additional_fields = []
    phil_insert_keys = []
    metadata_dicts = [{}, {}, {}]
    IDCsvToDSpace = [{}, {}, {}]
    if i_lower != 0:
        for i, item in enumerate(IDCsvToDSpace):
            with open("IDS2DSPACE_{}.json".format(schemes[i]), "r") as fp:
                IDCsvToDSpace[i] = json.load(fp)

    missing_ids = []
    dict_templates = ["slidemetadata_dict.json", "scanmetadata_dict.json", "wsimetadata_dict.json"]

    for i, item in enumerate(metadata_dicts):
        with open(dict_templates[i], "r") as fp:
            metadata_dicts[i] = json.load(fp)

    root_file_tree = os.walk(file_dir)
    files = root_file_tree.__next__()
    root = files[0]
    folders = files[1]

    # start loop for update
    while i_upper < (pandas_csv_scan.shape[0]):
        if ex_flag:
            ex_flag = False
            print(i_lower)
            print(i_upper)
            input()
        for n, metadatadict in enumerate(metadata_dicts):

            fill_fields = []
            pandas_csv_scan.columns = replace_csv[n]

            for current_key in replace_csv[n]:
                if not "NA" in current_key:
                   fill_fields.append(current_key)

            for i in tqdm.tqdm(range(pandas_csv_scan.shape[0])):
                if i <= i_lower and i_lower != 0:
                    continue
                elif i > i_upper:
                    break

                print(i, "i")
                print(i_lower, "i_lower")
                print(n, 'n')

                if i % 100 == 0:
                    r = requests.post(serverurlprefix + '/server/api/authn/login', params=params)
                    h = {'Authorization': r.headers['Authorization']}
                    #time.sleep(0.1)
                for field in fill_fields:
                    if field in same_val_fields:
                        for same_val in same_val_fields:
                            metadatadict[same_val] = pandas_csv_scan[field][i]
                    elif field == "int_id":
                        current_id = pandas_csv_scan[field][i]
                    else:
                        metadatadict[field] = pandas_csv_scan[field][i]

                # add slide to DSpace
                try:
                    if n == 0:
                        for k in range(pandas_csv_db.shape[0]):
                            if pandas_csv_scan["NA1"][i] == pandas_csv_db["Patient-ID"][k]:
                                metadatadict["slide.source.sourcetags"] = str(pandas_csv_db["Age"][k])
                        UUIDslide = metadatadict["slide.identifier.uuidslide"]
                        slide = items.dummySlide(metadatadict, UUIDslide, root, folders, current_id)
                        # Todo add API calls for bundle and Bitsream meanwhile print the slide###
                        #print(json.dumps(slide[0], indent=4, sort_keys=True))
                        status, slideid = items.createItem(slide_coll_id, slide[0])
                        #time.sleep(0.1)
                        pandas_csv_scan_orig['DSPACE-URL'][i] = "http://dspace.silicolab.bibbox.org/items/" + slideid
                        bundle_names = ["ORIGINAL", "THUMBNAIL"]

                        for bundle in bundle_names:
                            status, bundle_id = items.createBundle(slideid, items.dummyBundle(bundle))
                            #time.sleep(0.1)
                            filepath_curr = os.path.join(root, current_id)
                            #time.sleep(0.1)
                            if os.path.exists(filepath_curr):
                                for image in os.listdir(filepath_curr):
                                    if bundle == "THUMBNAIL" and "macro_small" in image:
                                        image_path = os.path.join(filepath_curr, image)
                                        files, bitstream = items.dummyBitsteam(image_path)
                                        status, bitstream_id = items.createBitstream(bundle_id, files, bitstream)
                                        #time.sleep(0.1)
                                    elif ("label_small" in image or "macro_small" in image) and bundle == "ORIGINAL":
                                        image_path = os.path.join(filepath_curr, image)
                                        files, bitstream = items.dummyBitsteam(image_path)
                                        status, bitstream_id = items.createBitstream(bundle_id, files, bitstream)
                                        #time.sleep(0.1)
                            else:
                                missing_ids.append(current_id)
                        IDCsvToDSpace[n].update({i: {current_id: [slideid, UUIDslide]}})
                except requests.exceptions.ConnectionError:
                    print("==> ConnectionResetError")
                    ex_flag = True
                    break

                #add scan to Dspace
                try:
                    if n == 1:
                        for key in IDCsvToDSpace[n - 1][i].keys():
                            slideid = IDCsvToDSpace[n - 1][i][key][0]
                        scanUUID = metadatadict["scan.identifier"]
                        scan = items.dummyScan(slideid, metadatadict, scanUUID, root, folders, current_id)

                        # print(json.dumps(scan, indent=4, sort_keys=True))

                        # Todo add API calls for adding relation to Slide meanwhile print the scan ###
                        status, scanid = items.createItem(scan_coll_id, scan)
                        #time.sleep(0.1)

                        for bundle in bundle_names:
                            status, bundle_id = items.createBundle(scanid, items.dummyBundle(bundle))
                            filepath_curr = os.path.join(root, current_id)
                            #time.sleep(0.1)
                            if os.path.exists(filepath_curr):
                                for image in os.listdir(filepath_curr):
                                    if "mrxs_mask_use" in image or "thumbnail_small" in image:
                                        image_path = os.path.join(filepath_curr, image)
                                        files, bitstream = items.dummyBitsteam(image_path)
                                        status, bitstream_id = items.createBitstream(bundle_id, files, bitstream)
                                        #time.sleep(0.1)

                        if runningEnv == "silicolab":
                            items.createRelationship(RelIDSlide2Scan, slideid, scanid)
                        IDCsvToDSpace[n].update({i: {current_id: [scanid, scanUUID]}})

                except requests.exceptions.ConnectionError:
                    print("==> ConnectionResetError")
                    ex_flag = True
                    break
                #add wsi to dspace
                try:
                    if n == 2:
                        wsiUUID = metadatadict["wsi.identifier"]
                        for key in IDCsvToDSpace[n - 1][i].keys():
                            scanid = IDCsvToDSpace[n - 1][i][key][0]
                        for key in IDCsvToDSpace[n - 2][i].keys():
                            slideid = IDCsvToDSpace[n - 2][i][key][0]
                        wsi = items.dummyWSI(metadatadict, wsiUUID, root, folders, current_id)

                        # # Todo add API calls for adding item, bundle and Bitsream meanwhile print the wsi ###
                        status, wsiid = items.createItem(wsi_collection_id, wsi)
                        #time.sleep(0.1)
                        bundle_names = ["ORIGINAL", "THUMBNAIL"]

                        for bundle in bundle_names:
                            status, bundle_id = items.createBundle(wsiid, items.dummyBundle(bundle))
                            #time.sleep(0.1)
                            filepath_curr = os.path.join(root, current_id)
                            if os.path.exists(filepath_curr):
                                for image in os.listdir(filepath_curr):
                                    if "thumbnail_small" in image:
                                        image_path = os.path.join(filepath_curr, image)
                                        files, bitstream = items.dummyBitsteam(image_path)
                                        status, bitstream_id = items.createBitstream(bundle_id, files, bitstream)
                                        #time.sleep(0.1)
                        if runningEnv == "silicolab":
                            items.createRelationship(RelIDScan2WSI, scanid, wsiid)
                            items.createRelationship(RelIDSlide2WSI, slideid, wsiid)
                        IDCsvToDSpace[n].update({i: {current_id: [wsiid, wsiUUID]}})

                except requests.exceptions.ConnectionError:
                    print("==> ConnectionResetError")
                    ex_flag = True
                    break
            if ex_flag:
                break
        if not ex_flag:
            pandas_csv_scan_orig.to_csv('scans_csv_update_{}.csv'.format(runningEnv), index=False, encoding='utf-8')
            with open("missin_internal_ids.json", "w") as fp:
                json.dump(missing_ids, fp)

            for i, item in enumerate(IDCsvToDSpace):
                print(item)
                with open("IDS2DSPACE_{}_{}.json".format(schemes[i], runningEnv), "w") as fp:
                    json.dump(IDCsvToDSpace[i], fp)

            i_lower = i_upper
            i_upper += batch_size
            if done:
                i_upper = pandas_csv_scan.shape[0]
            elif i_upper > pandas_csv_scan.shape[0] - 1:
                i_upper = pandas_csv_scan.shape[0] - 1
                print(i)
                done = True

    upload_time = time.time() - upload_time
    print("Total upload time {}s".format(upload_time))
    print("Program terminated successfully")

## graveyard

    # old parsing
    # for n, schema in enumerate(schemes):
    #
    #     dict_curr = metadata_dicts[n]
    #     with open(schema + ".txt", "r") as fp:
    #         for line in fp.readlines():
    #             # print(line.strip("\n"))
    #             # print(line.strip("\n").split(" ")[0])
    #             # print(line.strip("\n").split(" ")[-1])
    #             if line.strip("\n").split(" ")[0] in replace_csv[n]:
    #                 pass
    #                 # check whats happening here: answer is nothing
    #             elif line.strip("\n").split(" ")[-1] in standart_values:
    #                 # print(line.strip("\n").split(" ")[0])
    #                 # print(line.strip("\n").split(" ")[-1])
    #                 if line.strip("\n").split(" ")[-1] == "Layer" or line.strip("\n").split(" ")[-1] == "Fakelman" or \
    #                     line.strip("\n").split(" ")[-1] == "P1000":
    #                     insert_val = line.strip("\n").split(" ")[-2] + " " +  line.strip("\n").split(" ")[-1]
    #                     dict_curr.update({line.strip("\n").split(" ")[0]: insert_val})
    #                 else:
    #                     dict_curr.update({line.strip("\n").split(" ")[0]:line.strip("\n").split(" ")[-1]})
    #             # because values are added here anyways
    #             elif not line.strip("\n").split(" ")[-1].lower() == "leer":
    #                 phil_insert_keys.append(line.strip("\n").split(" ")[0])
    #
    #     metadatafields = mf.metadataFieldsForSchema(schema)
    #
    #     # print(json.dumps(metadatafields, indent=4, sort_keys=True))
    #
    #     for field in metadatafields:
    #         metadata_key = schema + "."
    #         for i, key in enumerate(field.keys()):
    #             if i == 1 and not (field[key] is None):
    #                 metadata_key += (field[key])
    #             elif i == 2 and not (field[key] is None):
    #                 metadata_key += ("." + field[key])
    #         if not dict_curr.get(metadata_key, False):
    #             dict_curr.update({metadata_key: None})
    #
    #     if save:
    #         with open(schema + "metadata_dict.json", "w") as fp:
    #             json.dump(dict_curr, fp)
