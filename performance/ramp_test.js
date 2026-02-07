import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

export let ResponseTimeTrend = new Trend('response_time_trend');

const BASE_URL = 'http://localhost:8000/api/stories/';
const LOGIN_URL = 'http://localhost:8000/api/login/';

// Test user credentials (must exist in your DB)
const USERNAME = 'testuser@example.com';
const PASSWORD = 'yourpassword';

export const options = {
    stages: [
        { duration: '10s', target: 50 },
        { duration: '20s', target: 200 },
        { duration: '30s', target: 100 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],
        checks: ['rate>0.99'],
    },
};

export default function () {
    // 1️⃣ Login to get JWT
    const loginPayload = JSON.stringify({ email: USERNAME, password: PASSWORD });
    let res = http.post(LOGIN_URL, loginPayload, {
        headers: { 'Content-Type': 'application/json' },
    });

    check(res, { 'login succeeded': (r) => r.status === 200 && r.json('access') !== undefined });
    const token = res.json('access');
    const authHeaders = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

    sleep(0.5);

    // 2️⃣ List stories
    res = http.get(BASE_URL, { headers: authHeaders });
    check(res, { 'list status 200': (r) => r.status === 200 });
    ResponseTimeTrend.add(res.timings.duration);
    sleep(0.5);

    // 3️⃣ Story detail
    const storyId = 1;  // change dynamically if needed
    res = http.get(`${BASE_URL}${storyId}/`, { headers: authHeaders });
    check(res, { 'detail status 200': (r) => r.status === 200 });
    ResponseTimeTrend.add(res.timings.duration);
    sleep(0.5);

    // 4️⃣ POST reaction
    const reactionPayload = JSON.stringify({ reaction: 'like' });
    res = http.post(`${BASE_URL}${storyId}/reaction/`, reactionPayload, { headers: authHeaders });
    check(res, { 'reaction status 201 or 409': (r) => r.status === 201 || r.status === 409 });
    ResponseTimeTrend.add(res.timings.duration);
    sleep(0.5);

    // 5️⃣ PATCH reaction (toggle reaction)
    const patchPayload = JSON.stringify({ reaction: 'dislike' });
    res = http.patch(`${BASE_URL}${storyId}/reaction/`, patchPayload, { headers: authHeaders });
    check(res, { 'patch reaction status 200 or 409': (r) => r.status === 200 || r.status === 409 });
    ResponseTimeTrend.add(res.timings.duration);
    sleep(0.5);

    // 6️⃣ POST review
    const reviewPayload = JSON.stringify({ content: 'This story is amazing!' });
    res = http.post(`${BASE_URL}${storyId}/reviews/`, reviewPayload, { headers: authHeaders });
    check(res, { 'review create status 201': (r) => r.status === 201 });
    ResponseTimeTrend.add(res.timings.duration);

    sleep(1);
}
