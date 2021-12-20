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

//customers
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-customer').modal('show');
			},
			success: function(data){
				$('#modal-customer .modal-content').html(data.html_form);
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
					$('#customer-table tbody').html(data.customer_list);
					$('#modal-customer').modal('hide');
				} else {
					$('#modal-customer .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

// create
$(".show-form").click(ShowForm);
$("#modal-customer").on("submit",".create-form",SaveForm);

//update
$('#customer-table').on("click",".show-form-update",ShowForm);
$('#modal-customer').on("submit",".update-form",SaveForm)

//delete
$('#customer-table').on("click",".show-form-delete",ShowForm);
$('#modal-customer').on("submit",".delete-form",SaveForm)
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
				$('#modal-product').modal('show');
			},
			success: function(data){
				$('#modal-product .modal-content').html(data.html_form);
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
	$("#modal-product").on("submit",".create-form",SaveForm);

	//update
	$('#product-table').on("click",".show-form-update",ShowForm);
	$('#modal-product').on("submit",".update-form",SaveForm)

	//delete
	$('#product-table').on("click",".show-form-delete",ShowForm);
	$('#modal-product').on("submit",".delete-form",SaveForm)
	});

//users
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-user').modal('show');
			},
			success: function(data){
				$('#modal-user .modal-content').html(data.html_form);
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
					$('#user-table tbody').html(data.user_list);
					$('#modal-user').modal('hide');
				} else {
					$('#modal-user .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

	// create
	$(".show-form").click(ShowForm);
	$("#modal-user").on("submit",".create-form",SaveForm);

	//update
	$('#user-table').on("click",".show-form-update",ShowForm);
	$('#modal-user').on("submit",".update-form",SaveForm)

	//delete
	$('#user-table').on("click",".show-form-delete",ShowForm);
	$('#modal-user').on("submit",".delete-form",SaveForm)
	});

//sales_cart
$(document).ready(function(){
	var SaveForm =  function(){
		var form = $(this);
		$.ajax({
			url: form.attr('data-url'),
			data: form.serialize(),
			type: form.attr('method'),
			dataType: 'json',
			success: function(data){
				if(data.form_is_valid){
					$('#cart-table tbody').html(data.cart_list);
				}
			}
		})
		return false;
	}

	//update
	$('#modal-sale').on("submit",".update-form",SaveForm)

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

//quotation
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-quotation').modal('show');
			},
			success: function(data){
				$('#modal-quotation .modal-content').html(data.html_form);
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
					$('#quotation-table tbody').html(data.quotation_list);
					$('#modal-quotation').modal('hide');
				} else {
					$('#modal-quotation .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

	// create
	$(".show-form").click(ShowForm);
	$("#modal-quotation").on("submit",".create-form",SaveForm);

	//update
	$('#quotation-table').on("click",".show-form-update",ShowForm);
	$('#modal-quotation').on("submit",".update-form",SaveForm)

	//delete
	$('#quotation-table').on("click",".show-form-delete",ShowForm);
	$('#modal-quotation').on("submit",".delete-form",SaveForm)
	});