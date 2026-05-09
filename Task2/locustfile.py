from locust import HttpUser, between, task, constant_pacing

class WebsiteUser(HttpUser):
    #wait_time = between(1, 5)
    wait_time = constant_pacing(0.05)  # запрос каждые 50 мс
    
    @task
    def index(self):
        self.client.get("/")