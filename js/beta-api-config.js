/* Shared public configuration. Auckland Transport keys live in the Cloudflare Worker only. */
window.AT_BETA_CONFIG = Object.assign({}, window.AT_BETA_CONFIG, {
    apiBase: 'https://transport-timetable-api.baileylivingstonnz.workers.dev'
});
