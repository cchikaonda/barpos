console.log("Hello World")

const spinnerBox = document.getElementById('spinner-box')
const dataBox = document.getElementById('data-box')
const salesReportTable = document.getElementById('page-content')
// salesReportTable.classList.add('not-visible')

$.ajax({
      type: 'GET',
      url: '/reports/sales_report_data',
      success: function(response){
          setTimeout(()=>{
            spinnerBox.classList.add('not-visible')
            salesReportTable.classList.remove('not-visible')
          }, 600)
             
      },
      error: function(error){
          console.log(error)
      }
    })

