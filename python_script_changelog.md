- use Session object (requests.Session()) to store and automatically send information ([XSRF Token](https://github.com/DSpace/RestContract/blob/main/csrf-tokens.md), Authentication)
    - session object replaces requests.get/post/... for all REST calls 

- introduce xsrf_token_check method to check for changed [xsrf tokens](https://github.com/DSpace/RestContract/blob/main/csrf-tokens.md) in the response header 

- [login](https://github.com/DSpace/RestContract/blob/main/authentication.md#Login) method now accounts for xsrf token 

- metadata field "relationship.type" has been [replaced](https://github.com/DSpace/DSpace/pull/3183) by "dspace.entity.type"  in DSpace 7


changes have been tested on a local machine running [dspace-angular](https://github.com/DSpace/dspace-angular) docker container
