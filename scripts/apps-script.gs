/**
 * Self-Insight Form Backend — Google Apps Script Web App
 *
 * Setup:
 * 1. Create a new Google Sheet (name: "Self-Insight Submissions")
 * 2. Open Extensions → Apps Script
 * 3. Paste this entire file
 * 4. Set Script Properties (Project Settings → Script Properties):
 *    - LINE_CHANNEL_TOKEN: LINE Messaging API channel access token
 *    - LINE_USER_ID: Yuma's LINE user ID
 * 5. Deploy → New deployment → Web app
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 6. Copy the Web App URL → paste into form/index.html SUBMIT_URL
 *
 * Sheet columns:
 * A: timestamp | B: uuid | C: display_name | D: tier | E: json_data | F: status | G: result_url
 */

const FORM_BASE_URL = 'https://ymatz28-beep.github.io/self-insight/form/';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const uuid = Utilities.getUuid().split('-')[0];

    // Build result URL with base64-encoded data
    const encoded = Utilities.base64Encode(Utilities.newBlob(JSON.stringify(data)).getBytes(), Utilities.Charset.UTF_8);
    const resultUrl = FORM_BASE_URL + '#r=' + encoded;

    // Append row
    sheet.appendRow([
      new Date().toISOString(),
      uuid,
      data.identity?.display_name || '',
      data.tier || 0,
      JSON.stringify(data),
      'pending',
      resultUrl,
    ]);

    // Send LINE notification to Yuma
    sendLineNotification(data.identity?.display_name || '名前なし', data.tier || 0, resultUrl);

    return ContentService
      .createTextOutput(JSON.stringify({ success: true, uuid }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  const action = e?.parameter?.action;

  if (action === 'list') {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const data = sheet.getDataRange().getValues();
    const rows = data.slice(1).map(row => ({
      timestamp: row[0],
      uuid: row[1],
      display_name: row[2],
      tier: row[3],
      status: row[5],
      result_url: row[6] || '',
    }));
    rows.reverse();
    return ContentService
      .createTextOutput(JSON.stringify({ rows }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  if (action === 'get') {
    const uuid = e?.parameter?.uuid;
    if (!uuid) {
      return ContentService.createTextOutput(JSON.stringify({ error: 'uuid required' })).setMimeType(ContentService.MimeType.JSON);
    }
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const data = sheet.getDataRange().getValues();
    for (let i = 1; i < data.length; i++) {
      if (data[i][1] === uuid) {
        return ContentService.createTextOutput(JSON.stringify({
          timestamp: data[i][0], uuid: data[i][1], display_name: data[i][2],
          tier: data[i][3], json_data: data[i][4], status: data[i][5], result_url: data[i][6],
        })).setMimeType(ContentService.MimeType.JSON);
      }
    }
    return ContentService.createTextOutput(JSON.stringify({ error: 'not found' })).setMimeType(ContentService.MimeType.JSON);
  }

  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok', service: 'self-insight-form' }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Send LINE push notification to Yuma when a new form is submitted.
 */
function sendLineNotification(name, tier, resultUrl) {
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty('LINE_CHANNEL_TOKEN');
  const userId = props.getProperty('LINE_USER_ID');
  if (!token || !userId) return;

  const msg = `🔔 Self-Insight 新規回答\n\n` +
    `名前: ${name}\n` +
    `Tier: ${tier}\n\n` +
    `結果を確認:\n${resultUrl}`;

  try {
    UrlFetchApp.fetch('https://api.line.me/v2/bot/message/push', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
      },
      payload: JSON.stringify({
        to: userId,
        messages: [{ type: 'text', text: msg }],
      }),
    });
  } catch (err) {
    // LINE failure should not block form submission
    console.error('LINE notification failed:', err);
  }
}

/**
 * Initialize sheet headers (run once manually in Apps Script editor)
 */
function initHeaders() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(1, 1, 1, 7).setValues([
    ['timestamp', 'uuid', 'display_name', 'tier', 'json_data', 'status', 'result_url']
  ]);
  sheet.setFrozenRows(1);
}
