const AT_ORIGIN = 'https://api.at.govt.nz';
const GITHUB_PAGES_ORIGIN = 'https://crystal-cobble.github.io';

const GTFS_PATHS = [
  /^\/gtfs\/v3\/routes\/?$/,
  /^\/gtfs\/v3\/stops\/?$/,
  /^\/gtfs\/v3\/stops\/[^/]+\/stoptrips\/?$/,
  /^\/gtfs\/v3\/trips\/[^/]+(?:\/(?:stoptimes|stops))?\/?$/,
  /^\/gtfs\/v3\/versions\/?$/,
  /^\/gtfs\/v3\/shapes\/?$/
];
const REALTIME_PATH = /^\/realtime\/legacy(?:\/(?:tripupdates|vehiclelocations|servicealerts))?\/?$/;
const QUERY_KEY = /^(?:filter\[[a-z_]+\]|page\[(?:limit|offset)\])$/;

function originAllowed(origin) {
  return origin === GITHUB_PAGES_ORIGIN || /^http:\/\/(?:127\.0\.0\.1|localhost)(?::\d+)?$/.test(origin);
}

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Accept',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin'
  };
}

function jsonResponse(body, status, origin = '') {
  const headers = new Headers({'Content-Type': 'application/json; charset=utf-8', 'X-Content-Type-Options': 'nosniff'});
  if (originAllowed(origin)) Object.entries(corsHeaders(origin)).forEach(([key, value]) => headers.set(key, value));
  return new Response(JSON.stringify(body), {status, headers});
}

function cacheSeconds(pathname) {
  if (pathname.startsWith('/realtime/legacy')) return pathname.endsWith('/servicealerts') ? 60 : 8;
  if (pathname.includes('/stoptrips')) return 300;
  return 3600;
}

function routeFor(pathname, env) {
  if (GTFS_PATHS.some(pattern => pattern.test(pathname))) return {key: env.AT_GTFS_KEY, accept: 'application/json'};
  if (REALTIME_PATH.test(pathname)) return {key: env.AT_REALTIME_KEY, accept: 'application/json'};
  return null;
}

function addCors(response, origin, cacheStatus) {
  const headers = new Headers(response.headers);
  Object.entries(corsHeaders(origin)).forEach(([key, value]) => headers.set(key, value));
  headers.set('X-Content-Type-Options', 'nosniff');
  headers.set('X-Proxy-Cache', cacheStatus);
  return new Response(response.body, {status: response.status, statusText: response.statusText, headers});
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin') || '';

    if (url.pathname === '/health' && request.method === 'GET') {
      return jsonResponse({ok: true, service: 'transport-timetable-api'}, 200, origin);
    }
    if (!originAllowed(origin)) return jsonResponse({error: 'Origin not allowed'}, 403);
    if (request.method === 'OPTIONS') return new Response(null, {status: 204, headers: corsHeaders(origin)});
    if (request.method !== 'GET') return jsonResponse({error: 'Method not allowed'}, 405, origin);

    const route = routeFor(url.pathname, env);
    if (!route) return jsonResponse({error: 'Endpoint not allowed'}, 404, origin);
    if (!route.key) return jsonResponse({error: 'Worker secret is not configured'}, 503, origin);
    for (const key of url.searchParams.keys()) {
      if (!QUERY_KEY.test(key)) return jsonResponse({error: 'Query parameter not allowed'}, 400, origin);
    }

    const target = new URL(url.pathname + url.search, AT_ORIGIN);
    const cache = caches.default;
    const cacheKey = new Request(target.toString(), {method: 'GET'});
    const cached = await cache.match(cacheKey);
    if (cached) return addCors(cached, origin, 'HIT');

    let upstream;
    try {
      upstream = await fetch(target, {
        headers: {
          'Accept': request.headers.get('Accept') || route.accept,
          'Ocp-Apim-Subscription-Key': route.key,
          'User-Agent': 'transport-timetable-worker/1.0'
        }
      });
    } catch {
      return jsonResponse({error: 'Auckland Transport is temporarily unreachable'}, 502, origin);
    }

    if (!upstream.ok) return jsonResponse({error: 'Auckland Transport request failed', status: upstream.status}, upstream.status, origin);
    const headers = new Headers(upstream.headers);
    headers.delete('Set-Cookie');
    headers.set('Cache-Control', `public, max-age=${cacheSeconds(url.pathname)}`);
    headers.set('X-Content-Type-Options', 'nosniff');
    const response = new Response(upstream.body, {status: upstream.status, statusText: upstream.statusText, headers});
    ctx.waitUntil(cache.put(cacheKey, response.clone()));
    return addCors(response, origin, 'MISS');
  }
};
