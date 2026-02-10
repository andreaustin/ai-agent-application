import requests

base_url = "https://serpapi.com/search.json?engine=google_flights"
departure_id = "&departure_id=LGA,JFK,EWR"
arrival_id = "&arrival_id=AUS"
currency = "&currency=USD"
flight_type = "&type=2" 
outbound = f"&outbound_date=2026-03-03"

url = f"{base_url}{departure_id}{arrival_id}{currency}{flight_type}{outbound}"

# if return_date:
#     returning = f"&return_date={return_date}"
#     url += returning
url += f"&api_key=d62231893de7d99101a146a8983ef6e147e617698ee096b5d78ab698963a188a"
response = requests.get(url)
if response.status_code != 200:
    print(f"Error fetching flight data: {response.status_code}\n{response.text}")
results = response.json()
best_flights = results["best_flights"]
print(best_flights)