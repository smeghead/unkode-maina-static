# unkode-maina-static

convert to static html site from https://unkode-mania.net/


## Development

```bash
docker compose build
docker compose run --rm app bash
python3 -m pip install beautifulsoup4
```

### Dev WebServer

```bash
scripts/start_dev_server.sh
```
and open `http://localhost:8000/`