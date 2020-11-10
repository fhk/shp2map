# SHP2Map

Send a ZIP containing SHP files and get a map

## Howto

```
# create a new env

pip install -r requirements.txt

python application.py &

curl -X POST -F "file=@test_data/Airports.zip" -F api_key=super-secret-api-key -X POST localhost:5000/v1/shp2map -o test.html
```

