

function showPopup() {
    var id = '#dialog';

    //Get the screen height and width
    var maskHeight = $(document).height();
    var maskWidth = $(window).width();

    //Set height and width to mask to fill up the whole screen
    $('#mask').css({
        'width' : maskWidth,
        'height' : maskHeight
    });

    //transition effect
    $('#mask').toggle();

    //Get the window height and width
    var winH = $(window).height();
    var winW = $(window).width();

    //Set the popup window to center
    $(id).css('top', winH / 2 - $(id).height() / 2);
    $(id).css('left', winW / 2 - $(id).width() / 2);

    //transition effect
    $(id).toggle();
}

function hidePopup() {
    $('#mask, .window').hide();
}

function goTo(transport) {
    hidePopup();
    Context.transport = transport;
    loadItinerary();
    initialized = new Object(); // reset initialized
}

function alignPopups() {
    var box = $('.window');

    //Get the screen height and width
    var maskHeight = $(document).height();
    var maskWidth = $(window).width();

    //Set height and width to mask to fill up the whole screen
    $('#mask').css({
        'width' : maskWidth,
        'height' : maskHeight
    });

    //Get the window height and width
    var winH = $(window).height();
    var winW = $(window).width();

    //Set the popup window to center
    box.css('top', winH / 2 - box.height() / 2);
    box.css('left', winW / 2 - box.width() / 2);
}


$(document).ready(function() {
    $(window).resize(function() {

        alignPopups();

    });
});

var win=null;
  function printIt(printThis)
  {
    win = window.open();
    win.document.open();
    win.document.write('<'+'html'+'><'+'head'+'><'+'style'+'>');
    win.document.write('body, td { font-family: Verdana; font-size: 10pt;}');
    win.document.write('<'+'/'+'style'+'><'+'/'+'head'+'><'+'body'+'>');
    win.document.write(printThis);
    win.document.write('<'+'/'+'body'+'><'+'/'+'html'+'>');
    win.document.close();
    win.print();
    win.close();
  }