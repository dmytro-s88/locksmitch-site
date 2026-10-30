// LocksMitch: Instagram photo feed for the website gallery.
// The token lives in Script Properties under IG_TOKEN (never in code).
// GET ?feed=instagram returns {ok, photos:[{src, link, caption}]} with photos and carousels only.

var IG_FIELDS = 'id,caption,media_type,media_url,permalink,timestamp,children{media_type,media_url}';
var IG_MAX = 12;

function instagramFeed_() {
  var cache = CacheService.getScriptCache();
  var hit = cache.get('ig_feed');
  if (hit) return JSON.parse(hit);

  var token = PropertiesService.getScriptProperties().getProperty('IG_TOKEN');
  if (!token) return { ok: false, error: 'no_token', photos: [] };

  var url = 'https://graph.instagram.com/v21.0/me/media?fields=' + encodeURIComponent(IG_FIELDS) +
            '&limit=50&access_token=' + encodeURIComponent(token);
  var res = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  if (res.getResponseCode() !== 200) {
    console.error('Instagram API ' + res.getResponseCode() + ': ' + res.getContentText().slice(0, 300));
    return { ok: false, error: 'api', photos: [] };
  }

  var photos = [];
  (JSON.parse(res.getContentText()).data || []).forEach(function (m) {
    if (photos.length >= IG_MAX) return;
    var src = null;
    if (m.media_type === 'IMAGE') src = m.media_url;
    else if (m.media_type === 'CAROUSEL_ALBUM' && m.children && m.children.data) {
      var firstImage = m.children.data.filter(function (c) { return c.media_type === 'IMAGE'; })[0];
      if (firstImage) src = firstImage.media_url;
    }
    if (!src) return; // videos and reels are skipped
    photos.push({ src: src, link: m.permalink, caption: firstLine_(m.caption) });
  });

  var out = { ok: true, photos: photos };
  cache.put('ig_feed', JSON.stringify(out), 3600); // refresh at most once an hour
  return out;
}

function firstLine_(text) {
  var line = String(text || '').split('\n')[0].replace(/#\S+/g, '').trim();
  return line.length > 90 ? line.slice(0, 87) + '…' : line;
}

// Long-lived tokens last 60 days; a monthly trigger keeps it fresh.
function refreshInstagramToken() {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('IG_TOKEN');
  if (!token) return;
  var res = UrlFetchApp.fetch('https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=' +
                              encodeURIComponent(token), { muteHttpExceptions: true });
  if (res.getResponseCode() === 200) {
    props.setProperty('IG_TOKEN', JSON.parse(res.getContentText()).access_token);
    props.setProperty('IG_TOKEN_REFRESHED', new Date().toISOString());
  } else {
    console.error('Token refresh failed ' + res.getResponseCode() + ': ' + res.getContentText().slice(0, 300));
  }
}

// Run once after the token is saved: checks the feed and sets up the monthly refresh.
function setupInstagram() {
  CacheService.getScriptCache().remove('ig_feed');
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'refreshInstagramToken') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('refreshInstagramToken').timeBased().onMonthDay(1).atHour(4).create();
  var feed = instagramFeed_();
  Logger.log('Photos found: ' + feed.photos.length + (feed.ok ? '' : ' (error: ' + feed.error + ')'));
  return { ok: feed.ok, photos: feed.photos.length, error: feed.error || null };
}

// ---- Connecting Instagram without a popup ----
// 1) Open <web app URL>?ig=login in a normal tab and continue to Instagram.
// 2) Instagram sends you back here with ?code=..., which is exchanged for a 60-day token and saved.
var IG_APP_ID = '2200310130907398';
var IG_REDIRECT = 'https://script.google.com/macros/s/AKfycbwEnPklqAabpkxC7UoInrIwUW17F5hXMmveX2hEEUIxUGt7hskz_RNbpzz9QHiTZIKz/exec';

