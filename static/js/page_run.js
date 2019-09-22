
const expand_dir_view = (event) => {
	$(event.currentTarget).children('#dir-files').slideToggle()  //show()
}

const deleteAction = (path, el_to_delete) => {
	console.log('Path: ', path)
	const url = 'http://127.0.0.1:5000/delete-files/'
	const apiKey = 'emdl%4E60PLWzVpuZomzxQej1U0pMIBYZ10n2DEg@j8uP^Ikp7h#0m1qWLU#K0S' //process.env.API_KEY
	$.ajax({
		url: url,
		headers: {
			'Content-Type': 'application/json',
			'X-Api-Key': apiKey,
			'Delete-Path': path,
		},
		type: "post",
	}).done((res) => {
		if (res.message === 'Update Successful') {
			el_to_delete.removeClass('available')
			el_to_delete.addClass('deleted')
			console.log('El Class', el_to_delete.attr("class").split(/\s+/))
		}
	}).fail(error => {
		console.log(`Error: ${error.status}: ${error.statusText}` )
	})
}

$(window).on('load', function() {
	$('.info-row').on('click', expand_dir_view);
	
	$('.dir-div, .file-div').hover(function(e){
		$(this).find('.delete-btn').show()}, function () {
			$(this).find('.delete-btn').hide()
		});
	
	$('.file-div').on('click', function (e){
		e.preventDefault();
		e.stopPropagation();
	});
	
	$('.delete-btn').on('click', function(e) {
		e.preventDefault();
		e.stopPropagation();
		const path = $(this).data('path')
		let el_to_delete = $(this);
		if ($(this).data('cont') === 'dir') {
			el_to_delete = $(this).parents('div[id="info-row-div"]').eq(0);
		} else if ($(this).data('cont') === 'file') {
			el_to_delete = $(this).parents('div[id="dir-files"]').eq(0);
		} else {
			let el_to_delete = ''
		}
		
		console.log('Element: ', el_to_delete)
		bootbox.confirm({
		    size: 'large',
				title: 'Confirm Delete File',
		    message: 'Are you sure you want to delete:<br><br><b>' + path + '</b><br><br> This cannot be undone!',
		    buttons: {
		        confirm: {
		            label: 'Delete',
		            className: 'btn-danger'
		        },
		        cancel: {
		            label: 'Cancel',
		            className: 'btn-success'
		        }
		    },
		    callback: function(result){
		      console.log('User pick: ', result)
			    if (result){
			    	deleteAction(path, el_to_delete)
			    }
		    }
		})
	});
});
