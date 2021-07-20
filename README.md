# Digital Repositories Tests

Collection of python script to test and evaluate tools to build a TDR (Trusted Digital Repository)


## generate a local environment and install packages

* `python3 -m venv localenv`
* `source localenv/bin/activate`
* `pip install -r requirements.txt`
* `pip freeze > requirements.txt`

## DSpace 7 Test Environment

### Setup of DSpace using docker 

Follow the [latest instructions] (https://wiki.lyrasis.org/display/DSPACE/Try+out+DSpace+7#TryoutDSpace7-InstallviaDocker) on how to install dSpace 7 via docker
Alternatively:
	
* Install steps
    * `git clone https://github.com/human-centered-ai-lab/dspace-angular`
    * `cd dspace-angular`
    * `docker-compose -f docker/docker-compose.yml pull`
    * `docker-compose -f docker/docker-compose.yml -f docker/docker-compose-rest.yml up -d`
    * `docker-compose -f docker/docker-compose.yml -f docker/docker-compose-rest.yml down`
    * `docker volume rm d7_assetstore d7_pgdata  d7_solr_authority d7_solr_oai  d7_solr_search  d7_solr_statistics`

* load entities
    * `docker-compose -f docker/docker-compose.yml -f docker/docker-compose-rest.yml -f docker/db.entities.yml up -d`
    * `docker-compose -f docker/cli.yml -f docker/cli.assetstore.yml run --rm dspace-cli`

* make admin user
    * `docker-compose -f docker/cli.yml run --rm dspace-cli create-administrator -e v@bibbox.org -f admin -l user -p vendetta -c en`

* restart 
    * `docker-compose -f docker/docker-compose.yml -f docker/docker-compose-rest.yml -f docker/db.entities.yml up -d`
    * `docker-compose -f docker/docker-compose.yml -f docker/docker-compose-rest.yml up -d`

* dump DB
    * `docker exec -t dspacedb pg_dumpall -c -U dspace  > db.sql`

### Setup Test Environment 	
*In order to use the python scrips 'as is', [add relationship types] (https://wiki.bibbox.org/index.php/DSpace) for digital pathology

    * docker cp digital_pathology/relationship-types.xml dspace:/dspace/config/entities/relationship-types.xml
    * docker exec -it dspace /bin/sh
    * apt-get update
    * apt-get install nano
    * nano  /dspace/config/entities/relationship-types.xml
    * /dspace/bin/dspace dsrun org.dspace.app.util.InitializeEntities -f /dspace/config/entities/relationship-types.xml

* Add metadata fields by running "dspace-metadata-rest-experiments.py"

* Add dummy items by running "dspace-items.rest.experiments.py" 



