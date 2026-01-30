import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,          // virtual users
  duration: "30s",  // test duration
};

export default function () {
  const res = http.get("http://localhost:8000/api/stories/");

  check(res, {
    "status is 200": (r) => r.status === 200,
    "response time < 500ms": (r) => r.timings.duration < 500,
  });

  sleep(1);
}





