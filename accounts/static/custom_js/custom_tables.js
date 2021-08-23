$(function () {
    $("#unpaid_orders_table").DataTable({
        "responsive": true,
        "autoWidth": false,
    });
    $("#search_item_table").DataTable({
        "responsive": true,
        "autoWidth": false,
    });
    $("#unsettled_orders_table").DataTable({
        "responsive": true,
        "autoWidth": false,
    });
    $("#sales_report_table").DataTable({
        "responsive": true,
        "autoWidth": false,
    });
    
    $('#example2').DataTable({
        "paging": true,
        "lengthChange": false,
        "searching": false,
        "ordering": true,
        "info": true,
        "autoWidth": false,
        "responsive": true,
    });
    });
