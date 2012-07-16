HomePage = (function() {
    var STATUS_NONE = 0;
    var STATUS_VALID = 1;
    var STATUS_INVALID = 2;
    
    function createPoint() {
        var point = new Object();
        point.status = STATUS_NONE;
        point.poi = null;
        point.address = null;
        point.coord = null;
        return point;
    }    
    
    var from = createPoint();
    var to = createPoint();
    var time = null;
    var date = null;

    function getUrl() {
        url = '/directions?';
        if(from.poi != null) {
            url += 'from=' + encodeURIComponent($.trim(from.poi.name));
        } else
            url += 'from=' + encodeURIComponent(from.address) + '&fll=' + from.coord[0].toString() + '-' + from.coord[1].toString();
        if(to.poi != null) {
            url += '&to=' + encodeURIComponent($.trim(to.poi.name));
        } else
            url += '&to=' + encodeURIComponent(to.address) + '&tll=' + to.coord[0].toString() + '-' + to.coord[1].toString();
        url += '&date=' + $.datepicker.formatDate('yy-mm-dd', date)
        if (time != '09:30')
            url += '&time=' + time.replace(':', '-');
        return url;
    }

    function retrieveDateTime() {
        date = $("#datepicker").datepicker('getDate');
        time = Utils.formatTime($('#timepicker').val());
        
        setStatus('time', time ? 'valid' : 'invalid');        
    }

    function warmCache() {
        if(from.status == STATUS_VALID && to.status == STATUS_VALID) {
            retrieveDateTime();
            url = getUrl();
            url += '&out=none';
            $.ajax(url);
        }
    }

    function searchByAddress(address, callback, errorCallback) {            
        if(address != '') {
            if(address.indexOf('St. Petersburg') < 0) {
                searchByAddress(address + ', St. Petersburg, Russia', callback, errorCallback);
                return;
            }
             
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
                            callback(lat, lng);
                            return;
                        }
                    }
                    errorCallback();
                } else {
                    errorCallback();
                }
            });
        }
    }

    function resolvePoint(point, name)
    {
        if (point.status == STATUS_VALID)
            return;
            
        var term = $('#' + name).val();
        if (term == '')
            return;
            
        $.ajax('place?out=json&term=' + term).success(function(data) {
            var places = eval(data);
            if (places.length > 0) {
                if (point.poi == null) {                    
                    point.status = STATUS_VALID;
                    point.poi = places[0];
                    $('#' + name).val(places[0].name);
                    updateStatuses();
                }                
            }
            else {
                searchByAddress(term,
                    function(lat, lng) {
                        if (point.poi == null) {
                            point.status = STATUS_VALID;
                            point.address = term;
                            point.coord = [lat, lng];
                            updateStatuses();
                        }
                    },
                    function() {
                        if (point.poi == null) {
                            point.status = STATUS_INVALID;
                            updateStatuses();
                        }
                    });
            }
        });
    }
    
    function setStatus(name, status) {
        $('#' + name + '_status').attr('src', '/images/' + status + '.png');
    }
    
    function updateStatus(point, name) {
        if (point.status == STATUS_VALID)
            setStatus(name, 'valid');
        else if (point.status == STATUS_INVALID)
            setStatus(name, 'invalid');
        else 
            setStatus(name, 'empty');
    }
    
    function updateStatuses() {
        updateStatus(from, 'from');
        updateStatus(to, 'to');
    }

    return {
        init : function() {
            $("#from").autocomplete({
                source : "/place?out=json",
                minLength : 2,
                focus : function(event, ui) {
                    $("#from").val(ui.item.name);
                    return false;
                },
                select : function(event, ui) {
                    $("#from").val(ui.item.name);
                    from.status = STATUS_VALID;
                    from.poi = ui.item;
                    updateStatuses();
                    //warmCache();
                    return false;
                }
            }).data("autocomplete")._renderItem = function(ul, item) {
                return $("<li></li>").data("item.autocomplete", item).append("<a>" + item.name + "</a>").appendTo(ul);
            };
            $("#from").keydown(function() { from = createPoint(); updateStatuses(); });
            $("#from").blur(function () { resolvePoint(from, 'from'); });

            $("#to").autocomplete({
                source : "/place?out=json",
                minLength : 2,
                focus : function(event, ui) {
                    $("#to").val(ui.item.name);
                    return false;
                },
                select : function(event, ui) {
                    $("#to").val(ui.item.name);
                    to.status = STATUS_VALID;
                    to.poi = ui.item;
                    updateStatuses();
                    //warmCache();
                    return false;
                }
            }).data("autocomplete")._renderItem = function(ul, item) {
                return $("<li></li>").data("item.autocomplete", item).append("<a>" + item.name + "</a>").appendTo(ul);
            };
            $("#to").keydown(function() { to = createPoint(); updateStatuses(); });
            $("#to").blur(function () { resolvePoint(to, 'to'); });

            $("#datepicker").datepicker({
                minDate : 0,
                maxDate : "+6M"
            });
            $("#datepicker").datepicker("option", "dateFormat", "dd MM yy");
            var tomorrow = new Date();
            tomorrow.setDate(new Date().getDate() + 1);
            $("#datepicker").datepicker('setDate', tomorrow);

            $("#timepicker").blur(function() { retrieveDateTime(); })
        },
        search : function() {
            _gaq.push(['_trackEvent', 'HomePage.search', 'clicked']);
            
            if ($('#from').val() == '' || from.status == STATUS_INVALID) {
                $('#from').focus().parent().effect('pulsate');
                return;
            }
            
            if ($('#to').val() == '' || to.status == STATUS_INVALID) {
                $('#to').focus().parent().effect('pulsate');
                return;
            }
            
            if (from.status == STATUS_NONE || to.status == STATUS_NONE) {
                setTimeout('HomePage.search()', 100);
                return;
            }

            retrieveDateTime();
            if(date == null) {
                $('#datepicker').focus().parent().effect('pulsate');
                return;
            }
            if(!time) {
                $('#timepicker').focus().parent().effect('pulsate');
                return;
            }

            this.goToDirections();
        },
        goToDirections : function(from_address, from_lat, from_lng) {
            document.location = getUrl(from_address, from_lat, from_lng);
        },
    };
})();