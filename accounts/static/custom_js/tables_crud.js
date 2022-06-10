//customer
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


//customer dash pos
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-customer-dash').modal('show');
			},
			success: function(data){
				$('#modal-customer-dash .modal-content').html(data.html_form);
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
					// $('#customer-list value').html(data.customer_list);
					$( "#customer-list" ).load(window.location.href + " #customer-list" );
					$('#modal-customer-dash').modal('hide');
				} else {
					$('#modal-customer-dash .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

// create
$(".show-form").click(ShowForm);
$("#modal-customer-dash").on("submit",".create-form",SaveForm);

//update
$('#customer-table-dash').on("click",".show-form-update",ShowForm);
$('#modal-customer-dash').on("submit",".update-form",SaveForm)

//delete
$('#customer-table-dash').on("click",".show-form-delete",ShowForm);
$('#modal-customer-dash').on("submit",".delete-form",SaveForm)
    });


//customer pos
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-customer-pos').modal('show');
			},
			success: function(data){
				$('#modal-customer-pos .modal-content').html(data.html_form);
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
					$('#customer-table-pos tbody').html(data.customer_list);
					$('#modal-customer-pos').modal('hide');
				} else {
					$('#modal-customer-pos .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

// create
$(".show-form").click(ShowForm);
$("#modal-customer-pos").on("submit",".create-form",SaveForm);

//update
$('#customer-table-pos').on("click",".show-form-update",ShowForm);
$('#modal-customer-pos').on("submit",".update-form",SaveForm)

//delete
$('#customer-table-pos').on("click",".show-form-delete",ShowForm);
$('#modal-customer-pos').on("submit",".delete-form",SaveForm)
    });


//supplier
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-supplier').modal('show');
			},
			success: function(data){
				$('#modal-supplier .modal-content').html(data.html_form);
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
					$('#supplier-table tbody').html(data.supplier_list);
					$('#modal-supplier').modal('hide');
				} else {
					$('#modal-supplier .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

// create
$(".show-form").click(ShowForm);
$("#modal-supplier").on("submit",".create-form",SaveForm);

//update
$('#supplier-table').on("click",".show-form-update",ShowForm);
$('#modal-supplier').on("submit",".update-form",SaveForm)

//delete
$('#supplier-table').on("click",".show-form-delete",ShowForm);
$('#modal-supplier').on("submit",".delete-form",SaveForm)
    });


//batch
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-batch').modal('show');
			},
			success: function(data){
				$('#modal-batch .modal-content').html(data.html_form);
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
					$('#batch-table tbody').html(data.batch_list);
					location.reload();
					$('#modal-batch').modal('hide');
				} else {
					$('#modal-batch .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

	// create
	$(".show-form").click(ShowForm);
	$("#modal-batch").on("submit",".create-form",SaveForm);

	//update
	$('#batch-table').on("click",".show-form-update",ShowForm);
	$('#modal-batch').on("submit",".update-form",SaveForm)

	//delete
	$('#batch-table').on("click",".show-form-delete",ShowForm);
	$('#modal-batch').on("submit",".delete-form",SaveForm)
	});


//stock
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-stock').modal('show');
			},
			success: function(data){
				$('#modal-stock .modal-content').html(data.html_form);
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
					$('#stock-table tbody').html(data.stock_list);
					location.reload();
					$('#modal-stock').modal('hide');
				} else {
					$('#modal-stock .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

	// create
	$(".show-form").click(ShowForm);
	$("#modal-stock").on("submit",".create-form",SaveForm);

	//update
	$('#stock-table').on("click",".show-form-update",ShowForm);
	$('#modal-stock').on("submit",".update-form",SaveForm)

	//delete
	$('#stock-table').on("click",".show-form-delete",ShowForm);
	$('#modal-stock').on("submit",".delete-form",SaveForm)
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
					$('#unit-table tbody').html(data.unit_list)
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
				$('#modal-item ').modal('show');
			},
			success: function(data){
				$('#modal-item .modal-content').html(data.html_form);
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
					$('#item-table tbody').html(data.item_list);
					$('#modal-item').modal('hide');
				} else {
					$('#modal-item .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

	// create
	$(".show-form").click(ShowForm);
	$("#modal-item ").on("submit",".create-form",SaveForm);

	//update
	$('#item-table').on("click",".show-form-update",ShowForm);
	$('#modal-item').on("submit",".update-form",SaveForm)

	//delete
	$('#item-table').on("click",".show-form-delete",ShowForm);
	$('#modal-item ').on("submit",".delete-form",SaveForm)
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


//expenses category
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-expense-category').modal('show');
			},
			success: function(data){
				$('#modal-expense-category .modal-content').html(data.html_form);
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
					$('#expenses-table tbody').html(data.expense_category_list);
					$('#modal-expense-category').modal('hide');
					location.reload();
				} else {
					$('#modal-expense-category .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

	// create
	$(".show-form").click(ShowForm);
	$("#modal-expense-category").on("submit",".create-form",SaveForm)

	//update
	$('#expenses-category-table').on("click",".show-form-update",ShowForm);
	$('#modal-expense-category').on("submit",".update-form",SaveForm)

	//delete
	$('#expenses-category-table').on("click",".show-form-delete",ShowForm);
	$('#modal-expense-category').on("submit",".delete-form",SaveForm)
	});

	
//expenses
$(document).ready(function(){
	var ShowForm = function(){
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType:'json',
			beforeSend: function(){
				$('#modal-expense').modal('show');
			},
			success: function(data){
				$('#modal-expense .modal-content').html(data.html_form);
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
					$('#expenses-table tbody').html(data.expense_list);
					$('#modal-expense').modal('hide');
					location.reload();
				} else {
					$('#modal-expense .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

	// create
	$(".show-form").click(ShowForm);
	$("#modal-expense").on("submit",".create-form",SaveForm);

	//update
	$('#expenses-table').on("click",".show-form-update",ShowForm);
	$('#modal-expense').on("submit",".update-form",SaveForm)

	//delete
	$('#expenses-table').on("click",".show-form-delete",ShowForm);
	$('#modal-expense').on("submit",".delete-form",SaveForm)
	});