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
 *
 * Sheet columns:
 * A: timestamp | B: uuid | C: display_name | D: tier | E: json_data | F: status
 */

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

    // Generate UUID
    const uuid = Utilities.getUuid();

    // Append row
    sheet.appendRow([
      new Date().toISOString(),           // A: timestamp
      uuid,                                // B: uuid
      data.identity?.display_name || '',   // C: display_name
      data.tier || 0,                      // D: tier
      JSON.stringify(data),                // E: full json
      'pending'                            // F: status (pending → processing → done)
    ]);

    // Return UUID to client
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
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok', service: 'self-insight-form' }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Initialize sheet headers (run once manually)
 */
function initHeaders() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(1, 1, 1, 6).setValues([
    ['timestamp', 'uuid', 'display_name', 'tier', 'json_data', 'status']
  ]);
  sheet.setFrozenRows(1);
}
