import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
  },
};

const BASE = __ENV.BASE_URL || "http://127.0.0.1:8000";

export default function () {
  const r1 = http.get(`${BASE}/health`);
  check(r1, { "health 200": (r) => r.status === 200 });

  const r2 = http.get(`${BASE}/assets?limit=10`);
  check(r2, { "assets 200": (r) => r.status === 200 });

  sleep(1);
}

