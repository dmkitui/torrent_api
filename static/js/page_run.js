
const expand_dir_view = (event) => {
	$(event.currentTarget).children('#dir-files').slideToggle()  //show()
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
		    }
		})
	});
});
