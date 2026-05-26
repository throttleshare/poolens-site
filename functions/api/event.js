// POST /api/event - anonymous first-party launch event capture.
// Env: SUBSCRIBERS_DB (D1 binding shared with the Route Ready waitlist)

const ALLOWED_ORIGINS = new Set([
  'https://splashlens.com',
  'https://www.splashlens.com',
  'https://app.splashlens.com',
  'http://localhost:8788',
  'http://localhost:5173',
]);

function corsHeaders(request) {
  const origin = request.headers.get('Origin') || '';
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.has(origin) ? origin : 'https://splashlens.com',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Content-Type': 'application/json',
  };
}

function clean(value, max = 120) {
  return String(value || '').replace(/[\u0000-\u001f\u007f]/g, '').trim().slice(0, max);
}

export async function onRequestPost({ request, env }) {
  const headers = corsHeaders(request);
  let body;

  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ ok: false, error: 'Invalid JSON' }), { status: 400, headers });
  }

  const event = clean(body.event || body.name, 80);
  if (!event) {
    return new Response(JSON.stringify({ ok: false, error: 'Event name required' }), { status: 400, headers });
  }

  const props = body.props && typeof body.props === 'object' ? body.props : {};
  const path = clean(body.path || props.path, 300);
  const plan = clean(body.plan || props.plan, 60);
  const mode = clean(body.mode || props.mode, 60);
  const source = clean(body.source || props.source || 'unknown', 60);
  const referrer = clean(request.headers.get('Referer') || body.referrer || props.referrer, 500);
  const userAgent = clean(request.headers.get('User-Agent'), 300);
  const country = clean(request.cf?.country, 10);
  const propsJson = JSON.stringify(props).slice(0, 2000);

  try {
    await env.SUBSCRIBERS_DB.prepare(
      `INSERT INTO events (event, source, path, plan, mode, props, user_agent, referrer, country)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(event, source, path, plan, mode, propsJson, userAgent, referrer, country).run();

    return new Response(JSON.stringify({ ok: true }), { status: 200, headers });
  } catch (err) {
    console.error('Event capture error:', err);
    return new Response(JSON.stringify({ ok: false, error: 'Database error' }), { status: 500, headers });
  }
}

export async function onRequestOptions({ request }) {
  return new Response(null, { status: 204, headers: corsHeaders(request) });
}
