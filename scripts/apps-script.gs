/**
 * Self-Insight Form Backend — Google Apps Script Web App
 *
 * Setup:
 * 1. Create a new Google Sheet (name: "Self-Insight Submissions")
 * 2. Open Extensions → Apps Script
 * 3. Paste this entire file
 * 4. Deploy → New deployment → Web app
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 5. Copy the Web App URL → paste into form/index.html SUBMIT_URL
 *    and form/admin.html API URL
 *
 * Sheet columns:
 * A: timestamp | B: uuid | C: display_name | D: tier | E: json_data | F: status
 */

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

    // Generate short UUID (8 chars)
    const uuid = Utilities.getUuid().split('-')[0];

    // Append row
    sheet.appendRow([
      new Date().toISOString(),           // A: timestamp
      uuid,                                // B: uuid
      data.identity?.display_name || '',   // C: display_name
      data.tier || 0,                      // D: tier
      JSON.stringify(data),                // E: full json
      'pending'                            // F: status (pending → done)
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ success: true, uuid: uuid }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  const action = e?.parameter?.action;

  // List all submissions (for admin page)
  if (action === 'list') {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    const rows = data.slice(1).map(row => ({
      timestamp: row[0],
      uuid: row[1],
      display_name: row[2],
      tier: row[3],
      status: row[5],
    }));
    // Most recent first
    rows.reverse();
    return ContentService
      .createTextOutput(JSON.stringify({ rows }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  // Get single submission by UUID
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
          timestamp: data[i][0],
          uuid: data[i][1],
          display_name: data[i][2],
          tier: data[i][3],
          json_data: data[i][4],
          status: data[i][5],
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
 * Initialize sheet headers (run once manually in Apps Script editor)
 */
function initHeaders() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(1, 1, 1, 6).setValues([
    ['timestamp', 'uuid', 'display_name', 'tier', 'json_data', 'status']
  ]);
  sheet.setFrozenRows(1);
}
