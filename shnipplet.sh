curl -v -X POST http://dspace-rest.silicolab.bibbox.org/server/api/authn/login --data "user=v@bibbox.org&password=vendetta"

curl -v http://dspace-rest.silicolab.bibbox.org/server/api/core/items -H "Authorization: Bearer Bearer eyJhbGciOiJIUzI1NiJ9.eyJlaWQiOiI5MjFiZWVmNy1iMDZkLTQzMjAtYWQ4NC1kNTlkOTUxYzc0MWQiLCJzZyI6W10sImV4cCI6MTU4ODA4MDc2M30.e8dvJDTOt7u_3dUcPXHCC8IqKy3RkOnOSGum-GfCpO8"

curl -v http://dspace-rest.silicolab.bibbox.org/server/api/core/items/21421937-7af1-45d8-bdbe-2f66c0ade7ea -H "Authorization: Bearer Bearer eyJhbGciOiJIUzI1NiJ9.eyJlaWQiOiI5MjFiZWVmNy1iMDZkLTQzMjAtYWQ4NC1kNTlkOTUxYzc0MWQiLCJzZyI6W10sImV4cCI6MTU4ODA4MDc2M30.e8dvJDTOt7u_3dUcPXHCC8IqKy3RkOnOSGum-GfCpO8"

curl -v -X DELETE http://dspace-rest.silicolab.bibbox.org/server/api/core/items/21421937-7af1-45d8-bdbe-2f66c0ade7ea -H "Authorization: Bearer Bearer eyJhbGciOiJIUzI1NiJ9.eyJlaWQiOiI5MjFiZWVmNy1iMDZkLTQzMjAtYWQ4NC1kNTlkOTUxYzc0MWQiLCJzZyI6W10sImV4cCI6MTU4ODA4MDc2M30.e8dvJDTOt7u_3dUcPXHCC8IqKy3RkOnOSGum-GfCpO8"
