import pymongo
import requests
import json

# connect to the MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/?directConnection=true")
# create a new database
db = client["grp3database"]

# create a new collection
col = db["traveldata"]

#print(client.list_database_names())


#code to get the co-ordinates of a place
in_city = input("Enter the name of the city ")
print(in_city)
#inputting URL parameters through dictionary
payload = {'name': in_city, 'apikey' : '5ae2e3f221c38a28845f05b6540ea8483e4f4f34b2f64545966718a3'}
#passing the parameters
res = requests.get("https://api.opentripmap.com/0.1/en/places/geoname?", params = payload)
#printing success code
print(res.status_code)
d_API = res.text
#print(d_API)
d_API_json_l = json.loads(d_API)

parse_data = json.loads(d_API)

i_name = parse_data['name']
i_country = parse_data['country']
i_cor1 = parse_data['lat']
i_cor2 = parse_data['lon']
i_pop = parse_data['population']
i_timezone = parse_data['timezone']

tr_data = {"city_name": parse_data['name'],
        "country": parse_data['country'],
        "latitude": parse_data['lat'],
        "longitude":parse_data['lon'],
        "population": parse_data['population'],
        "timezone": parse_data['timezone']}

mydoc = col.insert_one(tr_data)

for a in col.find():
    print(a)

rad_city = input("Enter the radius from the city co-ordinates in metres ")
radius_payload = {'radius': rad_city, 'lon' : i_cor2, 'lat': i_cor1, 'apikey' :'5ae2e3f221c38a28845f05b6540ea8483e4f4f34b2f64545966718a3'}
t_radius_res = requests.get("https://api.opentripmap.com/0.1/en/places/radius?", params = radius_payload)
radius_res = t_radius_res.text
print(type(t_radius_res))
parse_radius = json.loads(radius_res)

pre_parse_radius = json.dumps(parse_radius, indent = 2)

listObj = []

for fea in parse_radius['features']:
    listObj.append({
        "city":in_city,
       "id": fea['id'],
       "coordinates": fea['geometry']['coordinates'],
       "name": fea['properties']['name'],
       "distance from city centre in metres": fea['properties']['dist'],
       "type": fea['properties']['kinds']
    })

json_pdata = json.dumps(listObj, indent=4)
with open("city_locations_mongo.json", "w") as outfile:
    outfile.write(json_pdata)

file_data = []
col2 = db["city_locations"]
with open('city_locations_mongo.json') as file:
    file_data = json.load(file)

#print(file_data)
y = col2.insert_many(file_data)
for b in col2.find():
   print(b)


mydoc = col2.find().sort("type")

myquery = { "name": '' }
col2.delete_many(myquery)

for k in mydoc:
    print(k)

myquery = { "type": { "$gt": "o" } }

mydoc1 = col2.find(myquery)

for l in mydoc1:
    print(l)
