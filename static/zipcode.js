"use strict"

$(document).ready(function(){
  $(function() {
    // IMPORTANT: Fill in your client key
    // var clientKey = "js-kWKYUb68qGd30rF073cxetS0EA96c6lw25uXhB5HhiLhKqiRtupIYhJCRSI4Y4A1";

    // Heroku app client key
    // var clientKey = "8BGWozMytsnnbsinhVJ0c7HPSWF0zMG5bLTLZf6OZFOiTC8oDt4VodD6DLlBU723"

    //Heroku.com key
    var clientKey ="js-M2Or8S0XcxVnfkxg4IAkuZ8mCYxvew42KLgvuCQ9CYhKtCIvRpSq3Ss1WrcEBKL4"
    
    var cache = {};
    var container = $(".form-group");
    var errorDiv = container.find("div.text-error");
    
    /** Handle successful response */
    function handleResp(data)
    {
      // Check for error
      if (data.error_msg)
        errorDiv.text(data.error_msg);
      else if ("city" in data)
      {
        // Set city and state
        container.find("input[name='city']").val(data.city);
        container.find("input[name='state']").val(data.state);
      }
    }
    
    // Set up event handlers

    container.find("input[name='zipcode']").on("keyup change", function() {
      // Get zip code
      var zipcode = $(this).val().substring(0, 5);
      if (zipcode.length == 5 && /^[0-9]+$/.test(zipcode))
      {
        // Clear error
        errorDiv.empty();
        
        // Check cache
        if (zipcode in cache)
        {
          handleResp(cache[zipcode]);
        }
        else
        {
          // Build url
          var url = "https://www.zipcodeapi.com/rest/"+clientKey+"/info.json/" + zipcode + "/radians";
          
          // Make AJAX request
          $.ajax({
            "url": url,
            "dataType": "json"
          }).done(function(data) {
            handleResp(data);
            
            // Store in cache
            cache[zipcode] = data;
          }).fail(function(data) {
            if (data.responseText && (json = $.parseJSON(data.responseText)))
            {
              // Store in cache
              cache[zipcode] = json;
              
              // Check for error
              if (json.error_msg)
                errorDiv.text(json.error_msg);
            }
            else
              errorDiv.text('Request failed.');
          });
        }
      }
    }).trigger("change");
  });

 });//end of document ready function