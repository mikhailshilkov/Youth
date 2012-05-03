function showDetails(index, action) {
    $("#details_collapsed_" + index.toString()).toggle();
    var id = "#details_expanded_" + index.toString();
    $(id).toggle();

    if(action == 'map' && !initialized[index]) {
        initialized[index] = true;
        var myOptions = {
            mapTypeId : google.maps.MapTypeId.ROADMAP
        };
        var mapPane = $(id + " .details");
        mapPane.css('width', '100%');
        mapPane.css('height', '300px');
        var map = new google.maps.Map(mapPane.get(0), myOptions);

        var bounds = new google.maps.LatLngBounds();
        var flightPlanCoordinates = [];
        var route = eval('Context.route' + index.toString());
        for(var i = 0; i < route.length; i++) {
            var step = route[i];
            var point = new google.maps.LatLng(step['lat'], step['lng']);
            flightPlanCoordinates.push(point);
            bounds.extend(point);

            if (i == 0 || i == route.length - 1)
            {
                var marker = new google.maps.Marker({
                    position : point,
                    map : map,
                    title : "Hello World!"
                });
            }

        }
        var flightPath = new google.maps.Polyline({
            path : flightPlanCoordinates,
            strokeColor : "#6666FF",
            strokeOpacity : 0.8,
            strokeWeight : 5
        });
        flightPath.setMap(map);
        map.fitBounds(bounds);
    }
}

var initialized = new Object();

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
    window.location.href = '/?transport=' + transport + '&time=' + Context.startTime;
}


$(document).ready(function() {
    $(window).resize(function() {

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

    });
});
