"use strict"

function initMap(evt) {

  // Create center based on the first shelter located
  var firstShelter = $(".shelter");
  firstShelter = firstShelter[0];
  var firstShelterlat = Number(firstShelter.dataset.lat);
  var firstShelterlong = Number(firstShelter.dataset.long);
  var shelterCenter = {lat: firstShelterlat, lng: firstShelterlong};  
  var styledMapType = new google.maps.StyledMapType(

 [
    {
        "featureType": "water",
        "stylers": [
            {
                "color": "#19a0d8"
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "weight": 6
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "color": "#e85113"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#efe9e4"
            },
            {
                "lightness": -40
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#efe9e4"
            },
            {
                "lightness": -20
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "lightness": 100
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "lightness": -100
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "labels.icon"
    },
    {
        "featureType": "landscape",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "landscape",
        "stylers": [
            {
                "lightness": 20
            },
            {
                "color": "#efe9e4"
            }
        ]
    },
    {
        "featureType": "landscape.man_made",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "lightness": 100
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "lightness": -100
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "hue": "#11ff00"
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "lightness": 100
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "labels.icon",
        "stylers": [
            {
                "hue": "#4cff00"
            },
            {
                "saturation": 58
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "color": "#f0e4d3"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#efe9e4"
            },
            {
                "lightness": -25
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#efe9e4"
            },
            {
                "lightness": -10
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    }
],
 {name: 'Styled Map'});

 
  
  // Create a map object and specify the DOM element for display.
  var map = new google.maps.Map(document.getElementById("shelter-map"), {
    center: shelterCenter,
    scrollwheel: false,
    zoom: 11,
    zoomControl: true,
    mapTypeControlOptions: {
            mapTypeIds: ['roadmap', 'satellite', 'hybrid', 'terrain',
                    'styled_map']
    }                
  });

  //Associate the styled map with the MapTypeId and set it to display.
  map.mapTypes.set('styled_map', styledMapType);
  map.setMapTypeId('styled_map');  

  // Add markers and info windows to all shelters
  var allShelters = $(".shelter");
  var infoWindow = new google.maps.InfoWindow({
    width: 150
  });         

  // Iterate through to produce shelter lat, long 
  // and info window content
  for (var i=0; i<allShelters.length; i++) {
    var thisShelter = allShelters[i];
    var shelterLat = Number(thisShelter.dataset.lat);
    var shelterLong = Number(thisShelter.dataset.long);
    var shelterName = thisShelter.dataset.name;
    var shelterAddr1 = thisShelter.dataset.addr1;
    var shelterCity = thisShelter.dataset.city;
    var shelterState = thisShelter.dataset.state;
    var shelterZip = thisShelter.dataset.zip; 
    var shelterEmail = thisShelter.dataset.email;
    var shelterPhone = thisShelter.dataset.phone;
    var shelterID = thisShelter.dataset.shelterid;

    // Define the marker
    var icon = { url: 'static/img/pet-pointer.png',
                 scaledSize : new google.maps.Size(34, 48)
               };

    var marker = new google.maps.Marker ({
      position: {lat: shelterLat, lng: shelterLong},
      map: map,
      icon: icon
    }); 
    // Construct mailto: so users can email shelter 
    var finalEmail = "<a href=mailto:"+ shelterEmail + ">" 
                      + "Contact us" + "</a>";
    console.log(finalEmail)                  
    var shelterURL = "/shelter-pets?id=";                  
    var finalShelterID = "<a href=" + shelterURL + shelterID + ">"
                         + "See our pets" + "</a>";
    console.log(finalShelterID)                                     

    // Define the content of the infoWindow
    var html = ('<div class="infowindow-shelters">' +
            '<p>'+ shelterName  + '<br>' + shelterAddr1 + '<br>' +
                   shelterCity  +  ", "  + shelterState +  " "   + 
                   shelterZip   + '<br>' + 
                   shelterPhone + '<br>' + '<br>' + 
                   finalEmail   + '<br>' +  
              finalShelterID    + '</p>' +                                           
                   '</div>');

    bindInfoWindow(marker, map, infoWindow, html);  
    
    }         
  }  

  function bindInfoWindow(marker, map, infoWindow, html) {
      google.maps.event.addListener(marker, 'click', function () {
          infoWindow.close();
          infoWindow.setContent(html);
          infoWindow.open(map, marker);
      });
  }



 
