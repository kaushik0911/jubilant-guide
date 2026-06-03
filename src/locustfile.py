import random

from locust import HttpUser, between, task


class RoadblockSimulationUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_roadblock(self):
        random_lat = random.uniform(-90.0, 90.0)
        random_long = random.uniform(-180.0, 180.0)
        random_status = random.choice(["blocked", "partially-blocked", "open"])

        payload = {"lat": random_lat, "long": random_long, "status": random_status}

        self.client.post("/blocker/create", json=payload, name="/blocker/create")
