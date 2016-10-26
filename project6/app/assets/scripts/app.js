var allLocations = [
{
  name: "Tony's Restaurant & Pizzeria",
  lat: 40.8815465,
  lng: -74.2308552,
  yelpID: "tonys-restaurant-and-pizzeria-little-falls"
},
{
  name: "Bella Notte Italian Restaurant",
  lat: 40.878983,
  lng: -74.2244497,
  yelpID: "bella-notte-little-falls-2"
},
{
  name: "Chang Sing Restaurant",
  lat: 40.878824,
  lng: -74.2242987,
  yelpID: "chang-sing-restaurant-little-falls"
},
{
  name: "Maggie's Town Tavern",
  lat: 40.879327,
  lng: -74.2244274,
  yelpID: "maggies-town-tavern-little-falls"
},
{
  name: "Falls Creamery",
  lat: 40.8818153,
  lng: -74.230677,
  yelpID: "falls-creamery-little-falls"
},
{
  name: "Little Falls Historical Society",
  lat: 40.881288,
  lng: -74.2307038,
  yelpID: "little-falls-historical-society-little-falls"
},
{
  name: "Wilmore Park",
  lat: 40.8798107,
  lng: -74.2246071,
  yelpID: null
},
{
  name: "Lenape Trailhead",
  lat: 40.861999,
  lng: -74.2143454,
  yelpID: "mills-reservation-cedar-grove-2"
},
{
  name: "Lu Nello Restaurant",
  lat: 40.8753631,
  lng: -74.2346062,
  yelpID: "lu-nello-cedar-grove"
},
{
  name: "Morris Canal Park",
  lat: 40.8827594,
  lng: -74.229387,
  yelpID: null
},
{
  name: "Pizza & Sandwich Express",
  lat: 40.8820465,
  lng: -74.2292985,
  yelpID: "pizza-and-sandwich-express-little-falls"
},
{
  name: "Suchorsky Park",
  lat: 40.8870321,
  lng: -74.2390878,
  yelpID: null
},
{
  name: "Amity Park",
  lat: 40.8824355,
  lng: -74.2463638,
  yelpID: null
},
{
  name: "Passaic Valley High School",
  lat: 40.8766356,
  lng: -74.2158879,
  yelpID: "passaic-valley-regional-high-school-district-1-little-falls"
}];

function nonceGenerator(length) {
  var text = "";
  var letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

  for (var i = 0; i < length; i++) {
    text += letters.charAt(Math.floor(Math.random() * letters.length));
  }
  return text;
}

var CONSUMER_KEY = "yelp_consumer_key";
var CONSUMER_SECRET = "yelp_consumer_secret";
var TOKEN = "yelp_token";
var TOKEN_SECRET = "yelp_token_secret";
var YELP_URL = "https://api.yelp.com/v2/business/";
var GOOGLE_MAP = null;

var Location = function(marker, yelpID) {
  this.marker = marker;
  this.yelpID = yelpID;
  this.yelpResponse = null;
  this.rating = null;
};

function initMap() {
  var littleFalls = {lat: 40.8773133, lng: -74.230562};
  var map = new google.maps.Map(document.getElementById("map"), {
    zoom: 15,
    center: littleFalls
  });
  GOOGLE_MAP = map;
}

function gMapError() {
  $('#map').html("<h1>Google maps failed to load.</h1>");
}

/* Create a new Google Maps marker */
function newMarker(item, map) {
  return new google.maps.Marker({
    position: {lat: item.lat, lng: item.lng},
    map: map,
    title: item.name
   });
}

/* Add animation to Google maps marker */
function addAnimation(oldMarker, newMarker) {
  if (newMarker.marker.getAnimation()) {
    return newMarker.marker.setAnimation(null);
  }

  if (oldMarker) {
    oldMarker.marker.setAnimation(null);
  }
  return newMarker.marker.setAnimation(google.maps.Animation.BOUNCE);
}

