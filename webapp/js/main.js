function AmbientController() {
  'use strict';
  /*jslint browser: true*/
  /*global $ */
  /*global console */

  var buttonFeedbackTime = 1000;
  var _this = this;

  this.ambiGridServerAddress = 'http://172.20.0.12:4444/';
  this.ambiGridApiAddress = this.ambiGridServerAddress + 'ambiGridApi/';
  this.sliders;

  this.init = function() {
    $('#ambiGrid-address').html(this.ambiGridServerAddress);

    this.setupNoUiSlider();

    // base color
    $('#ambiGrid-base-color-lightness').change(function() {
      var lightness = $(this).val();
      var targetUri = _this.ambiGridApiAddress + 'setBaseColor/lightness/' + lightness;
      _this.apiRequestWithFeedbackForButton(targetUri);
    });

    $('.ambiGrid-set-base-color').click(function(event) {
      var hexColor = $('#ambiGrid-base-color-hex').val();
      if (hexColor.length == 7) {
        var targetUri = _this.ambiGridApiAddress + 'setBaseColor/hex/' + hexColor.substring(1);
        _this.apiRequestWithFeedbackForButton(targetUri);
      }

      event.preventDefault();
    });

    // clock color
    $('#ambiGrid-clock-color-lightness').change(function() {
      var lightness = $(this).val();
      var targetUri = _this.ambiGridApiAddress + 'setClockColor/lightness/' + lightness;
      _this.apiRequestWithFeedbackForButton(targetUri);
    });

    $('.ambiGrid-set-clock-color').click(function(event) {
      var hexColor = $('#ambiGrid-clock-color-hex').val();
      if (hexColor.length == 7) {
        var targetUri = _this.ambiGridApiAddress + 'setClockColor/hex/' + hexColor.substring(1);
        _this.apiRequestWithFeedbackForButton(targetUri);
      }

      event.preventDefault();
    });

    // start fade-out
    $('.ambiGrid-set-fade-out').click(function(event) {
      var timeToFadeOut = $('#ambiGrid-time-to-fade-out').val();
      console.log(timeToFadeOut);
      var targetUri = _this.ambiGridApiAddress + 'setFadeOut/' + (timeToFadeOut * 60);
      console.log(targetUri);
      _this.apiRequestWithFeedbackForButton(targetUri);
      event.preventDefault();
    });

    // stop fade-out
    $('.ambiGrid-unset-fade-out').click(function(event) {
      var targetUri = _this.ambiGridApiAddress + 'stopFadeOut';
      _this.apiRequestWithFeedbackForButton(targetUri);
      event.preventDefault();
    });

    // set animation handler
    $('.ambiGrid-set-animation-mono').click({
      animationName: 'monoColor'
    }, this.setAnimationHandler);
    $('.ambiGrid-set-animation-pulsing-circle').click({
      animationName: 'pulsingCircle'
    }, this.setAnimationHandler);
    $('.ambiGrid-set-animation-random-glow').click({
      animationName: 'randomGlow'
    }, this.setAnimationHandler);
    $('.ambiGrid-set-animation-binary-clock').click({
      animationName: 'binaryClock'
    }, this.setAnimationHandler);
    $('.ambiGrid-set-animation-clock-circle').click({
      animationName: 'binaryClockWithPulsingCircle'
    }, this.setAnimationHandler);

    //this.updateStatus();
  };

  this.setupNoUiSlider = function() {
    _this.sliders = document.getElementsByClassName('sliders');

    for (var i = 0; i < _this.sliders.length; i++) {
      noUiSlider.create(_this.sliders[i], {
        start: 5,
        connect: 'lower',
        orientation: 'vertical',
        range: {
          min: 0,
          max: 255
        },
        format: wNumb({
          decimals: 0,
          thousand: '.'
      	})
      });

      // Bind the color changing function to the slide event:
      _this.sliders[i].noUiSlider.on('slide', _this.setColor);
    }
  }

  this.setColor = function() {
    var apiColor = _this.sliders[0].noUiSlider.get() + '/' +
      _this.sliders[1].noUiSlider.get() + '/' +
      _this.sliders[2].noUiSlider.get();
    var cssColor = 'rgb(' +
      _this.sliders[0].noUiSlider.get() + ',' +
      _this.sliders[1].noUiSlider.get() + ',' +
      _this.sliders[2].noUiSlider.get() + ')';

    var targetUri = _this.ambiGridApiAddress + 'setBaseColor/rgb/' + apiColor;
    _this.apiRequestWithFeedbackForButton(targetUri);

    $('.jumbotron').css('background-color', cssColor);
  }

  this.setAnimationHandler = function(event) {
    var targetUri = _this.ambiGridApiAddress + 'setAnimation/' + event.data.animationName;
    _this.apiRequestWithFeedbackForButton(targetUri);
    event.preventDefault();
  }

  this.updateStatus = function() {
    $.getJSON(this.ambiGridApiAddress + 'status').done(function(json) {
      console.log('update AmbiGrid status - successfull request, JSON data: ' + json);

      $('#ambiGrid-status').html('test');
    }).fail(function(jqxhr, textStatus, error) {
      var err = textStatus + ', ' + error;
      console.log('request failed: ' + err);
      $('#ambiGrid-status').html('fail');
    });
  };

  this.setAmbiGridStatusInformation = function(json) {
    $('#ambiGrid-status').html(json.status);
    $('#ambiGrid-time-to-fade-out').html(json.fadeOutIn);
    $('#ambiGrid-animation').html('?');
    $('#ambiGrid-frame-rate').html(json.currentFPS);

    if ('fadeOutIn' in json) {
      $('#ambiGrid-time-to-fade-out').html(json.fadeOutIn / 60);
    } else {
      $('#ambiGrid-time-to-fade-out').html('-');
    }

    $('#ambiGrid-base-color-lightness').val(json.baseLightness * 100);
    $('#ambiGrid-base-color-hex').val(json.baseColor);
    $('#ambiGrid-clock-color-lightness').val(json.clockLightness * 100);
    $('#ambiGrid-clock-color-hex').val(json.clockColor);

    $('.jumbotron').css('background-color', json.baseColor);
  };

  this.apiRequestWithFeedbackForButton = function(uri, $button) {
    if (uri.slice(-1) != '/') {
      uri = uri + '/';
    }

    $.ajax({
      url: uri,
      dataType: 'jsonp',
      success: function(json) {
        _this.setAmbiGridStatusInformation(json);
      },

      error: function(jqxhr, textStatus, error) {
        var err = textStatus + ', ' + error;
        console.log('request failed: ' + err);
      }
    });
  };

  this.setFeedbackToButton = function(buttonStyle, $button) {
    $button.addClass(buttonStyle);
    setTimeout(function(buttonStyle, $button) {
      $button.removeClass(buttonStyle);
    }, buttonFeedbackTime);
  };

}

var ambientController = new AmbientController();
ambientController.init();
