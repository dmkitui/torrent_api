
const expand_dir_view = (event) => {
	const div = $(event.currentTarget)
	$(event.currentTarget).children('#dir-files').slideToggle()  //show()
}

$(window).on('load', function() {
	console.log('We here hommies')
	$('.info-row').on('click', expand_dir_view);
	
	$('.info-row').hover(function(){
		console.log('Are we hovering?')
		$(this).find('.delete-btn').show()}, function () {
			$(this).find('.delete-btn').hide()
		});
});

$(document).on("click", ".delete-btn", function(e) {
	const path = $(this).data('path')
	console.log('Path: ', path)
	e.preventDefault()
	e.stopPropagation();
	bootbox.confirm({
	    size: "large",
			title: 'Confirm Delete File',
	    message: "Are you sure you want to delete:<br><br><b>" + path + "</b><br><br> This cannot be undone!",
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
