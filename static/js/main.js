var CurrentHotel = null;

function navigateToItinerary() {
    var address = $('#address').val();
    if (CurrentHotel != null && address == CurrentHotel.name)
        navigateToItineraryByLatLng(CurrentHotel.latitude, CurrentHotel.longitude);
    else
        navigateToItineraryByAddress(address);
}

function navigateToItineraryByLatLng(lat, lng) {
    document.location = '/itinerary?from=' + encodeURIComponent(lat.toString() + ',' + lng.toString());
}

function navigateToItineraryByAddress(address) {
    if(address != '') {
        var geocoder = new google.maps.Geocoder();
        var bounds = new google.maps.LatLngBounds(new google.maps.LatLng(60.28, 29.93), new google.maps.LatLng(59.79, 30.58));
        geocoder.geocode({
            'address' : address,
            'bounds' : bounds
        }, function(results, status) {
            if(status == google.maps.GeocoderStatus.OK) {
                var location = null;
                for(var i = 0; i < results.length; i++) {
                    var latLng = results[i].geometry.location;
                    var lat = latLng.lat();
                    var lng = latLng.lng();
                    var wellType = Math.max($.inArray('street_address', results[i].types), 
                        $.inArray('subpremise', results[i].types),
                        $.inArray('premise', results[i].types));
                    if(lat > 59.79 && lat < 60.28 && lng > 29.93 && lng < 30.58 && wellType >= 0) {
                        location = lat.toString() + ',' + lng.toString();
                        break;                         
                    }
                }
                if (location != null) {
                    navigateToItineraryByLatLng(lat, lng);
                }
                else {
                    if(address.indexOf('St. Petersburg') < 0)
                        navigateToItineraryByAddress(address + ', St. Petersburg, Russia');
                    else
                        alert("Address was not found");
                }
            } else {
                alert("Address was not found for the following reason: " + status);
            }
        });
    }
}

function setupAddressAutocomplete()
{
    $("#address").autocomplete({
            source: "/hotel?out=json",
            minLength: 2,
            focus: function( event, ui ) {
                $("#address").val( ui.item.name );
                return false;
            },
            select: function( event, ui ) {
                $("#address").val( ui.item.name );
                CurrentHotel = ui.item;
                return false;
            }
        })
        .data("autocomplete")._renderItem = function( ul, item ) {
            return $( "<li></li>" )
                .data( "item.autocomplete", item )
                .append( "<a>" + item.name + "</a>" )
                .appendTo( ul );
        };
}

function showDetails(index, action) {
    $("#details_collapsed_" + index.toString()).toggle();
    var id = "#details_expanded_" + index.toString();
    $(id).toggle();

    if(action == 'map' && !initialized[index]) {
        initialized[index] = true;
        var myOptions = {
            mapTypeId : google.maps.MapTypeId.ROADMAP,
            scaleControl : true
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

            if(i == 0 || i == route.length - 1) {
                var marker = new google.maps.Marker({
                    position : point,
                    map : map,
                    title : i == 0 ? "From" : "To"
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
    window.location.href = '/itinerary?from=' + encodeURIComponent(Context.from) + '&transport=' + transport + '&time=' + Context.startTime;
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
