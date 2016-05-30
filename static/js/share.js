$('.popup').click(function(e) {
  var url = this.href;
  window.open(url, 'Share', 'status=1,left=0,top=0,width=575,height=400');
  return false;
});
