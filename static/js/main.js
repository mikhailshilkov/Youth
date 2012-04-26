function showDetails(index)
{
   $("#details_collapsed_" + index.toString()).toggle();
   $("#details_expanded_" + index.toString()).toggle();
}

function showPopup() 
{
        var id = '#dialog';
     
        //Get the screen height and width
        var maskHeight = $(document).height();
        var maskWidth = $(window).width();
     
        //Set height and width to mask to fill up the whole screen
        $('#mask').css({'width':maskWidth,'height':maskHeight});
         
        //transition effect     
        $('#mask').toggle();    
     
        //Get the window height and width
        var winH = $(window).height();
        var winW = $(window).width();
               
        //Set the popup window to center
        $(id).css('top',  winH/2-$(id).height()/2);
        $(id).css('left', winW/2-$(id).width()/2);
     
        //transition effect
        $(id).toggle();      
}

function hidePopup()
{
	$('#mask, .window').hide();
}

function goTo(transport)
{
	window.location.href = '/?transport=' + transport + '&time=' + Context.startTime;
}

$(document).ready(function () {
	$(window).resize(function () {
  
        var box = $('.window');
  
        //Get the screen height and width
        var maskHeight = $(document).height();
        var maskWidth = $(window).width();
       
        //Set height and width to mask to fill up the whole screen
        $('#mask').css({'width':maskWidth,'height':maskHeight});
                
        //Get the window height and width
        var winH = $(window).height();
        var winW = $(window).width();
  
        //Set the popup window to center
        box.css('top',  winH/2 - box.height()/2);
        box.css('left', winW/2 - box.width()/2);
  
	});
});