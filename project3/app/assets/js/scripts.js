function updateLikes(slug) {
  var obj = slug != undefined ? '.like-area.' + slug : '';
  obj += ' [name="like"]'
  $(obj).on('click', function(e) {
    e.preventDefault();
    action = $(this).parent().attr('action');
    slug = action.split("/")[3];
    $.ajax({
      method: "POST",
      url: action,
      data: { like : $(this).attr('value') },
    }).done(function(html) {
      $('.like-area.' + slug).html(html);
      updateLikes(slug);
    });
  });
}

$(window).on('load', function() {
  updateLikes();
});
