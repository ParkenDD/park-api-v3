# ParkAPIv3 Push Client

In order to test push tasks or to upload files you got per e-mail, there is an upload script included in this
repository. It requires python requests, so either, you have that installed at your system, or you create a virtual 
environment for that:

```
cd push-client
virtalenv venv
pip install "requests~=2.31.0"
source venv/bin/activate
python push-client.py
```

If you have requests, you can run the script with two arguments:
- the source uid which should be registered as user at `config.yaml` and should have a representation at ParkAPI-sources
- the path to the file to push

Afterward, the password will be asked in a secure way, then the upload progress begins.

### curl equivalent

As the push client just does HTTP request, you can replace it with curl if you prefer. This command would push an XML
file:

```bash
curl -XPOST \
  -u user:password \
  -d @data.xml \
  --header "Content-Type: application/xml" \
  https://api.mobidata-bw.de/park-api/api/admin/v1/generic-parking-sites/xml
```
