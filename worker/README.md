# Transport timetable API Worker

This Cloudflare Worker keeps the Auckland Transport subscription keys out of the GitHub Pages files. It only accepts read-only requests from the Crystal-Cobble GitHub Pages origin, only forwards the GTFS and realtime endpoints used by the site, and caches successful responses at Cloudflare's edge.

Deployed endpoint: `https://transport-timetable-api.baileylivingstonnz.workers.dev`

The deployed Worker requires two encrypted Cloudflare secrets:

- `AT_GTFS_KEY`
- `AT_REALTIME_KEY`

Set `apiBase` in `js/beta-api-config.js` to the Worker's HTTPS URL. Never add either key to this repository or to a Wrangler `vars` section.