/* Build the parameters for a Yelp request to be sent ansynchronously */
function yelpRequest(yelpID) {
  if (yelpID === null) return null;
  var httpMethod = "GET",
      businessURL = YELP_URL + yelpID,
      parameters = {
        oauth_consumer_key : CONSUMER_KEY,
        oauth_token : TOKEN,
        oauth_nonce : nonceGenerator(12),
        oauth_timestamp : Math.floor(Date.now()/1000),
        oauth_signature_method : "HMAC-SHA1",
        oauth_version : "1.0",
        callback: "cb"
      };
  parameters.oauth_signature = oauthSignature.generate(httpMethod, businessURL, parameters, CONSUMER_SECRET, TOKEN_SECRET);
  return parameters;
}

var ViewModel = function() {
  var self = this;

  this.map = GOOGLE_MAP;
  this.locationList = ko.observableArray([]);
  this.filterQuery = ko.observable("");
  this.infoWindow = new google.maps.InfoWindow();
  this.currentMarker = null;

  /* Click Handler for the markes */
  this.clickMarker = function(newMarker) {
    self.map.panTo(newMarker.marker.position);
    addAnimation(self.currentMarker, newMarker);
    self.currentMarker = newMarker;
    self.openInfoWindow();
  };

  /* Either makes an AJAX request to Yelp or uses stored information to display
   * the infobox for each marker */
  this.openInfoWindow = function() {
    var currentMarker = self.currentMarker;
    var marker = currentMarker.marker;
    var review = currentMarker.yelpResponse;
    var rating = currentMarker.rating;

    var fail = function() {
      self.infoWindow.setContent("<h3>" + marker.title +
        "</h3><h5>No Yelp information available</h5>");
      return self.infoWindow.open(self.map, marker);
    };

    var success = function(review, rating) {
      currentMarker.yelpResponse = review;
      currentMarker.rating = rating;
      self.infoWindow.setContent("<h3>" + marker.title + "</h3><h5>Rating: " +
        rating + "/5</h5><h4>Yelp Reviews</h4>" + review + "<h5><a href='" +
        "https://www.yelp.com/biz/" + currentMarker.yelpID + "'>Link</a></h5>" +
        "<h6>Powered by the <a href='https://www.yelp.com/developers/'>Yelp API</a></h6>");
      return self.infoWindow.open(self.map, marker);
    };

    if (currentMarker.yelpID === null) {
      return fail();
    }

    if (review) {
      return success(review, rating);
    }

    var params = yelpRequest(currentMarker.yelpID),
        businessURL = YELP_URL + currentMarker.yelpID;

    $.ajax({
      url: businessURL,
      dataType: "jsonp",
      cache: true,
      data: params,
    }).done(function(r) {
      return success(r.reviews[0].excerpt, r.rating);
    }).fail(function(r) {
      return fail();
    });
  };

  /* Build the knockout observable array with click handler */
  allLocations.forEach(function(item) {
    var marker = newMarker(item, self.map);
    var newLoc = new Location(marker, item.yelpID);
    marker.addListener("click", function() {
      self.clickMarker(newLoc);
    });
    self.locationList.push(newLoc);
  });

  this.locationList.sort(function(left, right) {
    return left.marker.title == right.marker.title ? 0 : (left.marker.title < right.marker.title ? -1 : 1);
  });

  /* Filters location by value typed into filter input box */
  this.filterLocations = ko.computed(function() {
    var filter = self.filterQuery().toLowerCase();
    if (!filter) {
      self.locationList().forEach(function(item) { item.marker.setVisible(true); });
      return self.locationList();
    }
    return ko.utils.arrayFilter(self.locationList(), function(item) {
      if (self.infoWindow) self.infoWindow.close();
      var v = item.marker.title.toLowerCase().includes(filter);
      item.marker.setVisible(v);
      return v;
    });
  });
};

$(window).on("load", function() {
  ko.applyBindings(new ViewModel());
});
