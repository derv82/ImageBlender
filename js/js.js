var CONTEXT;
var $IMAGES = new Array();
var $THUMBS = new Array();
var OPACITY = 1.0;

$(document).ready(function() {
	init();
});

function getCanvas()  { return $('#mainCanvas') }

function init() {
	// Setup button/text event handlers
	$('#searchTerm')
		.on('input', function(changeEvent) {
			$(this).data('search_index', 0);
			$IMAGES = new Array();
			$('#thumbTable').empty();
			redraw();
			$('#thumbnailCount').text("(" + getVisibleImageCount() + "/" + $IMAGES.length + ")");
		})
		.keypress(function(kpe) {
			if (kpe.keyCode === 13) {
				$('#searchButton').click();
			}
		});
	$('#searchButton').click(function() {
		searchImages( $('#searchTerm').val() );
	})
	.click(); // Load images

	getSearchTerms();

	// Setup HTML5 canvas
	var $canvas = getCanvas();
	CONTEXT = $canvas[0].getContext('2d');

	$(window).resize(function() {
		var $canvas = $('#mainCanvas');

		var w = $canvas.parent().width() - $canvas.position().left / 2;
		$canvas
			.attr('width', w)
			.attr('height', w);
		redraw();
		$('#sliderObject').width('100%');
	});
	
	// Setup colorpicker
	$('.colorPicker')
		.colorpicker({
			'format' : 'rgba',
			'color' : $canvas.css('background-color')
		})
		.on('changeColor', function (ev) {
			var rgba = ev.color.toRGB();
			var color = "rgba("
			 + rgba.r + ", "
			 + rgba.g + ", "
			 + rgba.b + ", "
			 + rgba.a + ")";
			getCanvas().css('background-color', color);
			$('html,body').css('background-color', color);
		});
	$('#imageColor').val('rgba(255, 255, 255, 1)');

	$('#imageOpacity')
		.slider({
			id: 'sliderObject',
			min: 0.0,
			max: 1.0,
			step: 0.05,
			selection: 'none',
			tooltip: 'show',
			formater: function(input) {
				return (input.toFixed(2) * 100) + '%';
			}
		})
		.on('slide', function(ev) {
			OPACITY = ev.value;
			redraw();
		});

	// Alert message close button
	$('.close')
		.click(function() {
			$('.message').hide()
		});

	// Setup navigation
	pageChanged();
	$(window).bind('popstate', function(e) {
		pageChanged();
		e.stopPropagation();
	});
}

/* Triggers a page load */
function pageChanged() {
	$('a:focus').blur();
	$('.nav li').removeClass('active');
	$('.page')
		.slideUp(200)
		.fadeOut(200);

	var keys = getQueryHashKeys(),
	    pageID = 'home';

	if ('gallery' in keys) {
		pageID = 'gallery';
		$('#searchInputs').hide();
	} else {
		pageID = 'home';
		$('#searchInputs').show();
	}

	$('#' + pageID + 'Container')
		.stop()
		.hide()
		.slideDown(500)
		.fadeIn(500);
	$('#' + pageID + 'Nav')
		.addClass('active');
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
		.addClass('thumbnail thumbnail-sm active btn-success')
		.attr('src', image.localThumbPath ? localThumbPath : image.tbUrl)
		.click(function() {
			$img.toggleClass('active');
			$(this).toggleClass('active');
			$(this).toggleClass('btn-success');
			$(this).toggleClass('btn-danger');
			updateGlobalOpacity();
			redraw();
			$('#thumbnailCount').text("(" + getVisibleImageCount() + "/" + $IMAGES.length + ")");
		});
	$('<div class="col-xs-6 col-sm-2 col-md-6 col-lg-4 col-xl-3"/>')
		.append($thumb)
		.prependTo( $('#thumbTable') );

	$img
		.addClass('active')
		.attr('id', image.imageId)
		.attr('src', image.localPath ? image.localPath : image.unescapedUrl)
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
		})
		.appendTo('body')
		.hide();

	if (!image.localPath) {
		downloadImage(image);
	}

	$IMAGES.push($img);

	updateGlobalOpacity();
}

function downloadImage(image) {
	// Tell the server to download this image
	var apiArgs = {
		'method' : 'downloadImage',
		'searchTerm' : $('#searchTerm').val(),
		'url' : image.unescapedUrl,
		'imageID' : image.imageId,
		'imageIndex' : image.imageIndex,
	};
	$.getJSON('./cgi-bin/API.cgi', apiArgs)
		.done(function(json) {
			if ('error' in json) {
				if ('trace' in json) {
					displayError(json.error, json.trace);
				}
				else {
					displayError(json.error);
				}
			}
			/*
			'json' response looks like:
			{
				url: <path to local image>,
			}
			*/
			// replace existing <img> src with json.url
			$('#' + json.imageID)
				.attr('src', '')
				.attr('src', json.url);
		})
		.fail(function(jqXHR, statusText, errorThrown) {
			displayError('statusText: ' + statusText, 'responseText: ' + jqXHR.responseText);
		});
}

