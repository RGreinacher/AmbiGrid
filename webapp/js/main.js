function AmbientController() {
  'use strict';
  /*jslint browser: true*/
  /*global $ */
  /*global console */

  var _this = this;

  // this.ambiGridServerAddress = 'http://172.20.0.12:4444/';
  this.ambiGridServerAddress = 'http://127.0.0.1:4444/';
  this.ambiGridApiAddress = this.ambiGridServerAddress + 'ambiGridApi/';
  this.sliders;
  this.colorSliderState = false; // can be 'hsl', 'rgb' or false

  // ********** init elements ****************************************

  this.init = function() {
    $('#ambiGrid-address').html(this.ambiGridServerAddress);

    // init noUiSlider
    this.sliders = document.getElementsByClassName('sliders');
    this.setupNoUiColorSlider();
    this.setupNoUiTimePicker();

    // init every other interaction
    _this.initHexColorInput();
    _this.initFadeOutMechanics();
    _this.initSetAnimationButtons();

    // ask for the current AmbiGrid state
    this.updateStatus();
  };

  this.initHexColorInput = function() {
    $('.ambiGrid-set-base-color').click(function(event) {
      var hexColor = $('#ambiGrid-base-color-hex').val();
      var targetUri = '';

      if (hexColor.length == 6) {
        targetUri = _this.ambiGridApiAddress + 'setBaseColor/hex/' + hexColor;
      } else if (hexColor.length == 7) {
        targetUri = _this.ambiGridApiAddress + 'setBaseColor/hex/' + hexColor.substring(1);
      }

      _this.apiRequest(targetUri);
      event.preventDefault();
    });
  };

  this.initFadeOutMechanics = function() {
    // event handler for start fade-out button
    $('.ambiGrid-set-fade-out').click(function(event) {
      var timeToFadeOut = _this.sliders[6].noUiSlider.get();
      var targetUri = _this.ambiGridApiAddress + 'setFadeOut/' + (timeToFadeOut * 60);
      _this.apiRequest(targetUri);
      event.preventDefault();
    });

    // event handler for stop fade-out button
    $('.ambiGrid-unset-fade-out').click(function(event) {
      var targetUri = _this.ambiGridApiAddress + 'stopFadeOut';
      _this.apiRequest(targetUri);
      event.preventDefault();
    });
  };

  this.initSetAnimationButtons = function() {
    $('.ambiGrid-set-animation-mono').click({
      animationName: 'monoColor',
    }, this.setAnimationHandler);

    $('.ambiGrid-set-animation-pulsing-circle').click({
      animationName: 'pulsingCircle',
    }, this.setAnimationHandler);

    $('.ambiGrid-set-animation-random-glow').click({
      animationName: 'randomGlow',
    }, this.setAnimationHandler);

    $('.ambiGrid-set-animation-binary-clock').click({
      animationName: 'binaryClock',
    }, this.setAnimationHandler);

    $('.ambiGrid-set-animation-clock-circle').click({
      animationName: 'binaryClockWithPulsingCircle',
    }, this.setAnimationHandler);
  };

  // ********** handler setup ****************************************

  this.setupNoUiColorSlider = function() {
    for (var i = 0; i < 6; i++) {
      if ($(_this.sliders[i]).hasClass('rgb-sliders')) {
        noUiSlider.create(_this.sliders[i], {
          start: 0,
          connect: 'lower',
          step: 1,
          range: { min: 0, max: 255 },
          format: wNumb({ decimals: 0, thousand: '.' }),
        });

        _this.sliders[i].noUiSlider.on('slide', _this.setRGBColor);
      } else {
        noUiSlider.create(_this.sliders[i], {
          start: 0,
          connect: 'lower',
          range: { min: 0, max: 1 },
        });

        _this.sliders[i].noUiSlider.on('slide', _this.setHSLColor);
      }

      // remember that the sliding has stopped
      _this.sliders[i].noUiSlider.on('change', function() {
        _this.colorSliderState = false;
      });
    }
  };

  this.setupNoUiTimePicker = function() {
    var fadeOutTimeSlider = document.getElementById('fade-out-time');
    var tipHandles = fadeOutTimeSlider.getElementsByClassName('noUi-handle');
    var tooltip;

    noUiSlider.create(fadeOutTimeSlider, {
      start: 20,
      connect: 'lower',
      step: 1,
      range: { min: 1, max: 60 },
      format: wNumb({ decimals: 0, thousand: '.' }),
    });

    // add tooltip to slider
    tooltip = document.createElement('div');
    tipHandles[0].appendChild(tooltip);

    tooltip.className += 'tooltip';
    tooltip.innerHTML = '<span></span> min';
    tooltip = tooltip.getElementsByTagName('span')[0];

    fadeOutTimeSlider.noUiSlider.on('update', function(values, handle) {
      tooltip.innerHTML = values[handle];
    });
  };

  this.setHSLColor = function() {
    var apiColor = _this.sliders[0].noUiSlider.get() + '/' +
      _this.sliders[1].noUiSlider.get() + '/' +
      _this.sliders[2].noUiSlider.get();
    var targetUri = _this.ambiGridApiAddress + 'setBaseColor/hsl/' + apiColor;

    _this.colorSliderState = 'hsl';
    _this.apiRequest(targetUri);
  };

  this.setRGBColor = function() {
    var apiColor = _this.sliders[3].noUiSlider.get() + '/' +
      _this.sliders[4].noUiSlider.get() + '/' +
      _this.sliders[5].noUiSlider.get();
    var targetUri = _this.ambiGridApiAddress + 'setBaseColor/rgb/' + apiColor;

    _this.colorSliderState = 'rgb';
    _this.apiRequest(targetUri);
  };

  this.setAnimationHandler = function(event) {
    var targetUri = _this.ambiGridApiAddress + 'setAnimation/' + event.data.animationName;
    _this.apiRequest(targetUri);
    event.preventDefault();
  };

  // ********** update routines ****************************************

  this.updateStatus = function() {
    var targetUri = _this.ambiGridApiAddress + 'status';
    _this.apiRequest(targetUri);
  };

  this.processAmbiGridStatus = function(json) {
    _this.updateStatusInformationText(json);
    _this.updateSliderPositions(json);

    // set the base color as preview
    $('.jumbotron').css('background-color', json.baseHexColor);
    $('#hue').css('background-color', json.baseHexColor);
  };

  this.updateStatusInformationText = function(statusJson) {
    $('#ambiGrid-lightness').html(
      Number((statusJson.currentLightness).toFixed(4))
    );
    $('#ambiGrid-frame-rate').html(statusJson.currentFPS);

    if ('fadeOutIn' in statusJson) {
      $('#ambiGrid-status').html(statusJson.status + ' (fading out)');
      $('#ambiGrid-time-to-fade-out').html(statusJson.fadeOutIn / 60);
      _this.sliders[6].noUiSlider.set(
        parseInt(statusJson.fadeOutIn / 60)
      );
    } else {
      $('#ambiGrid-status').html(statusJson.status);
      $('#ambiGrid-time-to-fade-out').html('-');
    }
  };

  this.updateSliderPositions = function(statusJson) {
    if (!_this.colorSliderState || _this.colorSliderState == 'rgb') {
      // set HSL slider
      _this.sliders[0].noUiSlider.set(statusJson.baseColorHue);
      _this.sliders[1].noUiSlider.set(statusJson.baseColorSaturation);
      _this.sliders[2].noUiSlider.set(statusJson.baseColorLightness);
      console.log('update HSL sliders'); // DEBUG
    }

    if (!_this.colorSliderState || _this.colorSliderState == 'hsl') {
      // set RGB slider
      _this.sliders[3].noUiSlider.set(statusJson.baseColorRed);
      _this.sliders[4].noUiSlider.set(statusJson.baseColorGreen);
      _this.sliders[5].noUiSlider.set(statusJson.baseColorBlue);
      console.log('update RGB sliders'); // DEBUG
    }

    $('#ambiGrid-base-color-hex').val(statusJson.baseHexColor);
  };

  // ********** networking ****************************************

  this.apiRequest = function(uri, $button) {
    if (uri.slice(-1) != '/') {
      uri = uri + '/';
    }

    $.ajax({
      url: uri,
      dataType: 'jsonp',
      success: function(json) {
        _this.processAmbiGridStatus(json);
      },

      error: function(jqxhr, textStatus, error) {
        var err = textStatus + ', ' + error;
        console.log('request failed: ' + err);
      },
    });
  };

}

var ambientController = new AmbientController();
ambientController.init();
