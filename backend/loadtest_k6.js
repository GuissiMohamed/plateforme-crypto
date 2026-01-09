/**
 * k6 load test script — Plateforme Crypto
 * Single, clean copy to avoid duplicated imports or blocks.
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Rate, Trend, Counter, Gauge } from "k6/metrics";

export const options = {
  scenarios: {
    ramping_load: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "5m", target: 50 },
        { duration: "10m", target: 100 },
        { duration: "5m", target: 200 },
        { duration: "5m", target: 100 },
        { duration: "5m", target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1000"],
    http_req_failed: ["rate<0.1"],
    http_reqs: ["rate>100"],
  },
};

const apiDuration = new Trend("api_duration");
const healthCheckSuccess = new Rate("health_check_success");
const assetListingSuccess = new Rate("asset_listing_success");
const priceRetrievalSuccess = new Rate("price_retrieval_success");
const indicatorSuccess = new Rate("indicator_success");
const authSuccess = new Rate("auth_success");
const errorCount = new Counter("errors");
const activeUsers = new Gauge("active_users");

const BASE_URL = "http://localhost:8000";
const ASSETS = ["bitcoin", "ethereum", "cardano", "ripple"];

function randomAsset() {
  return ASSETS[Math.floor(Math.random() * ASSETS.length)];
}

function randomEmail() {
  return `user_${Math.floor(Math.random() * 100000)}@test.com`;
}

export default function () {
  activeUsers.add(1);

  group("Health Check", function () {
    const res = http.get(`${BASE_URL}/health`);
    healthCheckSuccess.add(res.status === 200);
    apiDuration.add(res.timings.duration);
    check(res, { "status is 200": (r) => r.status === 200 });
  });

  sleep(1);

  group("Asset Listing", function () {
    const res = http.get(`${BASE_URL}/assets`);
    assetListingSuccess.add(res.status === 200);
    apiDuration.add(res.timings.duration);
    check(res, { "status is 200": (r) => r.status === 200 });
  });

  sleep(1);

  group("Price Retrieval", function () {
    const asset = randomAsset();
    const res = http.get(`${BASE_URL}/assets/${asset}/prices`);
    priceRetrievalSuccess.add([200, 404].includes(res.status));
    apiDuration.add(res.timings.duration);
    check(res, { "status is 200 or 404": (r) => [200, 404].includes(r.status) });
  });

  sleep(1);

  group("Indicators", function () {
    const asset = randomAsset();
    const res = http.get(`${BASE_URL}/assets/${asset}/indicators`);
    indicatorSuccess.add([200, 404].includes(res.status));
    apiDuration.add(res.timings.duration);
    check(res, { "status is 200 or 404": (r) => [200, 404].includes(r.status) });
  });

  sleep(1);

  group("Authentication Flow", function () {
    const email = randomEmail();
    const password = "TestPassword123!";
    const register = http.post(`${BASE_URL}/auth/register`, JSON.stringify({ email, password }), {
      headers: { "Content-Type": "application/json" },
    });
    authSuccess.add([200, 400].includes(register.status));

    const loginPayload = `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`;
    const login = http.post(`${BASE_URL}/auth/login`, loginPayload, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    authSuccess.add([200, 401].includes(login.status));
    check(login, { "response time < 500ms": (r) => r.timings.duration < 500 });
  });

  sleep(2);
  activeUsers.add(-1);
}

export function setup() {
  console.log("Starting performance test...");
  return { startTime: new Date() };
}

export function teardown(data) {
  const endTime = new Date();
  const duration = (endTime - new Date(data.startTime)) / 1000;
  console.log(`Test completed in ${duration} seconds`);
}

/*
Stress scenario example:
k6 run --scenario stress_test loadtest_k6.js

export const stressTest = {
  executor: 'constant-arrival-rate',
  rate: 100,
  timeUnit: '1s',
  duration: '5m',
  preAllocatedVUs: 50,
  maxVUs: 200,
};
*/
// Tests de Performance - k6
// Plateforme Crypto Market Analytics

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';

export const options = {
  scenarios: {
    ramping_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '5m', target: 50 },
        { duration: '10m', target: 100 },
        { duration: '5m', target: 200 },
        { duration: '5m', target: 100 },
        { duration: '5m', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.1'],
    http_reqs: ['rate>100'],
  },
};

