import requests


class Router:
    def __init__(self):
        self.base_url = "http://localhost:8080/ors/v2/isochrones/driving-car"


    def get_isochrone(self, lat, lon, time_limit=10):
        time_seconds = [time_limit * 60]

        headers = {
            "Accept": "application/geo+json;charset=UTF-8",
            "Content-Type": "application/json; charset=utf-8",
        }

        body = {
            "locations": [[lon, lat]],  # ORS = [Longitude, Latitude]
            "range": time_seconds,
            "range_type": "time",
        }

        try:
            response = requests.post(self.base_url, json=body, headers=headers)

            if response.status_code != 200:
                print(f"Full Error Response: {response.text}")

            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Local ORS request failed: {e}")
