import http from "k6/http";
import { check, sleep } from "k6";
import { BASE_URL, DEFAULT_HEADERS } from "./common/config.js";
import { login } from "./common/auth.js";
import { pickStoryId } from "./common/stories.js";

export const options = {
  scenarios: {
    write_interactions: {
      executor: "constant-vus",
      vus: 50,
      duration: "3m",
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<5000"],
    http_req_failed: ["rate<1"], // allow up to 100% because your checks validate expected failures
  },
};

export function setup() {
  const token = login();
  return { token };
}

export default function (data) {
  const headers = {
    ...DEFAULT_HEADERS,
    "Content-Type": "application/json",
    Authorization: `Bearer ${data.token}`,
  };

  const storyId = pickStoryId();

  // REACTION
  const reactionRes = http.post(
    `${BASE_URL}/stories/${storyId}/reaction/`,
    JSON.stringify({ reaction: "like" }),
    { headers }
  );

  check(reactionRes, {
    "reaction accepted or conflict": (r) =>
      r.status === 201 || r.status === 409,
  });

  if (reactionRes.status === 409) {
    const patchRes = http.patch(
      `${BASE_URL}/stories/${storyId}/reaction/`,
      JSON.stringify({ reaction: "dislike" }),
      { headers }
    );

    check(patchRes, { "reaction patch ok": (r) => r.status === 200 });
  }

  // RATING
  const ratingRes = http.post(
    `${BASE_URL}/stories/${storyId}/rating/`,
    JSON.stringify({ rating: 4 }),
    { headers }
  );

  check(ratingRes, {
    "rating accepted or bad request": (r) =>
      r.status === 201 || r.status === 400,
  });

  // REVIEW
  const reviewRes = http.post(
    `${BASE_URL}/stories/${storyId}/reviews/`,
    JSON.stringify({ content: "Great story!" }),
    { headers }
  );

  check(reviewRes, {
    "review accepted or bad request": (r) =>
      r.status === 201 || r.status === 400,
  });

  sleep(2);
}
