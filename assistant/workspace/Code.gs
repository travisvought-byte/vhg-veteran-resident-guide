/**
 * Veteran Home Guardians — Google Workspace Gmail draft intake pilot.
 *
 * PRIVATE EXECUTION: Install in a VHG-owned Google Apps Script project.
 * PUBLIC SOURCE: This script may be stored in GitHub; never add keys or inbox content.
 * This script NEVER calls sendEmail(), GmailDraft.send(), or the Gemini API.
 * All results stay as Gmail drafts for a human reviewer.
 *
 * Phase 1 deliberately handles new conversations; later replies in already
 * processed threads need human review. The script does not promise 24/7 support.
 */

// Change this when the mailbox or sender address is approved.
const VHG_CONFIG = Object.freeze({
  helpAddress: 'help@vethomeguard.org',
  resourceRoot: 'https://raw.githubusercontent.com/travisvought-byte/vhg-veteran-resident-guide/main/',
  maxThreadsPerRun: 15,
  searchLookback: '7d',
  maxBodyChars: 4000,
  labelProcessed: 'VHG/Processed',
  labelReview: 'VHG/Review',
  labelUrgent: 'VHG/Urgent',
  labelNeedsLocation: 'VHG/Needs-location',
  states: { OH: 'Ohio', PA: 'Pennsylvania', NY: 'New York', MI: 'Michigan', KY: 'Kentucky' },
  files: {
    OH: ['prototype-data.json', 'data/public/ohio-county-veterans-offices.json'],
    PA: ['data/public/pennsylvania-resources.json', 'data/public/pennsylvania-county-veterans-offices.json'],
    NY: ['data/public/new-york-resources.json', 'data/public/new-york-county-veterans-offices.json'],
    MI: ['data/public/michigan-resources.json', 'data/public/michigan-county-veterans-offices.json'],
    KY: ['data/public/kentucky-resources.json', 'data/public/kentucky-county-veterans-offices.json']
  }
});

const VHG_TOPICS = {
  housing: { patterns: ['homeless', 'housing', 'shelter', 'evict', 'rent', 'mortgage', 'unhoused', 'living in my car'],
    terms: ['housing', 'ssvf', 'shelter', 'homeless', 'rent', 'eviction'], tags: ['general_navigation', 'benefits_and_funding'] },
  accessibility: { patterns: ['wheelchair', 'ramp', 'accessibility', 'accessible', 'home modification', 'mobility', 'grab bars'],
    terms: ['ramp', 'accessib', 'equipment', 'hisa', 'adapted housing'], tags: ['equipment_home_accessibility'] },
  care: { patterns: ['nursing home', 'assisted living', 'caregiver', 'home care', 'respite', 'long term care', 'senior'],
    terms: ['nursing', 'care', 'aging', 'respite', 'ombudsman'], tags: ['help_at_home', 'care_facilities', 'caregiver_respite'] },
  benefits: { patterns: ['va claim', 'benefits', 'disability', 'pension', 'surviving spouse', 'widow', 'service connected', 'vso'],
    terms: ['benefits', 'claim', 'pension', 'veteran', 'compensation'], tags: ['veteran_services', 'benefits_and_funding'] },
  food: { patterns: ['food', 'groceries', 'hungry', 'meals', 'snap'],
    terms: ['food', 'meal', 'nutrition'], tags: ['general_navigation', 'help_at_home'] },
  transport: { patterns: ['transportation', 'ride', 'medical appointment', 'doctor appointment', 'travel to'],
    terms: ['transport', 'ride', 'travel'], tags: ['veteran_services', 'help_at_home'] },
  finances: { patterns: ['financial', 'utility', 'bills', 'emergency assistance', 'cannot afford', 'can\'t afford', 'no money'],
    terms: ['emergency', 'financial', 'payment', 'utility', 'grant'], tags: ['benefits_and_funding'] },
  legal: { patterns: ['lawyer', 'legal', 'tenant rights', 'discrimination', 'court', 'appeal denial'],
    terms: ['legal', 'rights', 'law', 'ombudsman'], tags: ['general_navigation'] }
};

