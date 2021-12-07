document.getElementById('download-excel-button').addEventListener('click', function(){
    var table2excel = new Table2Excel(
        'table', {
            plugins: [{
              worksheetCompleted ({ workbook, tables, worksheet, table }) {
                worksheet.getRow(1).hidden = true
                worksheet.getColumn(1).hidden = true
              }
            }]
          }
    );
    table2excel.export(document.querySelectorAll("#sales_report_table"))
});

document.getElementById('download-excel-button').addEventListener('click', function(){
  var table2excel = new Table2Excel(
      'table', {
          plugins: [{
            worksheetCompleted ({ workbook, tables, worksheet, table }) {
              worksheet.getRow(1).hidden = true
              worksheet.getColumn(1).hidden = true
            }
          }]
        }
  );
  table2excel.export(document.querySelectorAll("#item-table"))
});

document.getElementById('download-excel-button').addEventListener('click', function(){
  var table2excel = new Table2Excel(
      'table', {
          plugins: [{
            worksheetCompleted ({ workbook, tables, worksheet, table }) {
              worksheet.getRow(1).hidden = true
              worksheet.getColumn(1).hidden = true
            }
          }]
        }
  );
  table2excel.export(document.querySelectorAll("#stock-table"))
});