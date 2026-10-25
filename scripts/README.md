# ParkAPIv3 Push Script

In order to test push tasks or to upload files you got per e-mail, there is an upload script included in this
repository. It requires python requests, so either, you have that installed at your system, or you run the script with
[uv](https://docs.astral.sh/uv/), which handles the virtual environment for you:

```bash
cd scripts
uv run --with "requests~=2.32.3" push-client.py source_uid some/file.csv
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
