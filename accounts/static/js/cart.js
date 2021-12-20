$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-sale_item').modal('show');
			},
			success: function(data){
				$('#modal-sale_item .modal-content').html(data.html_form);
			}
		});
	};

	var SaveForm =  function(){
		var form = $(this);
		$.ajax({
			url: form.attr('data-url'),
			data: form.serialize(),
			type: form.attr('method'),
			dataType: 'json',
			success: function(data){
				if(data.form_is_valid){
					$('#sale-table tbody').html(data.sale_list);
					$('#modal-sale_item').modal('hide');
				} else {
					$('#modal-sale_item .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

// create
$(".show-form").click(ShowForm);
$("#modal-sale_item").on("submit",".create-form",SaveForm);

//update
$('#sale-table').on("click",".show-form-update",ShowForm);
$('#modal-book').on("submit",".update-form",SaveForm)

//delete
$('#sale-table').on("click",".show-form-delete",ShowForm);
$('#modal-sale_item').on("submit",".delete-form",SaveForm)
});
