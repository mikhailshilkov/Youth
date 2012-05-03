function map() {
    var start = '59.86758,30.261308';
    var end = '59.868398,30.259806';
    var request = {
        origin : start,
        destination : end,
        travelMode : google.maps.TravelMode.WALKING
    };
    var directionsService = new google.maps.DirectionsService();
    directionsService.route(request, function(result, status) {
        if(status == google.maps.DirectionsStatus.OK) {

            var bounds = new google.maps.LatLngBounds();
            var flightPlanCoordinates = [];
            for(var i = 0; i < result.routes[0].legs[0].steps.length; i++) {
                var step = result.routes[0].legs[0].steps[i];
                flightPlanCoordinates.push(step.start_point);
                flightPlanCoordinates.push(step.end_point);
                bounds.extend(step.start_point);
                bounds.extend(step.end_point);
            }
            var flightPath = new google.maps.Polyline({
                path : flightPlanCoordinates,
                strokeColor : "#222222",
                strokeOpacity : 0.8,
                strokeWeight : 4
            });
            flightPath.setMap(map);
            map.fitBounds(bounds);
        }
    });
}