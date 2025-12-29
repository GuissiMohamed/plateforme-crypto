from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(0.2, 1.0)

    @task(3)
    def health(self):
        self.client.get("/health")

    @task(2)
    def assets(self):
        self.client.get("/assets?limit=50")

    @task(1)
    def indicators(self):
        # un asset "bitcoin" existe généralement si collector tourne
        self.client.get("/assets/bitcoin/indicators")
