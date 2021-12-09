//Item units
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-unit').modal('show');
			},
			success: function(data){
				$('#modal-unit .modal-content').html(data.html_form);
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
					$('#unit-table tbody').html(data.unit_list);
					$('#modal-unit').modal('hide');
				} else {
					$('#modal-unit .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

// create
$(".show-form").click(ShowForm);
$("#modal-unit").on("submit",".create-form",SaveForm);

//update
$('#unit-table').on("click",".show-form-update",ShowForm);
$('#modal-unit').on("submit",".update-form",SaveForm)

//delete
$('#unit-table').on("click",".show-form-delete",ShowForm);
$('#modal-unit').on("submit",".delete-form",SaveForm)
});

//Products/items
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-product ').modal('show');
			},
			success: function(data){
				$('#modal-product  .modal-content').html(data.html_form);
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
					$('#product-table tbody').html(data.item_list);
					$('#modal-product').modal('hide');
				} else {
					$('#modal-product .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

	// create
	$(".show-form").click(ShowForm);
	$("#modal-product ").on("submit",".create-form",SaveForm);

	//update
	$('#product-table').on("click",".show-form-update",ShowForm);
	$('#modal-product ').on("submit",".update-form",SaveForm)

	//delete
	$('#product-table').on("click",".show-form-delete",ShowForm);
	$('#modal-product ').on("submit",".delete-form",SaveForm)
	});

//category
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-category').modal('show');
			},
			success: function(data){
				$('#modal-category .modal-content').html(data.html_form);
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
					$('#category-table tbody').html(data.category_list);
					$('#modal-category').modal('hide');
				} else {
					$('#modal-category .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

	// create
	$(".show-form").click(ShowForm);
	$("#modal-category").on("submit",".create-form",SaveForm);

	//update
	$('#category-table').on("click",".show-form-update",ShowForm);
	$('#modal-category').on("submit",".update-form",SaveForm)

	//delete
	$('#category-table').on("click",".show-form-delete",ShowForm);
	$('#modal-category').on("submit",".delete-form",SaveForm)
	});
