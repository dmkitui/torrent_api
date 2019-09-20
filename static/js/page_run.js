
const expand_dir_view = (event) => {
	console.log('clicked')
	console.log('Event: ', event)
	const div = $(event.currentTarget)
	
//	const file_divs = div.getElementsByClassName('file-div')
	$(event.currentTarget).children('#dir-files').slideToggle()  //show()
}

$(window).on('load', function() {
	console.log('We here hommies')
	$('.info-row').on('click', expand_dir_view);
});