MapHelper = {
    show : function(mapPane, route) {
        var myOptions = {
            mapTypeId : google.maps.MapTypeId.ROADMAP,
            scaleControl : true
        };
        var map = new google.maps.Map(mapPane.get(0), myOptions);
        var bounds = new google.maps.LatLngBounds();
        var coordinates = [];
        var startPoint = new google.maps.LatLng(route['start']['lat'], route['start']['lng']);
        var endPoint = new google.maps.LatLng(route['end']['lat'], route['end']['lng']);
        var isSubway = route['type'] == 'Subway';
        coordinates.push(startPoint);
        bounds.extend(startPoint);
        this.addMarker(map, startPoint, route['startName'], route['startIcon']);

        var needsDirections = !isSubway;
        if(route['type'] == 'Walk')// don't search directions for walks < 200 m
            needsDirections = google.maps.geometry.spherical.computeDistanceBetween(startPoint, endPoint) > 150;
        if(needsDirections) {
            var request = {
                origin : startPoint,
                destination : endPoint,
                travelMode : route['type'] == 'Walk' ? google.maps.TravelMode.WALKING : google.maps.TravelMode.DRIVING
            };
            /*var directionsService = new google.maps.DirectionsService();
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
             MapHelper.addMarker(map, endPoint, route['endName'], route['endIcon']);
             MapHelper.addPolyline(map, coordinates);
             MapHelper.fitBounds(map, bounds);
             }
             });*/
            $(document).ready(function() {
                $.ajax({
                    url : 'http://open.mapquestapi.com/directions/v1/route',
                    dataType : 'jsonp',
                    crossDomain : true,
                    data : {
                        routeType : 'pedestrian',
                        generalize : 20,
                        outFormat : 'json',
                        shapeFormat : 'raw',
                        locale : 'en_GB',
                        unit : 'k',
                        from : route['start']['lat'] + ',' + route['start']['lng'],
                        to : route['end']['lat'] + ',' + route['end']['lng']
                    },
                    success : function(data, textStatus, jqXHR) {
                        if (data.info.statuscode == "0") {
                            var shape = data.route.shape;
                            for(var i = 0; i < shape.shapePoints.length / 2; i++) {
                                var point = new google.maps.LatLng(shape.shapePoints[i*2], shape.shapePoints[i*2+1]);
                                coordinates.push(point);
                                bounds.extend(point);
                            }                            
                        }
                        coordinates.push(endPoint);
                        bounds.extend(endPoint);
                        MapHelper.addMarker(map, endPoint, route['endName'], route['endIcon']);
                        MapHelper.addPolyline(map, coordinates);
                        MapHelper.fitBounds(map, bounds);
                    }
                });
            });
        } else {
            coordinates.push(endPoint);
            bounds.extend(endPoint);
            this.addMarker(map, endPoint, route['endName'], route['endIcon']);
            this.addPolyline(map, coordinates);
            this.fitBounds(map, bounds);
        }
    },
    addMarker : function(map, point, name, icon) {
        new google.maps.Marker({
            position : point,
            map : map,
            title : name,
            icon : icon != null && icon != '' ? 'images/' + icon + '.png' : null
        });
    },
    addPolyline : function(map, coordinates) {
        var polyline = new google.maps.Polyline({
            path : coordinates,
            strokeColor : "#6666FF",
            strokeOpacity : 0.8,
            strokeWeight : 5
        });
        polyline.setMap(map);
    },
    fitBounds : function(map, bounds) {
        map.fitBounds(bounds);
        var listener = google.maps.event.addListener(map, "idle", function() {
            if(map.getZoom() > 16)
                map.setZoom(16);
            google.maps.event.removeListener(listener);
        });
    }
}