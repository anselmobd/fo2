django.jQuery(document).ready(function( $ ) {
  $( "#id_codigo" ).bind("input", function() {
    this.value = this.value.toUpperCase();
  });
});
