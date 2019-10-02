const appCredentials = appConfig

const DELETE_URL = appCredentials.DELETE_URL
const API_KEY = appCredentials.API_KEY

console.log('DELETE URL: ', DELETE_URL)

const expand_dir_view = (event) => {
	$(event.currentTarget).closest('.dir-div').toggleClass('expanded-dir')
	$(event.currentTarget).children('.dir-name').find('i').toggleClass('fa-folder-open-o')
	$(event.currentTarget).children('.dir-name').find('.dir-metadata').slideToggle()
	$(event.currentTarget).siblings('.dir-content').slideToggle()
}

const deleteAction = (path, el_to_delete) => {
	$.ajax({
		url: DELETE_URL,
		headers: {
			'Content-Type': 'application/json',
			'X-Api-Key': API_KEY,
			'Delete-Path': path,
		},
		type: "post",
	}).done((res) => {
		if (res.message === 'Update Successful') {
			el_to_delete.removeClass('available')
			el_to_delete.addClass('deleted')
		}
	}).fail(error => {
		console.log(`Error: ${error.status}: ${error.statusText}` )
	})
}

$(window).on('load', function() {
	$('.directory-row').on('click', expand_dir_view);
	
	$('.file-div').hover(function(e){
		$(this).find('.delete-btn').show()}, function () {
			$(this).find('.delete-btn').hide()
		});
	$('.directory-row').hover(function(e){
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
			    if (result){
			    	deleteAction(path, el_to_delete)
			    }
		    }
		})
	});
});
