var CONTEXT;
var $IMAGES = new Array();
var $THUMBS = new Array();
var OPACITY = 1.0;

$(document).ready(function() {
	init();
});

function getCanvas()  { return $('#mainCanvas') }

function init() {
	var $canvas = getCanvas();
	CONTEXT = $canvas[0].getContext('2d');

	for (var i = 1; i <= 4; i++ ){
		addImage(i + '.jpg');
	}

	$canvas
		.mousedown(function(e) {
			$(this)
				.css('opacity', 0.5)
				.data('mouseData', {
					lastX: e.pageX,
					lastY: e.pageY
				});
			$(this).mousemove(canvasMouseMoveHandler);
		})
		.mouseup(function(e) {
			$(this)
				.css('opacity', 1.0)
				.unbind('mousemove');
			redraw();
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

function canvasMouseMoveHandler(e) {
	if (e.buttons != 1) { return; }
	var pageX = e.pageX, pageY = e.pageY;
	this.width  -= $(this).data('mouseData').lastX - pageX;
	this.height -= $(this).data('mouseData').lastY - pageY;
	$(this).data('mouseData').lastX = pageX;
	$(this).data('mouseData').lastY = pageY;
	redraw();
}

function addImage(url) {
	var $img = $('<img/>');
	var $thumb = $('<img/>')
		.addClass('thumbnail selected')
		.attr('src', url)
		.click(function() {
			$img.toggleClass('selected');
			$(this).toggleClass('selected');
			updateGlobalOpacity();
			redraw();
		});
	$('#thumbTable')
		.append($thumb);

	$img
		.attr('src', url)
		.addClass('selected')
		.load(function() {
			var $canvas = getCanvas();
			CONTEXT.globalAlpha = OPACITY;
			CONTEXT.drawImage(
				this,
				0, 0, // top, left
				$canvas.width(),
				$canvas.height()
			);
		});
	$IMAGES.push($img);
	updateGlobalOpacity();
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
