# Transport timetable API Worker

This Cloudflare Worker keeps the Auckland Transport subscription keys out of the GitHub Pages files. It accepts read-only requests from the Crystal-Cobble GitHub Pages site, local development servers, and the standard origins used by packaged Android/iOS web apps. It forwards the GTFS, realtime, and train vehicle-assignment endpoints used by the site, plus AT Mobile's public vehicle-promotions feed, and caches successful responses at Cloudflare's edge.

Deployed endpoint: `https://transport-timetable-api.baileylivingstonnz.workers.dev`

The deployed Worker requires two encrypted Cloudflare secrets:

- `AT_GTFS_KEY`
- `AT_REALTIME_KEY`
- `AT_TIMETABLE_KEY`

The `/vehicle-promotions` endpoint proxies AT Mobile's public `BikesOnBus` promotion feed; it requires no additional secret.

The `/serviceinfo/v1/vehicles/byTripId/{tripId}` endpoint proxies AT's assigned-vehicle list for a trip using `AT_TIMETABLE_KEY`. The departure board follows AT's site and counts three carriages per returned vehicle.

Set `apiBase` in `js/beta-api-config.js` to the Worker's HTTPS URL. Never add either key to this repository or to a Wrangler `vars` section.