function searchImages(searchTerm) {
	$('#searchButton').addClass('active');
	var searchIndex = $('#searchTerm').data('search_index');
	if (searchIndex === undefined) {
		searchIndex = 0;
	}

	var apiArgs = {
		'method' : 'getImages',
		'search_term'  : searchTerm,
	    'search_index' : searchIndex
	};
	$.getJSON('./cgi-bin/API.cgi', apiArgs)
		.done(function(json) {
			$('#searchButton').removeClass('active');
			if ('error' in json) {
				if ('trace' in json) {
					displayError(json.error, json.trace);
				}
				else {
					displayError(json.error);
				}
			}
			
			if (!('images' in json)) {
				displayError('No images found.');
			}

			// Iterate over images and add them.
			for (var arrIndex = 0;
				     arrIndex < json.images.length;
				     arrIndex++) {
				addImage(json.images[arrIndex]);
			}
			$('#searchTerm').data('search_index', searchIndex + 4);
			//$('#searchButton').text('Get More Images');
			$('#thumbnailCount').text("(" + getVisibleImageCount() + "/" + $IMAGES.length + ")");
		})
		.fail(function(jqXHR, statusText, errorThrown) {
			displayError('statusText: ' + statusText, 'responseText: ' + jqXHR.responseText);
		});
}

function displayError(title, stackTrace) {
	$('#searchButton').removeClass('active');
	
	$('#errorTitle').html(title);
	if (stackTrace !== undefined) {
		var htmlTrace = $('<div/>').text(stackTrace).html();
		$("#errorBody")
			.html(htmlTrace)
			.fadeIn(1000);
	}
	else {
		$('errorBody').hide();
	}
	$('.message')
		.hide()
		.slideDown();
	
	//throw new Error( title + "\n" + ((stackTrace) ? stackTrace : "") );
}

function getSearchTerms(start, count) {
	if (start === undefined) { start =  0; }
	if (count === undefined) { count = 20; }

	var apiArgs = {
		'start'  : start,
		'count'  : count,
		'method' : 'getSearchTerms'
	};

	$.getJSON('./cgi-bin/API.cgi', apiArgs)
		.done(function(json) {
			if ('error' in json) {
				if ('trace' in json) {
					displayError(json.error, json.trace);
				}
				else {
					displayError(json.error);
				}
			}

			if (!('terms' in json)) {
				displayError('No terms found.');
			}

			// Iterate over images and add them.
			for (var arrIndex = 0;
				     arrIndex < json.terms.length;
				     arrIndex++) {
				$('<div/>')
					.addClass('col-xs-12')
					.html(json.terms[arrIndex])
					.appendTo('#termsDiv');
			}
		})
		.fail(function(jqXHR, statusText, errorThrown) {
			displayError('statusText: ' + statusText, 'responseText: ' + jqXHR.responseText);
		});
}

function saveImage() {
	$.ajax({
		type: "POST",
		url: "script.php",
		data: { 
			'method' : 'saveImage',
			'searchTerm' : $('#searchTerm').val(),
			'visibleImageCount' : getVisibleImageCount(),
			'extension' : 'png',
			'base64' : getCanvas().toDataURL('image/jpeg', 0.95)
		}
	})
	.done(function(json) {
		// TODO show saved image link, redirect?
		displayError(JSON.stringify(json));
	})
	.fail(function(jqXHR, statusText, errorThrown) {
		displayError('statusText: ' + statusText, 'responseText: ' + jqXHR.responseText);
	});
}

function getQueryHashKeys() {
	var a = window.location.hash.substring(1).split('&');
	if (a == "") return {};
	var b = {};
	for (var i = 0; i < a.length; ++i) {
		var keyvalue = a[i].split('=');
		var key = keyvalue[0];
		keyvalue.shift(); // Remove first element (key)
		var value = keyvalue.join('='); // Remaining elements are the value
		b[key] = decodeURIComponent(value); //.replace(/\+/g, " "));
	}
	return b;
}

function redraw() {
	var $canvas = getCanvas();
	CONTEXT.clearRect(0, 0, $canvas.width(), $canvas.height());
	for (var i = 0; i < $IMAGES.length; i++) {
		if ($IMAGES[i].hasClass('active')) {
			$IMAGES[i].load();
		}
	}
}

function getVisibleImageCount() {
	var count = 0;
	for (var i = 0; i < $IMAGES.length; i++ ){
		if ($IMAGES[i].hasClass('active')) {
			count++;
		}
	}
	return count;
}

function updateGlobalOpacity() {
	var visibleImages = Math.max(getVisibleImageCount(), 1);
	OPACITY = 1.0 / visibleImages;
	$('#imageOpacity')
		.val(OPACITY.toFixed(2))
		.slider('setValue', OPACITY.toFixed(2));
}
