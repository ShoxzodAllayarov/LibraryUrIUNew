(function ($) {
  "use strict";
  /*============= preloader js css =============*/
  var cites = [];
  cites[0] = "Innovatsion axborot markazi";
  cites[1] = "Innovatsion axborot markazi";
  var cite = cites[Math.floor(Math.random() * cites.length)];
  $("#preloader p").text(cite);
  $("#preloader").addClass("loading");

  $(window).on("load", function () {
    setTimeout(function () {
      $("#preloader").fadeOut(500, function () {
        $("#preloader").removeClass("loading");
      });
    }, 500);
  });
})(jQuery);
