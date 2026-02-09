import http from "k6/http";
import { check, sleep } from "k6";
import { BASE_URL } from "./common/config.js";

export const options = {
  // stages: [
  //   { duration: "30s", target: 50 },
  //   { duration: "60s", target: 100 },
  //   { duration: "30s", target: 150 },
  //   { duration: "60s", target: 200 },
  //   { duration: "30s", target: 0 },
  // ],
  stages: [
    { duration: "30s", target: 50 },
    { duration: "60s", target: 100 },
    { duration: "30s", target: 250 },
    { duration: "30s", target: 500 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<3000"],
    http_req_failed: ["rate<0.05"],
    checks: ["rate>0.95"],
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/stories/`);

  check(res, {
    "stories list 200": (r) => r.status === 200,
  });

  sleep(1);
}
