const SHEET_ID = '1PAGQoTapoPbtJ95d5ysLfHXkfprn1sTRZ6oQ_7JKkEo';

function doGet(e) {
  try {
    const sheetName = e.parameter.sheet;
    if (!sheetName) {
      return asJson_({ error: 'Missing "sheet" parameter' });
    }

    const ss = SpreadsheetApp.openById(SHEET_ID);
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      return asJson_({ error: 'Sheet not found: ' + sheetName });
    }

    const data = sheet.getDataRange().getValues(); // 2D array
    return asJson_(data);

  } catch (err) {
    return asJson_({ error: err.toString() });
  }
}

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents || '{}');
    const action = body.action;
    const ss = SpreadsheetApp.openById(SHEET_ID);

    if (action === 'updateAssignments') {
      const sheet = ss.getSheetByName('Case Tracker');
      if (!sheet) return asJson_({ error: 'Case Tracker sheet not found' });

      const data = sheet.getDataRange().getValues();
      const header = data[0];
      const assigneeColIndex = header.indexOf('Assignee') + 1; // 1-based

      if (assigneeColIndex === 0) {
        return asJson_({ error: 'Assignee column not found' });
      }

      const updates = body.updates || [];
      updates.forEach(update => {
        const row = update.row;        // 1-based row index
        const assignee = update.assignee;
        sheet.getRange(row, assigneeColIndex).setValue(assignee);
      });

      return asJson_({ status: 'ok', updated: updates.length });
    }

    return asJson_({ error: 'Unknown action: ' + action });

  } catch (err) {
    return asJson_({ error: err.toString() });
  }
}

// Helper to return JSON responses
function asJson_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
