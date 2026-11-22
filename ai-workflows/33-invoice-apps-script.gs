// OPTIONAL: PDF invoices with Google Forms + Docs + Gmail (alternative to n8n workflow 33)
// SETUP
//  Create the form: Google Forms → new form with questions titled exactly: Customer name, Email, Product, Quantity, Unit price. | Responses → Link to Sheets → create a new spreadsheet. | In the sheet, add a header Invoice No in the first empty column after the form columns.
//  Create the invoice template: Google Docs → design your invoice (logo, business name, address, bank/JazzCash details). | Type these placeholders where values should go: ##INVOICE## ##DATE## ##NAME## ##ITEM## ##QTY## ##PRICE## ##TOTAL## | Copy the template's ID from its URL (the long code between /d/ and /edit). | Create a Drive folder 'Invoices' and copy its ID from the URL.
//  Install the script: In the response sheet: Extensions → Apps Script → paste the code from the next chapter. | Replace TEMPLATE_ID, FOLDER_ID and BUSINESS at the top. Save. | Triggers (clock icon) → Add trigger → function onFormSubmit → event source: From spreadsheet → event type: On form submit → Save → allow permissions. | Submit a test order with your own email. You should receive the PDF within a minute.

// Skillstack - Order to Invoice automation (Google Apps Script)
const TEMPLATE_ID = 'PASTE_YOUR_GOOGLE_DOC_TEMPLATE_ID';
const FOLDER_ID   = 'PASTE_YOUR_INVOICES_FOLDER_ID';
const BUSINESS    = 'Your Business Name';
const TZ          = 'Asia/Karachi';

function onFormSubmit(e) {
  const v = e.namedValues;
  const name  = v['Customer name'][0];
  const email = v['Email'][0];
  const item  = v['Product'][0];
  const qty   = Number(v['Quantity'][0]);
  const price = Number(v['Unit price'][0]);
  const total = qty * price;
  const now   = new Date();
  const invNo = 'INV-' + Utilities.formatDate(now, TZ, 'yyMMdd-HHmmss');

  // 1) Copy the template and fill the placeholders
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const copy = DriveApp.getFileById(TEMPLATE_ID).makeCopy(invNo, folder);
  const doc = DocumentApp.openById(copy.getId());
  const body = doc.getBody();
  const values = {
    '##INVOICE##': invNo,
    '##DATE##': Utilities.formatDate(now, TZ, 'dd MMM yyyy'),
    '##NAME##': name,
    '##ITEM##': item,
    '##QTY##': String(qty),
    '##PRICE##': 'Rs ' + price.toLocaleString(),
    '##TOTAL##': 'Rs ' + total.toLocaleString()
  };
  Object.keys(values).forEach(function (k) { body.replaceText(k, values[k]); });
  doc.saveAndClose();

  // 2) Save as PDF and email it
  const pdf = copy.getAs(MimeType.PDF).setName(invNo + '.pdf');
  folder.createFile(pdf);
  GmailApp.sendEmail(email, 'Invoice ' + invNo + ' from ' + BUSINESS,
    'Dear ' + name + ',\n\nThank you for your order. Your invoice is attached.\n' +
    'Total: Rs ' + total.toLocaleString() + '\n\nShukriya,\n' + BUSINESS,
    { attachments: [pdf], name: BUSINESS });

  // 3) Write the invoice number next to the response
  const sheet = e.range.getSheet();
  sheet.getRange(e.range.getRow(), e.range.getLastColumn() + 1).setValue(invNo);
}
