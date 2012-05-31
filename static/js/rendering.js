var Templates = null;

function tripRequestParams() {
    return Context.from + '&date=' + Context.date + '&time=' + Context.time + 
           '&transport=' + Context.transport + '&out=json';
}

function loadItinerary() {
    var url = '/itinerary/trip?from=' + tripRequestParams();
    $.getJSON(url, function(view) {
        // prepare the view
        for (var i in view)
            for (var j in view[i].steps) {
                step = view[i].steps[j];
                if (step.details != null)
                    for (var k in step.details)
                    step.details[k].step_index = j.toString() + '_' + k.toString();
            }
        
        var template = Templates.filter('#itinerary').html();
        var itinerary = $.mustache(template, view);
        $("#itineraryContent").empty().append(itinerary);
    });
}

function createPopup() {
    if($('.window').length == 0) {
        var url = '/itinerary/options?from=' + tripRequestParams();
        $.getJSON(url, function(view) {
            // prepare the view
            for (var i in view)
                view[i].background = view[i].alias == Context.transport ? 'selected' : 'gray';
                
            var template = Templates.filter('#popup').html();
            var popup = $.mustache(template, view);
            $(document.body).append(popup);
            $('#mask').show();
            alignPopups();
        });
    } else {
        $('#mask, .window').show();
    }    
}


$(document).ready(function() {
    $.get("/templates/mustache.html", function(templates) {
        Templates = $(templates);
        loadItinerary();
    });
});
