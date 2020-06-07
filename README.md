# Digital Repositories Tests

Collection of python script to test and evaluate tools to build TDR, Trusted Digital Repositories


## generate a local environment and install packages

* `python3 -m venv localenv`
* `source localenv/bin/activate`
* `pip install -r requirements.txt`
* `pip freeze > requirements.txt`

## Dspace 7 Test environment

### setup of dspace with docker on silicolab server

* [latest instruction how to setup dSpace 7 with docker](https://wiki.lyrasis.org/display/DSPACE/Try+out+DSpace+7#TryoutDSpace7-InstallviaDocker)


* install steps
    * `git clone https://github.com/human-centered-ai-lab/dspace-angular`
    * `cd dspace-angular`
    * `docker-compose -f docker/docker-compose.yml pull`
    * `docker-compose -p d7 -f docker/docker-compose.yml -f docker/docker-compose-rest.yml up -d`
    * `docker-compose -p d7 -f docker/docker-compose.yml -f docker/docker-compose-rest.yml down`
    * `docker volume rm d7_assetstore d7_pgdata  d7_solr_authority d7_solr_oai  d7_solr_search  d7_solr_statistics`

* load entities
    * `docker-compose -p d7 -f docker/docker-compose.yml -f docker/docker-compose-rest.yml -f docker/db.entities.yml up -d`
    * `docker-compose -p d7 -f docker/cli.yml -f docker/cli.assetstore.yml run --rm dspace-cli`

* make admin user
    * `docker-compose -p d7 -f docker/cli.yml run --rm dspace-cli create-administrator -e v@bibbox.org -f admin -l user -p vendetta -c en`

* restart 
    * `docker-compose -p d7 -f docker/docker-compose.yml -f docker/docker-compose-rest.yml -f docker/db.entities.yml up -d`
    * `docker-compose -p d7 -f docker/docker-compose.yml -f docker/docker-compose-rest.yml up -d`

* dump DB
    * `docker exec -t dspacedb pg_dumpall -c -U dspace  > db.sql`



