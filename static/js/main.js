var CurrentHotel = null;
var CurrentTime = null;
var CurrentDate = null;

function navigateToItinerary() {
    CurrentDate = $("#datepicker").datepicker('getDate');
    if(CurrentDate == null) {
        alert('Wrong date');
        return;
    }
    CurrentTime = formatTime($('#timepicker').val());
    if(!CurrentTime) {
        alert('Wrong time');
        return;
    }

    var address = $('#address').val();
    if(CurrentHotel != null && address == CurrentHotel.name)
        navigateToItineraryByLatLng(CurrentHotel.latitude, CurrentHotel.longitude);
    else
        navigateToItineraryByAddress(address);
}

function navigateToItineraryByLatLng(lat, lng) {
    document.location = '/itinerary?from=' + lat.toString() + '-' + lng.toString() + '&date=' + $.datepicker.formatDate('yy-mm-dd', CurrentDate) + '&time=' + CurrentTime.replace(':', '-');
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
                    var wellType = Math.max($.inArray('street_address', results[i].types), $.inArray('subpremise', results[i].types), $.inArray('premise', results[i].types));
                    if(lat > 59.79 && lat < 60.28 && lng > 29.93 && lng < 30.58 && wellType >= 0) {
                        navigateToItineraryByLatLng(lat.toString(), lng.toString());
                        break;
                    }
                }
                if(location != null) {
                    navigateToItineraryByLatLng(lat, lng);
                } else {
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

function setupHomeInputs() {
    $("#address").autocomplete({
        source : "/hotel?out=json",
        minLength : 2,
        focus : function(event, ui) {
            $("#address").val(ui.item.name);
            return false;
        },
        select : function(event, ui) {
            $("#address").val(ui.item.name);
            CurrentHotel = ui.item;
            return false;
        }
    }).data("autocomplete")._renderItem = function(ul, item) {
        return $("<li></li>").data("item.autocomplete", item).append("<a>" + item.name + "</a>").appendTo(ul);
    };

    $("#datepicker").datepicker({
        minDate : 0,
        maxDate : "+6M"
    });
    $("#datepicker").datepicker("option", "dateFormat", "dd MM yy");
    $("#datepicker").datepicker('setDate', new Date().setDate(new Date().getDate() + 1));
}

function showDetails(index, action, route) {
    $("#details_collapsed_" + index.toString()).toggle();
    var id = "#details_expanded_" + index.toString();
    $(id).toggle();

    if(action == 'map' && !initialized[index]) {
        initialized[index] = true;
        var mapPane = $(id + " .details");
        mapPane.css('width', '100%');
        mapPane.css('height', '300px');

        showDetailsMap(mapPane, eval('(' + route + ')'));
    }
}

function showDetailsMap(mapPane, route) {
    var myOptions = {
        mapTypeId : google.maps.MapTypeId.ROADMAP,
        scaleControl : true
    };
    var map = new google.maps.Map(mapPane.get(0), myOptions);
    var bounds = new google.maps.LatLngBounds();
    var coordinates = [];
    var startPoint = new google.maps.LatLng(route['start']['lat'], route['start']['lng']);
    var endPoint = new google.maps.LatLng(route['end']['lat'], route['end']['lng']);
    coordinates.push(startPoint);
    bounds.extend(startPoint);
    mapAddMarker(map, startPoint, 'From');

    var needsDirections = route['type'] != 'Subway';
    if(route['type'] == 'Walk')// don't search directions for walks < 200 m
        needsDirections = google.maps.geometry.spherical.computeDistanceBetween(startPoint, endPoint) > 200;
    if(needsDirections) {
        var request = {
            origin : startPoint,
            destination : endPoint,
            travelMode : route['type'] == 'Walk' ? google.maps.TravelMode.WALKING : google.maps.TravelMode.DRIVING
        };
        var directionsService = new google.maps.DirectionsService();
        directionsService.route(request, function(result, status) {
            if(status == google.maps.DirectionsStatus.OK) {
                steps = result.routes[0].legs[0].steps;
                for(var i = 0; i < steps.length - 1; i++) {
                    var point = steps[i].end_location;
                    coordinates.push(point);
                    bounds.extend(point);
                }

                coordinates.push(endPoint);
                bounds.extend(endPoint);
                mapAddMarker(map, endPoint, 'To');
                mapAddPolyline(map, coordinates);
                mapFitBounds(map, bounds);
            }
        });
    } else {
        coordinates.push(endPoint);
        bounds.extend(endPoint);
        mapAddMarker(map, endPoint, 'To');
        mapAddPolyline(map, coordinates);
        mapFitBounds(map, bounds);
    }

}

function mapAddMarker(map, point, name) {
    new google.maps.Marker({
        position : point,
        map : map,
        title : name
    });
}

function mapAddPolyline(map, coordinates) {
    var polyline = new google.maps.Polyline({
        path : coordinates,
        strokeColor : "#6666FF",
        strokeOpacity : 0.8,
        strokeWeight : 5
    });
    polyline.setMap(map);
}

function mapFitBounds(map, bounds) {
    map.fitBounds(bounds);
    var listener = google.maps.event.addListener(map, "idle", function() {
        if(map.getZoom() > 16)
            map.setZoom(16);
        google.maps.event.removeListener(listener);
    });
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
    hidePopup();
    Context.transport = transport;
    loadItinerary();
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
function formatTime(time) {
    var result = false, m;
    var re = /^\s*([01]?\d|2[0-3]):?([0-5]\d)\s*$/;
    if(( m = time.match(re))) {
        result = (m[1].length == 2 ? "" : "0") + m[1] + ":" + m[2];
    }
    return result;
}