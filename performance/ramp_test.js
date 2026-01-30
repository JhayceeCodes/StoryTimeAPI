// import http from 'k6/http';
// import { check, sleep } from 'k6';
//
// export const options = {
//     stages: [
//         { duration: '30s', target: 10 },   // ramp up from 0 → 10 users
//         { duration: '1m',  target: 50 },   // ramp up from 10 → 50 users
//         { duration: '30s', target: 50 },   // stay at 50 users
//         { duration: '1m',  target: 100 },  // ramp up 50 → 100 users
//         { duration: '1m',  target: 0 },    // ramp down to 0
//     ],
// };
//
// export default function () {
//     const res = http.get('http://localhost:8000/api/stories/');
//
//     check(res, {
//         'status is 200': (r) => r.status === 200,
//         'response time < 500ms': (r) => r.timings.duration < 500,
//     });
//
//     sleep(1); // simulate user think time
// }


import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// Custom metric to track response times
export let ResponseTimeTrend = new Trend('response_time_trend');

const BASE_URL = 'http://localhost:8000/api/stories/';

export const options = {
    stages: [
        { duration: '10s', target: 50 },    // initial spike start
        { duration: '20s', target: 200 },   // peak spike
        { duration: '30s', target: 100 },   // ramp down partially
        { duration: '30s', target: 0 },     // ramp down to 0
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],  // ✅ correct percentile syntax
        checks: ['rate>0.99'],             // >99% checks succeed
    },
};

export default function () {
    // Anonymous request
    const res = http.get(BASE_URL);

    check(res, {
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });

    ResponseTimeTrend.add(res.timings.duration);

    sleep(0.5); // short think time to simulate spike
}
