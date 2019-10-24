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
	let parent;
	if (el_to_delete.data('cont') === 'dir') {
		parent = el_to_delete.parents('div[id="info-row-div"]').eq(0);
	} else if (el_to_delete.data('cont') === 'file') {
		parent = el_to_delete.parents('div[id="dir-files"]').eq(0);
	} else {
		parent = ''
	}
  const spinner = document.createElement('i')
  spinner.alt = 'delete action'
  spinner.setAttribute('class', 'fa fa-spinner fa-spin');
  spinner.setAttribute('style', 'font-size:24px;color:red;');
  console.log('Element: ', el_to_delete);
  el_to_delete.replaceWith(spinner)
	
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
			spinner.remove()
			parent.removeClass('available')
			parent.addClass('deleted')
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
