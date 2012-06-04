HomePage = (function() {
    var hotel = null;
    var attraction = null;
    var time = null;
    var date = null;
    
    function getUrl(from_address, from_lat, from_lng, to_address, to_lat, to_lng) {
        return '/directions?address=' + encodeURIComponent(from_address) + '&from=' + from_lat.toString() + '-' + from_lng.toString() + 
               '&attraction=' + encodeURIComponent(to_address) + '&to=' + to_lat.toString() + '-' + to_lng.toString() +
               '&date=' + $.datepicker.formatDate('yy-mm-dd', date) + '&time=' + time.replace(':', '-');        
    }
    
    function retrieveDateTime() {
        date = $("#datepicker").datepicker('getDate');
        time = Utils.formatTime($('#timepicker').val());
    }
    
    function warmCache() {
        if (hotel != null && attraction != null) {
            retrieveDateTime();
            url = getUrl(hotel.name, hotel.latitude, hotel.longitude, attraction.name, attraction.latitude, attraction.longitude);
            url += '&out=none';            
            $.ajax(url);
        }
    }        

    return {
        init : function() {
            $("#hotel").autocomplete({
                source : "/hotel?out=json",
                minLength : 2,
                focus : function(event, ui) {
                    $("#hotel").val(ui.item.name);
                    return false;
                },
                select : function(event, ui) {
                    $("#hotel").val(ui.item.name);
                    hotel = ui.item;
                    warmCache();
                    return false;
                }
            }).data("autocomplete")._renderItem = function(ul, item) {
                return $("<li></li>").data("item.autocomplete", item).append("<a>" + item.name + "</a>").appendTo(ul);
            };

            $("#attraction").autocomplete({
                source : "/attraction?out=json",
                minLength : 1,
                focus : function(event, ui) {
                    $("#attraction").val(ui.item.name);
                    return false;
                },
                select : function(event, ui) {
                    $("#attraction").val(ui.item.name);
                    attraction = ui.item;
                    warmCache();
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

        },
        search : function() {
            var hotelAddress = $('#hotel').val();
            if (hotelAddress == null) {
                alert('Hotel is empty');
                return;
            }
            if (attraction == null) {
                alert('Attraction is empty');
                return;
            }
            retrieveDateTime();
            if(date == null) {
                alert('Wrong date');
                return;
            }
            if(!time) {
                alert('Wrong time');
                return;
            }

            if(hotel != null && hotelAddress == hotel.name)
                this.goToDirections(hotel.name, hotel.latitude, hotel.longitude, attraction.name, attraction.latitude, attraction.longitude);
            else
                this.searchByAddress(hotelAddress);
        },
        searchByAddress : function(address) {
            if(address != '') {
                var geocoder = new google.maps.Geocoder();
                var bounds = new google.maps.LatLngBounds(new google.maps.LatLng(60.28, 29.93), new google.maps.LatLng(59.79, 30.58));
                geocoder.geocode({
                    'address' : address,
                    'bounds' : bounds
                }, function(results, status) {
                    if(status == google.maps.GeocoderStatus.OK) {
                        for(var i = 0; i < results.length; i++) {
                            var latLng = results[i].geometry.location;
                            var lat = latLng.lat();
                            var lng = latLng.lng();
                            var wellType = Math.max($.inArray('street_address', results[i].types), $.inArray('subpremise', results[i].types), $.inArray('premise', results[i].types));
                            if(lat > 59.79 && lat < 60.28 && lng > 29.93 && lng < 30.58 && wellType >= 0) {
                                HomePage.goToDirections(address, lat, lng, attraction.name, attraction.latitude, attraction.longitude);
                                return;
                            }
                        }

                        if(address.indexOf('St. Petersburg') < 0)
                            this.searchByAddress(address + ', St. Petersburg, Russia');
                        else
                            alert("Address was not found");
                    } else {
                        alert("Address was not found for the following reason: " + status);
                    }
                });
            }
        },
        goToDirections : function(from_address, from_lat, from_lng, to_address, to_lat, to_lng) {
            document.location = getUrl(from_address, from_lat, from_lng, to_address, to_lat, to_lng);
        },
    };
})();