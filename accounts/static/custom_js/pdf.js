window.onload = function(){
    document.getElementById("download-button").addEventListener("click", ()=>{
        const report = this.document.getElementById("report");
        var opt = {
            margin:       1,
            filename:     'sales_report.pdf',
            image:        { type: 'jpeg', quality: 0.05 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
          };
        html2pdf().set(opt).from(report).save();

    })
    document.getElementById("download-button-items").addEventListener("click", ()=>{
        const report = this.document.getElementById("report");
        var opt = {
            margin:       1,
            filename:     'items.pdf',
            image:        { type: 'jpeg', quality: 0.05},
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
          };
        html2pdf().set(opt).from(report).save();

    })
    
}

// window.onload = function(){
//     document.getElementById("download-button-item-table").addEventListener("click", ()=>{
//         const report = this.document.getElementById("item-table");
//         var opt = {
//             margin:       0.05,
//             filename:     'items_list.pdf',
//             image:        { type: 'jpeg', quality: 0.98 },
//             html2canvas:  { scale: 1 },
//             jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
//           };
//         html2pdf().set(opt).from(report).save();

//     })
// }

// window.onload = function(){
//     document.getElementById("download-button-stock-list").addEventListener("click", ()=>{
//         const report = this.document.getElementById("stock-table");
//         var opt = {
//             margin:       0.05,
//             filename:     'stock_list.pdf',
//             image:        { type: 'jpeg', quality: 0.98 },
//             html2canvas:  { scale: 1 },
//             jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
//           };
//         html2pdf().set(opt).from(report).save();

//     })
// }
