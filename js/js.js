var CONTEXT;
var $IMAGES = new Array();
var $THUMBS = new Array();
var OPACITY = 1.0;

$(document).ready(function() {
	init();
});

function getCanvas()  { return $('#mainCanvas') }

function init() {
	$('#searchTerm')
		.change(function(changeEvent) {
			$(this).data('search_index', 0);
		})
		.keypress(function(kpe) {
			if (kpe.keyCode === 13) {
				$('#searchButton').click();
			}
		});
	$('#searchButton').click(function() {
		searchImages( $('#searchTerm').val() );
	})
	.click();

	var $canvas = getCanvas();
	CONTEXT = $canvas[0].getContext('2d');

	$(window).resize(function() {
		var $canvas = $('#mainCanvas');

		var w = $canvas.parent().width() * 0.9;
		$canvas
			.attr('width', w)
			.attr('height', w);
		redraw();
	});
	$(window).resize();
}

/*
images: [{
    "localPath": null,
    "localThumbPath": null,
    "unescapedUrl": "http://www.webexhibits.org/causesofcolor/images/content/blueMorphoZ.jpg",
    "width": "1024",
    "height": "681",
    "tbUrl": "http://t2.gstatic.com/images?q=tbn:ANd9GcTV52rHEUSFXcU_Gh53as_pZHkOesI3B2PwIIS_vzIrhjQBQW_dF8YxDZNH",
    "tbWidth": "150",
    "tbHeight": "100",
    "imageId": "ANd9GcTV52rHEUSFXcU_Gh53as_pZHkOesI3B2PwIIS_vzIrhjQBQW_dF8YxDZNH",
    "imageIndex": 1
    "imageExtesion": "jpg",
}]
*/
function addImage(image) {
	var $img = $('<img/>');
	var $thumb = $('<img/>')
		.addClass('thumbnail selected')
		.attr('src', image.localThumbPath ? localThumbPath : image.tbUrl)
		.click(function() {
			$img.toggleClass('selected');
			$(this).toggleClass('selected');
			updateGlobalOpacity();
			redraw();
		});
	$('<div class="col-xs-4 col-sm-2 col-md-6 col-lg-4 col-xl-3"/>')
		.append($thumb)
		.appendTo( $('#thumbTable') );

	$img
		.addClass('selected')
		.attr('src', image.localPath ? localPath : image.unescapedUrl)
		.load(function() {
			CONTEXT.globalAlpha = OPACITY;
			try {
				var $canvas = getCanvas();
				CONTEXT.drawImage(
					this,
					0, 0, // top, left
					$canvas.width(),
					$canvas.height()
				);
			} catch (error) {
				console.log('Image not ready: '+ $(this).src
					+ '\nImage object: ', $(this), error);
			}
		});

	$IMAGES.push($img);

	updateGlobalOpacity();
}

function searchImages(searchTerm) {
	var searchIndex = $(this).data('search_index');
	if (searchIndex === undefined) {
		searchIndex = 0;
	}

	$(this).data('search_index', searchIndex + 4);

	var apiArgs = {
		'method' : 'getImages',
		'search_term'  : searchTerm,
	    'search_index' : searchIndex
	};
	$.getJSON('./cgi-bin/API.cgi', apiArgs)
		.done(function(json) {
			if ('error' in json) {
				if ('trace' in json) {
					console.log(json.trace);
				}
				throw new Error('Error: ' + json.error);
			}
			if (!('images' in json)) {
				throw new Error('"images" not returned by API');
			}
			// Iterate over images and add them.
			for (var arrIndex = 0;
				     arrIndex < json.images.length;
				     arrIndex++) {
				addImage(json.images[arrIndex]);
			}
		})
		.fail(function() {
			console.log('Failure to complete request to /cgi-bin/API.cgi');
		});
}

function redraw() {
	var $canvas = getCanvas();
	CONTEXT.clearRect(0, 0, $canvas.width(), $canvas.height());
	for (var i = 0; i < $IMAGES.length; i++) {
		if ($IMAGES[i].hasClass('selected')) {
			$IMAGES[i].load();
		}
	}
}

function getVisibleImageCount() {
	var count = 0;
	for (var i = 0; i < $IMAGES.length; i++ ){
		if ($IMAGES[i].hasClass('selected')) {
			count++;
		}
	}
	return count;
}

function updateGlobalOpacity() {
	var visibleImages = Math.max(getVisibleImageCount(), 1);
	OPACITY = 1.0 / visibleImages;
}
