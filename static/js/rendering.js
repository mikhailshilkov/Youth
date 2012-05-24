$(document).ready(function() {
    $.getJSON('/itinerary?from=59.937122%2C30.324893&out=json', function(view) {
        $.get("/templates/itinerary.mustache", function(template) {
            var article = $.mustache(template, view);
            $("#itineraryContent").append(article);
        });
    });
});