import requests
import json
import pandas as pd
from IPython.display import display
import pyodbc

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

data = {'city_name': [parse_data['name']],
        'country': [parse_data['country']],
        'latitude': [parse_data['lat']],
        'longitude': [parse_data['lon']],
        'population': [parse_data['population']],
        'timezone': [parse_data['timezone']]}

df1 = pd.DataFrame(data)
# print dataframe.
display(df1)
data_top = df1.head()
print(list(data_top.index))



print("name:" , i_name)

print("Co-ordinates:" ,"\n", i_cor1 , i_cor2)
rad_city = input("Enter the radius from the city co-ordinates in metres ")
radius_payload = {'radius': rad_city, 'lon' : i_cor2, 'lat': i_cor1, 'apikey' :'5ae2e3f221c38a28845f05b6540ea8483e4f4f34b2f64545966718a3'}
t_radius_res = requests.get("https://api.opentripmap.com/0.1/en/places/radius?", params = radius_payload)
radius_res = t_radius_res.text

listObj = []

parse_radius = json.loads(radius_res)
pre_parse_radius = json.dumps(parse_radius, indent = 2)
for fea in parse_radius['features']:
  listObj.append({
      "city": in_city,
  "id": fea['id'],
  "coordinates": fea['geometry']['coordinates'],
  "name": fea['properties']['name'],
  "distance": fea['properties']['dist'],
  "type": fea['properties']['kinds']
  })

#generates JSON file
json_pdata = json.dumps(listObj, indent=4)
with open("city_locations.json", "w") as outfile:
  outfile.write(json_pdata)

df = pd.read_json('city_locations.json')
#display(df)
#print(type(df))

cnxn = pyodbc.connect('DRIVER={Devart ODBC Driver for PostgreSQL};Server=localhost;Port=5432;Database=postgres;User ID=postgres;Password=D@niel123;String Types=Unicode')
cursor = cnxn.cursor()
#cursor.execute("ALTER TABLE city_details ALTER COLUMN latitude TYPE NUMERIC(14,11)")
#cursor.execute("ALTER TABLE city_details ALTER COLUMN longitude TYPE NUMERIC(14,11)")

for index,r1 in df1.iterrows():
    cursor.execute("INSERT INTO city_details(city_name,country,latitude,longitude,population,timezone) VALUES (?,?,?,?,?,?)", r1['city_name'],r1['country'],r1['latitude'],r1['longitude'],r1['population'],r1['timezone'])
cursor.execute("SELECT * FROM city_details")
row = cursor.fetchone()
while row:
    print (row)
    row = cursor.fetchone()

for index,r2 in df.iterrows():
    cursor.execute("INSERT INTO location_details(city_name,location_name,location_type,distance) VALUES (?,?,?,?)", r2['city'],r2['name'],r2['type'],r2['distance'])

print("City \t Location name \t Location_type \t Distance in Metres")
cursor.execute("SELECT * FROM location_details")
row1 = cursor.fetchone()
while row1:
    print(row1)
    row1 = cursor.fetchone()

cnxn.close()

