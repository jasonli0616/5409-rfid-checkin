function onOpen() {

  updateData();

  // Add update button to menu bar
  let ui = SpreadsheetApp.getUi();
  ui.createMenu("5409 Hours Tracker")
    .addItem("Update data", "updateData")
    .addToUi();
}


function updateData() {

  // Get spreadsheet
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  const sheet = spreadsheet.getSheetByName("Sheet1");
  let hoursSheet = spreadsheet.getSheetByName("Hours");
  let checkedInSheet = spreadsheet.getSheetByName("Checked-in");

  // Create sheets if don't exist
  if (hoursSheet == null)
    hoursSheet = spreadsheet.insertSheet("Hours");
  if (checkedInSheet == null)
    checkedInSheet = spreadsheet.insertSheet("Checked-in");

  // Clear current data
  hoursSheet.clear();
  checkedInSheet.clear();

  // Insert headers
  hoursSheet.getRange("A1:C1").setValues([["Name", "Hours", "Status"]]);
  checkedInSheet.getRange("A1:C1").setValues([["Name", "Hours", "In since"]])

  // Get JSON data
  const data = JSON.parse(sheet.getRange("A1").getDisplayValue());

  for (let i = 0; i < data.length; i++) {

    // Get user data
    let name = data[i]["name"];
    let checkInStatus = data[i]["check_in_status"];
    let since = new Date(data[i]["since"] * 1000);
    let hours = data[i]["elapsed_sec"] / 60 / 60;
    let checkIns = data[i]["check_ins"];
    let checkOuts = data[i]["check_outs"];

    // Write user data
    let hoursRow = hoursSheet.getRange(i+2, 1, 1, 3);
    hoursRow.setValues([[name, hours, checkInStatus ? "in" : "out"]]);

    // Write checked-in user data
    if (checkInStatus == true) {
      let checkedInRow = checkedInSheet.getRange(i+2, 1, 1, 4);
      checkedInRow.setValues([[name, hours, since.toLocaleDateString(), since.toLocaleTimeString()]]);
    }


  }
}
