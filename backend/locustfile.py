"""
Tests de Performance - Locust
Plateforme Crypto Market Analytics
Évalue la scalabilité et la latence du système
"""

from locust import HttpUser, task, between, TaskSet
from random import choice, randint
import time

# ================================================================
# CONSTANTES
# ================================================================

API_BASE_URL = "http://localhost:8000"

ASSETS = ["bitcoin", "ethereum", "cardano", "ripple"]
VALID_EMAILS = [f"user{i}@test.com" for i in range(1, 101)]


# ================================================================
# USER BEHAVIORS - SCÉNARIOS DE CHARGE
# ================================================================

class PublicEndpointBehavior(TaskSet):
    """Comportement utilisateur visitant les endpoints publics"""
    
    @task(3)
    def get_health(self):
        """Vérifier la santé de l'API"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(2)
    def list_assets(self):
        """Lister tous les assets"""
        with self.client.get("/assets", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Assets listing failed: {response.status_code}")
    
    @task(5)
    def get_asset_prices(self):
        """Récupérer les prix d'un asset"""
        asset = choice(ASSETS)
        with self.client.get(f"/assets/{asset}/prices", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Price retrieval failed: {response.status_code}")
    
    @task(4)
    def get_asset_indicators(self):
        """Récupérer les indicateurs d'un asset"""
        asset = choice(ASSETS)
        with self.client.get(f"/assets/{asset}/indicators", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Indicators retrieval failed: {response.status_code}")


class AuthenticationBehavior(TaskSet):
    """Comportement utilisateur s'authentifiant"""
    
    @task(1)
    def register_user(self):
        """Enregistrer un nouvel utilisateur"""
        email = f"perf_test_{randint(1, 100000)}@test.com"
        payload = {
            "email": email,
            "password": "TestPassword123!"
        }
        with self.client.post("/auth/register", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400:  # Email already exists
                response.success()
            else:
                response.failure(f"Registration failed: {response.status_code}")
    
    @task(2)
    def login_user(self):
        """Connexion utilisateur"""
        email = choice(VALID_EMAILS)
        payload = {
            "username": email,
            "password": "TestPassword123!"
        }
        with self.client.post("/auth/login", data=payload, catch_response=True) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")


class CombinedBehavior(TaskSet):
    """Comportement utilisateur normal : navigation + auth"""
    
    @task(10)
    def public_pages(self):
        """Consulter les pages publiques"""
        endpoints = [
            "/health",
            "/assets",
            f"/assets/{choice(ASSETS)}/prices",
            f"/assets/{choice(ASSETS)}/indicators"
        ]
        endpoint = choice(endpoints)
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Request failed: {response.status_code}")
    
    @task(1)
    def auth_flow(self):
        """Effectuer l'authentification"""
        # Enregistrement
        email = f"user_{int(time.time() * 1000)}@test.com"
        register_payload = {"email": email, "password": "Test123!"}
        
        with self.client.post("/auth/register", json=register_payload, catch_response=True) as response:
            if response.status_code == 200:
                # Connexion
                login_payload = {"username": email, "password": "Test123!"}
                with self.client.post("/auth/login", data=login_payload, catch_response=True) as login_response:
                    if login_response.status_code == 200:
                        login_response.success()


# ================================================================
# LOCUST USER CLASSES
# ================================================================

class PublicUser(HttpUser):
    """Utilisateur naviguant sur les endpoints publics"""
    tasks = [PublicEndpointBehavior]
    wait_time = between(1, 3)
    host = API_BASE_URL


class AuthUser(HttpUser):
    """Utilisateur s'authentifiant"""
    tasks = [AuthenticationBehavior]
    wait_time = between(2, 5)
    host = API_BASE_URL


class NormalUser(HttpUser):
    """Utilisateur normal : mélange public + auth"""
    tasks = [CombinedBehavior]
    wait_time = between(1, 4)
    host = API_BASE_URL
    weight = 2  # Plus de utilisateurs "normaux" que les autres


# ================================================================
# CONFIGURATION ADDITIONNELLE
# ================================================================

class StressTestUser(HttpUser):
    """Utilisateur pour stress test (requêtes rapides)"""
    
    @task
    def stress_health(self):
        """Requête santé très rapide"""
        self.client.get("/health")
    
    wait_time = between(0.5, 1)  # Très court
    host = API_BASE_URL
