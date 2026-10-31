// LocksMitch: posting to the LocksMitch Facebook Page.
// The app secret (FB_APP_SECRET) and the Page token (FB_PAGE_TOKEN) live in Script Properties, never in code.
// Connecting: open <web app URL>?fb=login, continue to Facebook, pick the Page.
// A Page token made from a long-lived user token has no expiry date; if Facebook revokes it, connect again.
var FB_APP_ID = '1146126358370915';
var FB_LOGIN_CONFIG = '1393127369559513'; // "Page posting" in Facebook Login for Business: pages_show_list, pages_read_engagement, pages_manage_posts
var FB_API = 'https://graph.facebook.com/v21.0/';
var FB_PAGE = '985784967959301'; // facebook.com/LocksMitch.ga

function facebookLoginPage_() {
  var state = 'fb_' + Utilities.getUuid();
  PropertiesService.getScriptProperties().setProperty('FB_STATE', state);
  var url = 'https://www.facebook.com/v21.0/dialog/oauth?client_id=' + FB_APP_ID +
            '&redirect_uri=' + encodeURIComponent(IG_REDIRECT) +
            '&response_type=code&config_id=' + FB_LOGIN_CONFIG + '&state=' + state;
  return page_('Connect Facebook', '<p>This lets LocksMitch publish posts you approve on your Facebook Page.</p>' +
               '<p><a class="b" href="' + url + '" target="_top">Continue to Facebook</a></p>');
}

function facebookCallback_(p) {
  try {
    return facebookCallbackInner_(p);
  } catch (err) {
    console.error('Facebook callback error: ' + err + '\n' + (err.stack || ''));
    return page_('Something went wrong', '<p>' + esc_(String(err)) + '</p><p>Open the connect link again to retry.</p>');
  }
}

function facebookCallbackInner_(p) {
  var props = PropertiesService.getScriptProperties();
  if (!p.state || p.state !== props.getProperty('FB_STATE')) {
    return page_('Link expired', '<p>Open the connect link again and retry.</p>');
  }
  var secret = props.getProperty('FB_APP_SECRET');
  if (!secret) return page_('App secret missing', '<p>Add FB_APP_SECRET in Project Settings → Script properties.</p>');

  var short = igCall_('get', 'oauth/access_token', { client_id: FB_APP_ID, client_secret: secret,
    redirect_uri: IG_REDIRECT, code: String(p.code).replace(/#_$/, '') }, '', FB_API).access_token;
  var long = igCall_('get', 'oauth/access_token', { grant_type: 'fb_exchange_token', client_id: FB_APP_ID,
    client_secret: secret, fb_exchange_token: short }, '', FB_API).access_token;
  // me/accounts comes back empty for this Page, so ask for the Page itself. Never any other Page.
  var page = igCall_('get', FB_PAGE, { fields: 'id,name,access_token' }, long, FB_API);
  if (!/locks\s*mitch/i.test(page.name) || !page.access_token) {
    return page_('Wrong Page', '<p>Nothing saved. Got: ' + esc_(page.name) + '.</p>');
  }

  props.deleteProperty('FB_STATE');
  props.setProperty('FB_PAGE_ID', page.id);
  props.setProperty('FB_PAGE_TOKEN', page.access_token);
  return page_('Facebook connected', '<p>Page: ' + esc_(page.name) + '.</p><p>You can close this tab.</p>');
}

// POST action=fb_publish&key=...&caption=...&image_urls=<one URL per line> | video_url=...  [&dry=1 only checks the token]
function fbPublish_(p) {
  if (!publishKeyOk_(p)) return { ok: false, error: 'forbidden' };
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('FB_PAGE_TOKEN'), pageId = props.getProperty('FB_PAGE_ID');
  if (!token || !pageId) return { ok: false, error: 'not_connected' };
  try {
    if (p.dry === '1') return { ok: true, dry: true, page: igCall_('get', pageId, { fields: 'id,name,link' }, token, FB_API) };
    var images = String(p.image_urls || '').split('\n').map(function (s) { return s.trim(); }).filter(String);
    var caption = String(p.caption || ''), postId;
    if (p.video_url) {
      postId = igCall_('post', pageId + '/videos', { file_url: p.video_url, description: caption }, token, FB_API).id;
    } else if (images.length === 1) {
      var photo = igCall_('post', pageId + '/photos', { url: images[0], message: caption }, token, FB_API);
      postId = photo.post_id || photo.id;
    } else if (images.length > 1) {
      var params = { message: caption };
      images.slice(0, 10).forEach(function (u, i) {
        var id = igCall_('post', pageId + '/photos', { url: u, published: 'false' }, token, FB_API).id;
        params['attached_media[' + i + ']'] = JSON.stringify({ media_fbid: id });
      });
      postId = igCall_('post', pageId + '/feed', params, token, FB_API).id;
    } else {
      return { ok: false, error: 'no_media' };
    }
    return { ok: true, id: postId, permalink: igCall_('get', postId, { fields: 'permalink_url' }, token, FB_API).permalink_url };
  } catch (err) {
    console.error('fb_publish: ' + err);
    return { ok: false, error: String(err.message || err).slice(0, 400) };
  }
}
