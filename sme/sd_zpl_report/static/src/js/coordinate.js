$(document).ready(function () {
  $('#preview_holder').mousemove(function (e) {
//  debugger;
  var dense = parseInt(document.getElementsByName('density_choosen')[0].value)
//    alert(dense);
    var offset = $(this).offset();
    var X = (e.pageX - offset.left);
    var Y = (e.pageY - offset.top);

    if (dense == 6) {
      X = X - 3.5
      Y = Y - 2.5
      if (0 > X) { X = 0; } else { X = Number(X.toFixed(2)); }
      if (0 > Y) { Y = 0; } else { Y = Number(Y.toFixed(2)); }
      $('#both_coordinates').text('X:' + X + ', Y:' + Y);
    }

    if (dense == 8) {
      X = X - 2.5
      Y = Y - 1.5
      if (0 > X) { X = 0; }else { X = Number(X.toFixed(2)); }
      if (0 > Y) { Y = 0; }else { Y = Number(Y.toFixed(2)); }
      $('#both_coordinates').text('X:' + X + ', Y:' + Y);
    }

    if (dense == 12) {
        X = X - 7
        Y = Y - 1.5
        if (0 > X) { X = 0 }else{X = X + (X/8)*4; X = Number(X.toFixed(2)); }
        if (0 > Y) { Y = 0 }else{Y = Y + (Y/8)*4; Y = Number(Y.toFixed(2)); }
      $('#both_coordinates').text('X:' + X + ', Y:' + Y);
    }

    if (dense == 24) {
      X = X - 7.2
      Y = Y - 1.5
      if (0 > X) { X = 0; } else { X= X*3; X = Number(X.toFixed(2)); }
      if (0 > Y) { Y = 0; } else { Y= Y*3; Y = Number(Y.toFixed(2)); }
      $('#both_coordinates').text('X:' + X + ', Y:' + Y);
    }

  });
});