function vhgGetLabel_(name) {
  return GmailApp.getUserLabelByName(name) || GmailApp.createLabel(name);
}

function vhgIsUrgent_(content) {
  return /\b(suicid(?:e|al)|kill myself|end my life|hurt myself|self.harm|want to die|overdose|immediate danger|life.threatening|medical emergency)\b/i.test(content || '');
}

function vhgExtractEmail_(value) {
  const found = String(value || '').match(/[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/);
  return found ? found[0].toLowerCase() : '';
}

function vhgWasAddressedToHelp_(message) {
  const recipients = (message.getTo() + ',' + message.getCc()).toLowerCase();
  return recipients.includes(VHG_CONFIG.helpAddress.toLowerCase());
}

function vhgIdentifyState_(text) {
  const s = String(text || '');
  const found = Object.entries(VHG_CONFIG.states).filter(([code, name]) => {
    return new RegExp('\\b' + name + '\\b', 'i').test(s) ||
      new RegExp('(?:^|[^A-Za-z])' + code + '(?=$|[^A-Za-z])').test(s);
  });
  return found.length === 1 ? found[0][0] : null;
}

function vhgFetchJson_(relativePath) {
  const url = VHG_CONFIG.resourceRoot + relativePath;
  const r = UrlFetchApp.fetch(url, { followRedirects: true, muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) throw new Error('Public resource data unavailable: ' + relativePath);
  const result = JSON.parse(r.getContentText('UTF-8'));
  if (!Array.isArray(result)) throw new Error('Guide data format unexpectedly changed: ' + relativePath);
  return result;
}

function vhgIdentifyCounty_(text, counties) {
  const hits = (counties || []).filter(row => {
    const name = String(row.county || '');
    if (!name) return false;
    return new RegExp('\\b' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?:\\s+County)?\\b', 'i').test(text);
  });
  return hits.length === 1 ? hits[0] : null;
}

function vhgAreaMatches_(record, state, county) {
  const area = Array.isArray(record.service_area) ? record.service_area.map(x => String(x).toLowerCase()) : [];
  const eligible = [VHG_CONFIG.states[state], state, 'Statewide', 'National', 'Federal', 'USA', 'US']
    .map(x => x.toLowerCase());
  return eligible.some(x => area.includes(x)) ||
    Boolean(county && area.some(x => x === county.toLowerCase() || x === (county + ' County').toLowerCase()));
}

function vhgFindTopics_(text) {
  const lower = String(text || '').toLowerCase();
  const hits = Object.keys(VHG_TOPICS).filter(key => VHG_TOPICS[key].patterns.some(p => lower.includes(p)));
  return hits.length ? hits : ['navigation'];
}

function vhgRankResources_(text, records, state, county) {
  const topics = vhgFindTopics_(text);
  const scored = [];
  (records || []).forEach(r => {
    if (!r || !r.verification || r.verification.record_status !== 'official_source_reviewed') return;
    if (!/^https?:\/\//i.test(r.official_url || '') || !vhgAreaMatches_(r, state, county)) return;
    const body = [r.name, r.organization, r.description, r.next_step].filter(Boolean).join(' ').toLowerCase();
    const tags = Array.isArray(r.needs_supported) ? r.needs_supported : [];
    let score = 0;
    topics.forEach(t => {
      if (t === 'navigation') { if (tags.includes('general_navigation')) score += 2; return; }
      const rule = VHG_TOPICS[t];
      if (rule.tags.some(tag => tags.includes(tag))) score++;
      rule.terms.forEach(term => { if (body.includes(term)) score += 4; });
    });
    if (county && (r.service_area || []).some(s => String(s).toLowerCase() === county.toLowerCase())) score += 2;
    if (score > 0) scored.push({record: r, score: score});
  });
  scored.sort((a, b) => b.score - a.score || String(a.record.name).localeCompare(String(b.record.name)));
  const seen = {};
  return scored.map(x => x.record).filter(r => {
    const id = r.program_id || r.name;
    if (seen[id]) return false;
    seen[id] = true;
    return true;
  }).slice(0, 5);
}

function vhgMakeDraft_(body, state, countyRow, resources) {
  const stateName = VHG_CONFIG.states[state];
  const location = (countyRow ? countyRow.county + ' County, ' : '') + stateName;
  const out = [
    'Thank you for contacting Veteran Home Guardians.',
    '',
    'Here are possible places to start for assistance in ' + location + '.',
    'These referrals come from published sources; they are not confirmations of current intake, availability, or eligibility.',
    ''
  ];
  if (vhgIsUrgent_(body)) out.push(
    'URGENT: If anyone is in immediate danger, call 911. For suicidal thoughts or an emotional crisis, call 988 and press 1 for the Veterans Crisis Line, or text 838255. Do not wait for an email reply.', ''
  );
  if (countyRow) out.push(
    'COUNTY VETERANS OFFICE',
    countyRow.county + ' County: ' + (countyRow.phone || 'confirm phone using source'),
    'Published source: ' + (countyRow.website || countyRow.source_url || 'See the state resource guide'),
    'Confirm the office\'s current intake and service availability directly.', ''
  );
  if (!resources.length) out.push(
    'The currently reviewed listings did not provide a clear match. This does NOT mean that assistance is unavailable. A county veterans office and the state resource guide are useful starting points.', ''
  );
  resources.forEach((r, index) => {
    out.push((index + 1) + '. ' + r.name);
    if (r.description) out.push('What it offers: ' + r.description);
    if (r.next_step) out.push('Suggested next step: ' + r.next_step);
    if (r.public_contact && r.public_contact.phone) out.push('Published phone: ' + r.public_contact.phone);
    out.push('Source: ' + r.official_url);
    out.push('Source reviewed: ' + (r.verification.last_reviewed_on || 'date not available') +
      '. Current services and eligibility must be confirmed.', '');
  });
  out.push(
    'Please confirm details directly with each organization. VHG cannot determine eligibility, guarantee funding, or provide emergency response. For VA claims, contact an accredited representative.', '',
    'Please do not email Social Security numbers, claim identifiers, medical records, or financial documents.', '',
    'Veteran Home Guardians', 'A Voice for All Veterans'
  );
  return out.join('\n');
}

function vhgLocationQuestion_(body, state) {
  const lines = [];
  if (vhgIsUrgent_(body)) lines.push(
    'If anyone is in immediate danger, call 911. For suicidal thoughts or an emotional crisis, call 988 and press 1 for the Veterans Crisis Line, or text 838255. Do not wait for an email reply.', ''
  );
  lines.push('Thank you for contacting Veteran Home Guardians.',
    'To help find relevant local resources, could you tell us the ' + (state ? 'county in ' + VHG_CONFIG.states[state] : 'state and county') + ' where assistance is needed?',
    'Please describe the general type of assistance needed if it was not in your first message.',
    'Do not send Social Security numbers, medical records, claim identifiers or financial documents.',
    '',
    'Veteran Home Guardians');
  return lines.join('\n');
}

/**
 * Workspace time-driven trigger entrypoint. It only creates DRAFTS and labels
 * threads; never replies, forwards, sends or calls an AI provider.
 */
function processVhgInbox() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) return;
  try {
    const query = 'to:' + VHG_CONFIG.helpAddress +
      ' newer_than:' + VHG_CONFIG.searchLookback +
      ' -label:"' + VHG_CONFIG.labelProcessed + '" -in:spam -in:trash';
    const threads = GmailApp.search(query, 0, VHG_CONFIG.maxThreadsPerRun);
    const review = vhgGetLabel_(VHG_CONFIG.labelReview);
    const processed = vhgGetLabel_(VHG_CONFIG.labelProcessed);
    const urgentLabel = vhgGetLabel_(VHG_CONFIG.labelUrgent);
    const locationLabel = vhgGetLabel_(VHG_CONFIG.labelNeedsLocation);
    const aliases = GmailApp.getAliases().map(x => x.toLowerCase());
    const fromOptions = aliases.includes(VHG_CONFIG.helpAddress.toLowerCase())
      ? {from: VHG_CONFIG.helpAddress, name: 'Veteran Home Guardians'} : {name: 'Veteran Home Guardians'};
    const loaded = {};
    threads.forEach(thread => {
      try {
        if (thread.getLabels().some(l => l.getName() === VHG_CONFIG.labelProcessed)) return;
        // One draft per new conversation. Follow-ups to handled threads remain
        // available for human review instead of silently generating duplicates.
        const first = thread.getMessages().find(m =>
          !m.isDraft() && vhgWasAddressedToHelp_(m) &&
          !vhgExtractEmail_(m.getFrom()).endsWith('@vethomeguard.org')
        );
        if (!first) return;
        const from = vhgExtractEmail_(first.getFrom());
        if (!from || /^(?:no.?reply|mailer-daemon|postmaster)@/i.test(from)) return;
        const auto = String(first.getHeader('Auto-Submitted') || '').toLowerCase();
        if (auto && auto !== 'no') return;
        if (first.getHeader('List-Id')) return;
        const body = String(first.getPlainBody() || '').slice(0, VHG_CONFIG.maxBodyChars);
        if (!body.trim()) return;
        const messageText = (first.getSubject() || '') + '\n' + body;
        if (vhgIsUrgent_(messageText)) urgentLabel.addToThread(thread);
        const state = vhgIdentifyState_(messageText);
        let draftText,needsLocation = false;
        if (!state) {
          draftText = vhgLocationQuestion_(messageText, null);needsLocation=true;
        } else {
          if (!loaded[state]) {
            const paths = VHG_CONFIG.files[state];
            loaded[state] = {resources: vhgFetchJson_(paths[0]), counties: vhgFetchJson_(paths[1])};
          }
          const data = loaded[state], county = vhgIdentifyCounty_(messageText, data.counties);
          if (!county) {
            draftText = vhgLocationQuestion_(messageText, state);needsLocation=true;
          } else {
            draftText = vhgMakeDraft_(
              messageText, state, county,
              vhgRankResources_(messageText, data.resources, state, county.county)
            );
          }
        }
        // Replies thread with original message and honors original reply-to.
        // Gmail alias is used only if the account explicitly supports it.
        first.createDraftReply(draftText, fromOptions);
        if (needsLocation) locationLabel.addToThread(thread);
        review.addToThread(thread);
        processed.addToThread(thread);
      } catch (error) {
        // Do not log email content or the sender. An operator can inspect
        // unlabeled threads in the mailbox and Apps Script execution errors.
        console.error('VHG intake processing failed for a thread: ' + error.message);
      }
    });
  } finally {
    lock.releaseLock();
  }
}

/**
 * Run this MANUALLY once after reviewing scopes and configuration.
 * Does not send email. A 5-minute timer polls for new messages.
 */
function installVhgDraftTrigger() {
  const existing = ScriptApp.getProjectTriggers().some(
    t => t.getHandlerFunction() === 'processVhgInbox'
  );
  if (!existing) ScriptApp.newTrigger('processVhgInbox').timeBased().everyMinutes(5).create();
}

/** Run manually to disable scheduled processing. Does not delete drafts. */
function stopVhgDraftTrigger() {
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'processVhgInbox') ScriptApp.deleteTrigger(t);
  });
}

/**
 * Run to validate source accessibility and sender settings.
 * Logs only setup facts, not addresses or incoming mail contents.
 */
function checkVhgDraftConfiguration() {
  const availableSender = GmailApp.getAliases().map(x => x.toLowerCase())
    .includes(VHG_CONFIG.helpAddress.toLowerCase()) ||
    Session.getEffectiveUser().getEmail().toLowerCase() === VHG_CONFIG.helpAddress.toLowerCase();
  const data = vhgFetchJson_(VHG_CONFIG.files.OH[0]);
  console.log('Guide records loaded: ' + data.length +
    '; approved From address in this account: ' + availableSender +
    '; this adapter creates drafts only.');
}
