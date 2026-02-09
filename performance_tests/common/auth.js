import http from "k6/http";
import { check, fail } from "k6";
import { DEFAULT_HEADERS } from "./config.js";


const USERNAME = __ENV.USERNAME;
const PASSWORD = __ENV.PASSWORD;

if (!USERNAME || !PASSWORD) {
    fail("USERNAME or PASSWORD environment variable is not set!");
}

const LOGIN_URL = "http://127.0.0.1:8000/accounts/login/";

export function login() {
  const payload = JSON.stringify({
    username: USERNAME,
    password: PASSWORD,
  });

  const res = http.post(LOGIN_URL, payload, {
    headers: {
      ...DEFAULT_HEADERS,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  });

  const ok = check(res, {
    "login status is 200": (r) => r.status === 200,
    "access token present": (r) => r.json("access") !== undefined,
  });

  if (!ok) {
    console.error("Login failed:", res.status, res.body);
    fail("Stopping test due to failed login");
  }

  return res.json("access");
}