// Custom metrics
const apiDuration = new Trend('api_duration');
const healthCheckSuccess = new Rate('health_check_success');
const assetListingSuccess = new Rate('asset_listing_success');
const priceRetrievalSuccess = new Rate('price_retrieval_success');
const indicatorSuccess = new Rate('indicator_success');
const authSuccess = new Rate('auth_success');
const errorCount = new Counter('errors');
const activeUsers = new Gauge('active_users');

const BASE_URL = 'http://localhost:8000';
const ASSETS = ['bitcoin', 'ethereum', 'cardano', 'ripple'];

function randomAsset() {
  return ASSETS[Math.floor(Math.random() * ASSETS.length)];
}

function randomEmail() {
  return `user_${Math.floor(Math.random() * 100000)}@test.com`;
}

export default function () {
  activeUsers.add(1);

  group('Health Check', function () {
    const res = http.get(`${BASE_URL}/health`);
    healthCheckSuccess.add(res.status === 200);
    apiDuration.add(res.timings.duration);
    check(res, { 'status is 200': (r) => r.status === 200 });
  });

  sleep(1);

  group('Asset Listing', function () {
    const res = http.get(`${BASE_URL}/assets`);
    assetListingSuccess.add(res.status === 200);
    apiDuration.add(res.timings.duration);
    check(res, { 'status is 200': (r) => r.status === 200 });
  });

  sleep(1);

  group('Price Retrieval', function () {
    const asset = randomAsset();
    const res = http.get(`${BASE_URL}/assets/${asset}/prices`);
    priceRetrievalSuccess.add([200, 404].includes(res.status));
    apiDuration.add(res.timings.duration);
    check(res, { 'status is 200 or 404': (r) => [200, 404].includes(r.status) });
  });

  sleep(1);

  group('Indicators', function () {
    const asset = randomAsset();
    const res = http.get(`${BASE_URL}/assets/${asset}/indicators`);
    indicatorSuccess.add([200, 404].includes(res.status));
    apiDuration.add(res.timings.duration);
    check(res, { 'status is 200 or 404': (r) => [200, 404].includes(r.status) });
  });

  sleep(1);

  group('Authentication Flow', function () {
    const email = randomEmail();
    const password = 'TestPassword123!';
    const register = http.post(`${BASE_URL}/auth/register`, JSON.stringify({ email, password }), {
      headers: { 'Content-Type': 'application/json' },
    });
    authSuccess.add([200, 400].includes(register.status));

    const loginPayload = `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`;
    const login = http.post(`${BASE_URL}/auth/login`, loginPayload, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    authSuccess.add([200, 401].includes(login.status));
    check(login, { 'response time < 500ms': (r) => r.timings.duration < 500 });
  });

  sleep(2);
  activeUsers.add(-1);
}

export function setup() {
  console.log('Starting performance test...');
  return { startTime: new Date() };
}

export function teardown(data) {
  const endTime = new Date();
  const duration = (endTime - new Date(data.startTime)) / 1000;
  console.log(`Test completed in ${duration} seconds`);
}

/*
Stress scenario example:
k6 run --scenario stress_test loadtest_k6.js

export const stressTest = {
  executor: 'constant-arrival-rate',
  rate: 100,
  timeUnit: '1s',
  duration: '5m',
  preAllocatedVUs: 50,
  maxVUs: 200,
};
*/
/**
 * Tests de Performance - k6
 * Plateforme Crypto Market Analytics
 * Évalue la scalabilité, latence et débit du système
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Rate, Trend, Counter, Gauge } from "k6/metrics";

// ================================================================
// CONFIGURATION
// ================================================================

export const options = {
  // Scénario 1 : Test de charge progressif
  scenarios: {
    ramping_load: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "5m", target: 50 },
        { duration: "10m", target: 100 },
        { duration: "5m", target: 200 },
        { duration: "5m", target: 100 },
        { duration: "5m", target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1000"],
    http_req_failed: ["rate<0.1"],
    http_reqs: ["rate>100"],
  },
};

// ================================================================
// MÉTRIQUES PERSONNALISÉES
// ================================================================

const apiDuration = new Trend("api_duration");
const healthCheckSuccess = new Rate("health_check_success");
const assetListingSuccess = new Rate("asset_listing_success");
const priceRetrievalSuccess = new Rate("price_retrieval_success");
const indicatorSuccess = new Rate("indicator_success");
const authSuccess = new Rate("auth_success");
const errorCount = new Counter("errors");
const activeUsers = new Gauge("active_users");

// ================================================================
// DONNÉES DE TEST
// ================================================================

const BASE_URL = "http://localhost:8000";
const ASSETS = ["bitcoin", "ethereum", "cardano", "ripple"];

function randomAsset() {
  return ASSETS[Math.floor(Math.random() * ASSETS.length)];
}

function randomEmail() {
  return `user_${Math.floor(Math.random() * 100000)}@test.com`;
}

// ================================================================
// SCÉNARIOS DE TEST
// ================================================================

export default function () {
  activeUsers.add(1);

  group("Health Check", function () {
    let response = http.get(`${BASE_URL}/health`);
    healthCheckSuccess.add(response.status === 200);
    apiDuration.add(response.timings.duration);

    check(response, {
      "status is 200": (r) => r.status === 200,
      "response time < 100ms": (r) => r.timings.duration < 100,
    });
  });

  sleep(1);

  group("Asset Listing", function () {
    let response = http.get(`${BASE_URL}/assets`);
    assetListingSuccess.add(response.status === 200);
    apiDuration.add(response.timings.duration);

    check(response, {
      "status is 200": (r) => r.status === 200,
      "has assets": (r) => r.body.includes("bitcoin") || r.body.length > 0,
      "response time < 300ms": (r) => r.timings.duration < 300,
    });
  });

  sleep(1);

  group("Price Retrieval", function () {
    const asset = randomAsset();
    let response = http.get(`${BASE_URL}/assets/${asset}/prices`);
    priceRetrievalSuccess.add([200, 404].includes(response.status));
    apiDuration.add(response.timings.duration);

    check(response, {
      "status is 200 or 404": (r) => [200, 404].includes(r.status),
      "response time < 400ms": (r) => r.timings.duration < 400,
    });
  });

  sleep(1);

  group("Indicators", function () {
    const asset = randomAsset();
    let response = http.get(`${BASE_URL}/assets/${asset}/indicators`);
    indicatorSuccess.add([200, 404].includes(response.status));
    apiDuration.add(response.timings.duration);

    check(response, {
      "status is 200 or 404": (r) => [200, 404].includes(r.status),
      "response time < 500ms": (r) => r.timings.duration < 500,
    });
  });

  sleep(1);

  group("Authentication Flow", function () {
    const email = randomEmail();
    const password = "TestPassword123!";

    let registerPayload = JSON.stringify({ email: email, password: password });
    let registerResponse = http.post(`${BASE_URL}/auth/register`, registerPayload, {
      headers: { "Content-Type": "application/json" },
    });

    authSuccess.add([200, 400].includes(registerResponse.status));

    let loginPayload = `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`;
    let loginResponse = http.post(`${BASE_URL}/auth/login`, loginPayload, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    authSuccess.add([200, 401].includes(loginResponse.status));
    check(loginResponse, { "response time < 500ms": (r) => r.timings.duration < 500 });
  });

  sleep(2);
  activeUsers.add(-1);
}

// ================================================================
// SETUP / TEARDOWN
// ================================================================

export function setup() {
  console.log("Starting performance test...");
  return { startTime: new Date() };
}

export function teardown(data) {
  const endTime = new Date();
  const duration = (endTime - new Date(data.startTime)) / 1000;
  console.log(`Test completed in ${duration} seconds`);
}

// ================================================================
// ALTERNATIVE : Test de stress (scenario séparé)
// ================================================================

/*
Utiliser avec:
k6 run --scenario stress_test loadtest_k6.js

export const stressTest = {
  executor: 'constant-arrival-rate',
  rate: 100,              // 100 requêtes par seconde
  timeUnit: '1s',
  duration: '5m',
  preAllocatedVUs: 50,
  maxVUs: 200,
};
*/
