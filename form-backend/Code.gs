// LocksMitch: estimate form from new.locksmitch.com -> email.
var TO = 'info@locksmitch.com';
var SUBJECT = 'Estimate request';
var MAX_PER_HOUR = 40;

function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p.company) return out({ ok: true }); // honeypot field, bots fill it

  var name = clean(p.name, 80);
  var phone = clean(p.phone, 40);
  var vehicle = clean(p.vehicle, 120);
  var service = clean(p.service, 60);
  var page = clean(p.page, 200);
  if (!name || !phone || !vehicle) return out({ ok: false, error: 'missing' });
  if ((phone.match(/\d/g) || []).length < 7) return out({ ok: false, error: 'phone' });

  var cache = CacheService.getScriptCache();
  var count = Number(cache.get('sent') || 0);
  if (count >= MAX_PER_HOUR) return out({ ok: false, error: 'busy' });
  cache.put('sent', String(count + 1), 3600);

  var when = Utilities.formatDate(new Date(), 'America/New_York', 'MMM d, yyyy h:mm a');
  var body = [
    'New estimate request from the website',
    '',
    'Service: ' + (service || '-'),
    'Vehicle: ' + vehicle,
    'Name: ' + name,
    'Phone: ' + phone,
    '',
    'Sent: ' + when + ' (Atlanta time)',
    'Page: ' + (page || 'new.locksmitch.com')
  ].join('\n');

  MailApp.sendEmail({ to: TO, subject: SUBJECT, body: body, name: 'LocksMitch website' });
  return out({ ok: true });
}

function doGet(e) {
  if (e && e.parameter && e.parameter.feed === 'instagram') return out(instagramFeed_());
  if (e && e.parameter && e.parameter.ig === 'login') return instagramLoginPage_();
  if (e && e.parameter && e.parameter.code) return instagramCallback_(e.parameter);
  return ContentService.createTextOutput('LocksMitch estimate form endpoint is running.');
}

// Run once from the editor to grant the "send email" permission.
function authorize() {
  Logger.log('Emails left today: ' + MailApp.getRemainingDailyQuota());
}

function out(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function clean(v, max) {
  return String(v || '').replace(/[\r\n\t]+/g, ' ').trim().slice(0, max);
}