function instagramLoginPage_() {
  var state = Utilities.getUuid();
  PropertiesService.getScriptProperties().setProperty('IG_STATE', state);
  var url = 'https://www.instagram.com/oauth/authorize?enable_fb_login=0' +
            '&client_id=' + IG_APP_ID +
            '&redirect_uri=' + encodeURIComponent(IG_REDIRECT) +
            '&response_type=code&scope=instagram_business_basic,instagram_business_content_publish' +
            '&state=' + state;
  return page_('Connect Instagram', '<p>This connects @locksmitch.ga to the website gallery and lets LocksMitch publish posts you approve.</p>' +
               '<p><a class="b" href="' + url + '" target="_top">Continue to Instagram</a></p>');
}

function instagramCallback_(p) {
  try {
    return instagramCallbackInner_(p);
  } catch (err) {
    console.error('Instagram callback error: ' + err + '\n' + (err.stack || ''));
    PropertiesService.getScriptProperties().setProperty('IG_LAST_ERROR', String(err).slice(0, 500));
    return page_('Something went wrong', '<p>' + esc_(String(err)) + '</p><p>Open the connect link again to retry.</p>');
  }
}

function instagramCallbackInner_(p) {
  var props = PropertiesService.getScriptProperties();
  if (!p.state || p.state !== props.getProperty('IG_STATE')) {
    return page_('Link expired', '<p>Open the connect link again and retry.</p>');
  }
  var secret = props.getProperty('IG_APP_SECRET');
  if (!secret) return page_('App secret missing', '<p>Add IG_APP_SECRET in Project Settings → Script properties.</p>');

  var r1 = UrlFetchApp.fetch('https://api.instagram.com/oauth/access_token', {
    method: 'post', muteHttpExceptions: true,
    payload: { client_id: IG_APP_ID, client_secret: secret, grant_type: 'authorization_code',
               redirect_uri: IG_REDIRECT, code: String(p.code).replace(/#_$/, '') }
  });
  var j1 = JSON.parse(r1.getContentText() || '{}');
  var short = j1.access_token || (j1.data && j1.data[0] && j1.data[0].access_token);
  if (!short) {
    console.error('Code exchange failed: ' + r1.getContentText().slice(0, 300));
    return page_('Instagram refused the code', '<p>' + esc_(j1.error_message || (j1.error && j1.error.message) || 'Unknown error') + '</p>');
  }
  var r2 = UrlFetchApp.fetch('https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=' +
                             encodeURIComponent(secret) + '&access_token=' + encodeURIComponent(short), { muteHttpExceptions: true });
  var j2 = JSON.parse(r2.getContentText() || '{}');
  if (!j2.access_token) {
    console.error('Long-lived exchange failed: ' + r2.getContentText().slice(0, 300));
    return page_('Could not get a long-lived token', '<p>' + esc_((j2.error && j2.error.message) || 'Unknown error') + '</p>');
  }
  props.deleteProperty('IG_STATE');
  props.setProperty('IG_TOKEN', j2.access_token);
  props.setProperty('IG_TOKEN_REFRESHED', new Date().toISOString());
  var res = setupInstagram();
  return page_('Instagram connected', '<p>Photos found: ' + res.photos + '. The website gallery will update within an hour.</p><p>You can close this tab.</p>');
}

function page_(title, body) {
  return HtmlService.createHtmlOutput('<style>body{font:16px/1.5 -apple-system,Segoe UI,sans-serif;padding:32px;max-width:520px}' +
    'a.b{display:inline-block;background:#6CC655;color:#0B170A;padding:12px 20px;border-radius:999px;text-decoration:none;font-weight:700}</style>' +
    '<h2>' + esc_(title) + '</h2>' + body).setTitle(title);
}

function esc_(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

// ---- Publishing posts (photo, carousel or reel) ----
// POST action=ig_publish&key=...&caption=...&image_urls=<one URL per line> | video_url=...  [&dry=1 only checks the token]
// Media must sit at public URLs. Only the SHA-256 of the key is stored here; the key itself stays on Dima's Mac.
var IG_PUBLISH_KEY_SHA256 = '6af7f9c6aceafb32ed9d88fcdc1dbd4a66270cb468361f85f54801b72799e796';
var IG_API = 'https://graph.instagram.com/v21.0/';

function igPublish_(p) {
  var digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, String(p.key || ''), Utilities.Charset.UTF_8)
    .map(function (b) { return ('0' + (b & 255).toString(16)).slice(-2); }).join('');
  if (digest !== IG_PUBLISH_KEY_SHA256) return { ok: false, error: 'forbidden' };
  var token = PropertiesService.getScriptProperties().getProperty('IG_TOKEN');
  if (!token) return { ok: false, error: 'no_token' };
  try {
    if (p.dry === '1') {
      var acc = igCall_('get', 'me', { fields: 'user_id,username,account_type' }, token), limit;
      try { limit = igCall_('get', 'me/content_publishing_limit', { fields: 'quota_usage,config' }, token).data; } // needs the publish permission
      catch (e) { limit = 'NO PUBLISH PERMISSION: ' + e.message; }
      return { ok: true, dry: true, account: acc, publishing_limit: limit };
    }
    var images = String(p.image_urls || '').split('\n').map(function (s) { return s.trim(); }).filter(String);
    var base = { caption: String(p.caption || '') };
    if (p.location_id) base.location_id = p.location_id;
    var container;
    if (p.video_url) {
      container = igCall_('post', 'me/media', Object.assign({ media_type: 'REELS', video_url: p.video_url, share_to_feed: 'true' }, base), token).id;
    } else if (images.length === 1) {
      container = igCall_('post', 'me/media', Object.assign({ image_url: images[0] }, base), token).id;
    } else if (images.length > 1) {
      var children = images.slice(0, 10).map(function (u) {
        var id = igCall_('post', 'me/media', { image_url: u, is_carousel_item: 'true' }, token).id;
        igWaitReady_(id, token);
        return id;
      });
      container = igCall_('post', 'me/media', Object.assign({ media_type: 'CAROUSEL', children: children.join(',') }, base), token).id;
    } else {
      return { ok: false, error: 'no_media' };
    }
    igWaitReady_(container, token);
    var postId = igCall_('post', 'me/media_publish', { creation_id: container }, token).id;
    CacheService.getScriptCache().remove('ig_feed');
    return { ok: true, id: postId, permalink: igCall_('get', postId, { fields: 'permalink' }, token).permalink };
  } catch (err) {
    console.error('ig_publish: ' + err);
    return { ok: false, error: String(err.message || err).slice(0, 400) };
  }
}

function igCall_(method, path, params, token) {
  params.access_token = token;
  var res = method === 'get'
    ? UrlFetchApp.fetch(IG_API + path + '?' + Object.keys(params).map(function (k) { return k + '=' + encodeURIComponent(params[k]); }).join('&'), { muteHttpExceptions: true })
    : UrlFetchApp.fetch(IG_API + path, { method: 'post', payload: params, muteHttpExceptions: true });
  var j = JSON.parse(res.getContentText() || '{}');
  if (res.getResponseCode() !== 200 || j.error) throw new Error(path + ': ' + ((j.error && (j.error.error_user_msg || j.error.message)) || res.getResponseCode()));
  return j;
}

// Containers (above all videos) need processing time before they can be published.
function igWaitReady_(id, token) {
  for (var i = 0; i < 60; i++) {
    var s = igCall_('get', id, { fields: 'status_code' }, token).status_code;
    if (s === 'FINISHED') return;
    if (s === 'ERROR' || s === 'EXPIRED') throw new Error('media ' + id + ' status ' + s);
    Utilities.sleep(i < 5 ? 2000 : 5000);
  }
  throw new Error('media ' + id + ' still processing');
}
