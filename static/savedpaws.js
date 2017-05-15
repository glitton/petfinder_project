"use strict"

$(document).ready(function(){

//Show search form
$("#save-search-form").hide();
$("#save-box").change(function(){
    if ($("#save-box").is(":checked")) {
      $("#save-search-form").show();
    } else {
      $("#save-search-form").hide();
    } 
});

//Save a search
$("#save-search-button").click(function(evt){
   evt.preventDefault();
   saveSearch();
});
//event listener 
function saveSearch(evt) {
    
    //Get the form values
    var title = $("#saved-title").val();
    var description = $("#saved-description").val();
    var saveBox = $("#save-status").val();

    //Pack up the form values into an object
    var formData = {"title": title,
                    "description": description,
                     "save": saveBox};

    //Make the AJAX request
    $.post("/save-search.json", formData, function(results){
          console.log("results: ", results);
          var success = results.success;

          if (success === true) { 
          $("#save-status").html(results.message);
         } 
      } //end of callback function
    ); //end of AJAX save search request
 } //end of saveSearch function

//Display the title, description and URL for save search modal
function savedURL(results) {
// create an array of keys to create URL
  var keys = ["age", "animal", "breed", "gender", "size", "zipcode"];

  var queryPair = []; 
// build first half of the URL
  var url = "/search-complete?";
// loop through keys, get value and append to queryPair array
  for (var i = 0; i < keys.length; i++) {
    var val = results[keys[i]];


    if (val) {
      queryPair.push(keys[i] + "=" + val);
    } else {
      queryPair.push(keys[i]+ "=");
    }
  }

  if (results.animal === "dog") {
    queryPair.push("dog-breeds" + "=" + results["breed"]);
    queryPair.push("cat-breeds=None");
  } else {
    queryPair.push("cat-breeds" + "=" + results["breed"]);
    queryPair.push("dog-breeds=None");
  }
  console.log(queryPair);

  var halfURL = queryPair.join("&");
  var finalURL = url + halfURL;
  
  console.log(finalURL);

  return finalURL;
}

//Display the search in the modal
//Event listener
$("#saved-searches").on("click", function() {

  //Make the AJAX request, event handler
  $.get("/get-saved-searches.json", function(results) {
    console.log("results: ", results.results);
    //Remove duplicate saves if user clicks multiple times
    $(".modal-body .save-modal").remove();
    for (var i = 0; i < results.results.length; i++) {
      var result = results.results[i]
      var href = savedURL(result);
      var savedLinkText = "Title: " + result.title + " &nbsp; Description: " + result.description; 
      var newAelement = $("<a>");
      newAelement.append(savedLinkText);
      newAelement.attr("class", "save-link");
      newAelement.attr("href", href);
      var newP = $("<p>");
      newP.append(newAelement);
      newP.attr("class", "save-modal");      
      $(".modal-body").append(newP);
    }

  // Show liked pets, keep hearts green
  $.get("get-liked-pets.json", function(results) {
    console.log("results: ", results.results);
    // Represents a liked pet
    var greenHearts = results.results;
    console.log(greenHearts);
    
    var likedPetId = results.results.pet_id;

    for (var i = 0; i < greenHearts.length; i++) {
      $("#"+likedPetId).removeClass("btn-primary").addClass("btn-success");
    }
  });

  $("#save-modal").modal("show"); 
   });
 });//End of event listener

// 
//Save Like pets to database 
$(".like").on("click", saveLikes);

function saveLikes(evt) {
       
    //Get the data attributes
    var shelterID = $(evt.currentTarget).data('shelterId');
    var animal = $(evt.currentTarget).data('animal');
    var petname = $(evt.currentTarget).data('name');
    var breed = $(evt.currentTarget).data('breeds');
    var age = $(evt.currentTarget).data('age');
    var gender = $(evt.currentTarget).data('gender');
    var petID = $(evt.currentTarget).data('petid');
    var size = $(evt.currentTarget).data('size');
    var description = $(evt.currentTarget).data('description');
    var lastUpdate = $(evt.currentTarget).data('lastupdate');

    //Pack up the form values into an object
    var formData = {"shelterID": shelterID,
                    "animal": animal,
                    "petname": petname,
                    "breed": breed,
                    "age": age,
                    "gender": gender,
                    "petID": petID,
                    "size": size,
                    "description": description,
                    "lastUpdate": lastUpdate};

    //Make the AJAX request
    $.post("/like-pets.json", formData, function(results){
          console.log("results: ", results);
          var success = results.success;
          var petId = results.pet_id;
          if (success === true) { 
           $("#"+petId).removeClass("btn-primary").addClass("btn-success");


         } 
      } //end of callback function
    ); //end of AJAX save search request
 } //end of saveLikes function 

 //Show learn more about pets from complete search
//event listener 
function learnMore(number) {
  $("#learn-more"+"-"+number).on("click", function(){
    $("#learn-more-modal"+"-"+number).modal("show");
  });
}
  

}); //end of document ready

