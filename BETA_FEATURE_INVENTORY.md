# Beta rebuild feature inventory

This inventory treats `index.html` and `live.html` as the current functional specification. Theme switching and theme-specific presentation are intentionally excluded from the beta rebuild.

## Departure board (`index.html`)

### Stop selection

- Search AT stops by stop name, stop code, platform and location.
- Debounced suggestions with grouped parent stations and child platforms.
- Select multiple stops and remove them individually.
- Clear every selected stop.
- Restore selected stops from local storage.
- Fetch complete stop details and child platforms after restoration.
- Prevent duplicate stop selection.
- Fall back from filtered AT search to a wider local filter.
- Fall back to a small built-in stop list when AT search is unavailable.

### Departures

- Load upcoming departures for every selected stop.
- Combine and chronologically sort departures from multiple stops.
- Show route, mode, destination, scheduled time and expected time.
- Show live due-time wording, delay/ahead/on-time status and cancellation state.
- Show platform or stop information.
- Show wheelchair and bicycle accessibility.
- Show occupancy status and occupancy meter.
- Use GTFS route colours plus AT line and Link-brand colour overrides.
- Limit the initial list and allow the complete list to be shown.
- Refresh departures automatically.
- Show an empty state when no services are found.

### Realtime enrichment

- Use the combined realtime feed where available.
- Fall back to separate trip-update and vehicle-location feeds.
- Match realtime trips and vehicles to scheduled departures.
- Display vehicle label, distance, congestion and schedule relationship.
- Identify cancelled and out-of-service services.
- Load ferry vessel positions.

### Rail disruption handling

- Determine whether Eastern, Southern, Western and Onehunga lines are running.
- Detect service alerts affecting rail routes.
- Detect stations with no scheduled rail trips.
- Display suspended-line and out-of-service notices.
- Find nearby rail-replacement bus stops.
- Allow a relevant replacement-bus stop to be added from a disruption notice.

### Journey details

- Expand a departure to view its trip.
- Load trip metadata, stop times and ordered stops.
- Mark the current stop in the journey.
- Show vehicle progress and location when available.
- Show route-specific service alerts.

### Page utilities

- Live Auckland date and clock.
- Last-updated indicator.
- Auckland weather, treated as optional.
- Fullscreen departure-board mode.
- Persist terminus-arrival and out-of-service toggles.
- Calendar/version warning when timetable data is unavailable for today.
- Responsive desktop and mobile layouts.
- Links to beta live tracking and the map.

## Live tracking (`live.html`)

### Map and vehicle display

- Leaflet map centred on Auckland.
- Live bus, train and ferry markers.
- Optional display of other boats.
- Directional vehicle markers with mode-specific icons and colours.
- Route-aware marker stacking.
- Remove stale markers when vehicles leave the feed.
- Restrict displayed vehicles to the Auckland region.
- Refresh vehicle positions every 15 seconds.
- Display vehicle count and last update time.

### Vehicle classification and fallbacks

- Load GTFS routes and build route-type, short-name, long-name and colour indexes.
- Use combined realtime data to associate vehicle IDs with route IDs.
- Fall back to the vehicle-location feed.
- Classify modes by GTFS route type and known route prefixes.
- Recognise known ferry vessel names.
- Use conservative water and rail-infrastructure checks only as last-resort classification.
- Report unresolved vehicles for diagnostics.

### Filters and route controls

- Independently toggle buses, trains, ferries and other boats.
- Filter visible vehicles by route text.
- Open a complete route panel.
- Search routes within the route panel.
- Toggle individual routes.
- Select or deselect every route.
- Show the current visible/total route count.

### Rail infrastructure

- Draw Eastern, Southern, Western and Onehunga rail lines.
- Toggle rail lines independently from vehicles.
- Show the City Rail Link tunnel and legend item.
- Load rail stations and display station markers.
- Find upcoming rail routes serving stations.
- Use official line colours.

### Vehicle information

- Popup with route, long name, mode and vehicle label.
- Bearing, speed and current position details.
- Occupancy information.
- Realtime timestamp and update age.
- Escaped API content before insertion into HTML.

### Location and responsive behaviour

- One-shot browser geolocation.
- Continuous position watching after location is enabled.
- User-location marker and map centring.
- Clear unsupported, active and error states for location.
- Responsive controls and mobile popup sizing.
- Link back to the beta departure board.

## Rebuild rules

- Use one AT identity only: Shore, Ocean, Safety and approved supporting colours.
- Use Open Sans for web UI and sentence-case headings.
- Use official AT logos without alteration and with adequate clear space.
- Use pictograms from `images/png` or `images/svg` for transport modes and facilities.
- Keep operational fallbacks; remove visual themes and presentation-only fallbacks.
- Keep the production HTML files unchanged until the beta rebuild is approved.
