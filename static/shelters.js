"use strict"

$(document).ready(function(){

//Code for showing the shelter modal
//event listener for Shelter Search Modal

  $("#shelter-link").on("click", function(){
    $("#shelter-modal").modal("show");
  });   

  // Show text shelter modal
  $(".text-shelter").on("click", function(){
    $("#text-shelter-modal").modal("show");
  });

}); //end of document ready function