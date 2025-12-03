# geoconnex-mainstem-lookup

A simple web server for returning the associated Geoconnex mainstem given a point in EPSG:4326 CRS

_Example:_
```
curl "http://127.0.0.1:8000?lon=-108.50231860661755&lat=39.05108882481538"

{"mainstem_id":29559,"mainstem_url":"https://reference.geoconnex.us/collections/mainstems/items/29559"}
```