
// http://stackoverflow.com/questions/1987524/turn-a-number-into-star-rating-display-using-jquery-and-css



// display rating confirmation
function rate_landmark(response) {
  if (response == "Your rating has been updated.") {
    bootbox.alert("Your rating has been updated.");
  } else {
    bootbox.alert("Thank you for your rating.");
  }
};
// FIXME update star display, static 


function review_landmark(response) {
  if (response == "Your review has been updated.") {
    bootbox.alert("Your review has been updated.");
  } else {
    bootbox.alert("Thank you for your rating.");
  }
};
// FIXME update review display, static

// ajax post request to save user landmark rating from landmark page to db
$('.rating-input').on('click', function(e) {
  e.preventDefault();
  $.ajax({
    type: "POST",
    url: '/rate_landmark',
    data: {
      'landmark_id': landmark_id,
      'score': $(this).val()
    },
    success: rate_landmark,
  });
});

// ajax post request to save user notes from landmark page to db
$('#ratings').on('submit', function(e){
  e. preventDefault();
  $.ajax({
    type: "POST",
    url: '/notes_landmark',
    data:{
      'landmark_id': landmark_id,
      'notes': $('#notes').val()
    },
    success: review_landmark,
  });
});


// http://stackoverflow.com/questions/10863658/load-image-with-jquery-and-append-it-to-the-dom

function add_image(response) {
  $('#image-display').append('<img src=' + response.data.link + '>');
  $.ajax({
    type: "POST",
    url: '/add_image',
    data: {
        'imageURL': response.data.link,
        'landmark_id': landmark_id
    },
    success: function() {
      bootbox.alert("Upload complete");
    }
  }); 
}

//display image on landmark details page AND popup?

// http://stackoverflow.com/questions/3572993/how-to-send-file-input-using-jquery
// ajax post request to upload image 
$('#input-upload').on('change', function(e) {
  var formdata = new FormData();
  formdata.append('image', $('#input-upload')[0].files[0]);
  $.ajax({
    type: "POST",
    headers: {
      'Authorization': 'Client-ID 462d3619fb2210d'
    },
    processData: false,
    contentType: false,
    url: 'https://api.imgur.com/3/image',
    data: formdata,
    success: add_image,
  });
});

// show landmarks that are highly rated and located nearby
$(document).on('ready', function(e) {
  $.ajax({
    type: "GET",
    url: '/other_favorites',
    data: {
      'landmark_id': landmark_id,
    },
    success: function(response) {
      $('#suggestions-title').removeClass('hidden');
      // move jQuery selector object out of forEach function to save runtime
      var $suggestions = $('#suggestions')
      response.forEach(function(suggestion) {
        $suggestions.append("<li><h3><a href='/landmarks/" + suggestion.landmark_id +
        "'>" + suggestion.landmark_name + "</a></h3></li><li><img src='" +
        suggestion.landmark_image + "'/></li>"); 
      });
    }
  });
});
// FIXME: add landmark_image, description in html string for suggestions
