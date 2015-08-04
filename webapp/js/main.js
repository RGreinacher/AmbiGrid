function AmbientController() {
  'use strict';
  /*jslint browser: true*/
  /*global $ */
  /*global console */

  var _this = this;
  var serverIP = '172.20.3.17';
  var httpPort = 4444;
  var wsPort = 4445;

  this.wsServerAddress = 'ws://' + serverIP + ':' + wsPort;
  this.httpServerAddress = 'http://' + serverIP + ':' + httpPort + '/';
  this.httpApiAddress = this.httpServerAddress + 'ambiGridApi/';
  this.webSocketConnection;
  this.webSocketAvailable = false;

  this.sliders;
  this.colorSliderState = false; // can be 'hsl', 'rgb' or false
  this.nextRequestID = -1;

  // ********** init elements ****************************************

  this.init = function() {
    $('#ambiGrid-address').html(this.httpServerAddress);

    // init noUiSlider
    this.sliders = document.getElementsByClassName('sliders');
    this.setupNoUiColorSlider();
    this.setupNoUiTimePicker();

    // init every other interaction
    this.initStatusUpdateButton();
    this.initHexColorInput();
    this.initFadeOutMechanics();
    this.initSetAnimationButtons();

    // init web socket connection
    this.initWebSocket();

    // ask for the current AmbiGrid state
    this.updateStatusWithDetails();
  };

  this.initStatusUpdateButton = function() {
    $('.ambiGrid-update-status').click(function(event) {
      event.preventDefault();
      _this.updateStatusWithDetails();
    });
  };

  this.initHexColorInput = function() {
    $('.ambiGrid-set-base-color').click(function(event) {
      event.preventDefault();
      var hexColor = $('#ambiGrid-base-color-hex').val();
      var message = {action: 'setBaseColor', type: 'hex'};

      if (hexColor.length == 6) {
        message.value = hexColor;
      } else if (hexColor.length == 7) {
        message.value = hexColor.substring(1);
      } else {
        return;
      }

      _this.apiRequest(message);
    });
  };

  this.initFadeOutMechanics = function() {
    // event handler for start fade-out button
    $('.ambiGrid-set-fade-out').click(function(event) {
      event.preventDefault();
      var timeToFadeOut = _this.sliders[6].noUiSlider.get();
      var message = {action: 'setFadeOut', seconds: (timeToFadeOut * 60)};

      _this.apiRequest(message);
    });

    // event handler for stop fade-out button
    $('.ambiGrid-unset-fade-out').click(function(event) {
      event.preventDefault();
      var message = {action: 'stopFadeOut'};

      _this.apiRequest(message);
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
      if ($(this.sliders[i]).hasClass('rgb-sliders')) {
        noUiSlider.create(_this.sliders[i], {
          start: 0,
          connect: 'lower',
          step: 1,
          range: { min: 0, max: 255 },
          format: wNumb({ decimals: 0, thousand: '.' }),
        });

        this.sliders[i].noUiSlider.on('slide', this.setRGBColor);
      } else {
        noUiSlider.create(this.sliders[i], {
          start: 0,
          connect: 'lower',
          range: { min: 0, max: 1 },
        });

        this.sliders[i].noUiSlider.on('slide', this.setHSLColor);
      }

      // remember that the sliding has stopped
      this.sliders[i].noUiSlider.on('change', function() {
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
    var message = {
      action: 'setBaseColor',
      type: 'hsl',
      hue: _this.sliders[0].noUiSlider.get(),
      saturation: _this.sliders[1].noUiSlider.get(),
      lightness: _this.sliders[2].noUiSlider.get(),
    };

    _this.colorSliderState = 'hsl';
    _this.apiRequest(message);
  };

  this.setRGBColor = function() {
    var message = {
      action: 'setBaseColor',
      type: 'rgb',
      red: _this.sliders[3].noUiSlider.get(),
      green: _this.sliders[4].noUiSlider.get(),
      blue: _this.sliders[5].noUiSlider.get(),
    };

    _this.colorSliderState = 'rgb';
    _this.apiRequest(message);
  };

  this.setAnimationHandler = function(event) {
    event.preventDefault();
    var message = {action: 'setAnimation', name: event.data.animationName};

    _this.apiRequest(message);
  };

  // ********** update routines ****************************************

  this.updateStatus = function() {
    var message = {action: 'status', details: false};

    this.apiRequest(message);
  };

  this.updateStatusWithDetails = function() {
    var message = {action: 'status', details: true};

    this.apiRequest(message);
  };

  this.processAmbiGridStatus = function(json) {
    this.updateStatusInformationText(json);
    this.updateSliderPositions(json);

    // set the base color as preview
    $('.jumbotron').css('background-color', json.baseHexColor);
    $('#hue').css('background-color', json.baseHexColor);
  };

  this.updateStatusInformationText = function(statusJson) {
    if ('fadeOutIn' in statusJson) {
      $('#ambiGrid-status').html(statusJson.status + ' (fading out)');
      $('#ambiGrid-time-to-fade-out').html(statusJson.fadeOutIn / 60);
      this.sliders[6].noUiSlider.set(
        parseInt(statusJson.fadeOutIn / 60)
      );
    } else {
      $('#ambiGrid-status').html(statusJson.status);
      $('#ambiGrid-time-to-fade-out').html('-');
    }

    if ('currentLightness' in statusJson && 'currentFPS' in statusJson) {
      $('#ambiGrid-lightness').html(
        Number((statusJson.currentLightness * 100).toFixed(2)) + '%'
      );
      $('#ambiGrid-frame-rate').html(statusJson.currentFPS);
    } else {
      $('#ambiGrid-lightness').html('?');
      $('#ambiGrid-frame-rate').html('?');
    }
  };

  this.updateSliderPositions = function(statusJson) {
    // set HSL slider if those are currently not in use
    if (!this.colorSliderState || this.colorSliderState == 'rgb') {
      this.sliders[0].noUiSlider.set(statusJson.baseColorHue);
      this.sliders[1].noUiSlider.set(statusJson.baseColorSaturation);
      this.sliders[2].noUiSlider.set(statusJson.baseColorLightness);
    }

    // set RGB slider if those are currently not in use
    if (!this.colorSliderState || this.colorSliderState == 'hsl') {
      this.sliders[3].noUiSlider.set(statusJson.baseColorRed);
      this.sliders[4].noUiSlider.set(statusJson.baseColorGreen);
      this.sliders[5].noUiSlider.set(statusJson.baseColorBlue);
    }

    $('#ambiGrid-base-color-hex').val(statusJson.baseHexColor);
  };

  // ********** Networking ****************************************

  this.initWebSocket = function() {
    this.webSocketConnection = new WebSocket(this.wsServerAddress);

    this.webSocketConnection.onopen = function(event) {
      _this.webSocketAvailable = true;
      $('#ambiGrid-address').html(_this.wsServerAddress);
      console.log('opened connection to: ' + event.currentTarget.URL);
    };

    this.webSocketConnection.onerror = function(error) {
      console.log('WebSocket Error: ' + error);
    };

    this.webSocketConnection.onclose = function(event) {
      _this.webSocketAvailable = false;
      $('#ambiGrid-address').html(_this.httpServerAddress);
      console.log('Disconnected from WebSocket.');
    };

    // Handle messages sent by the server.
    this.webSocketConnection.onmessage = function(event) {
      var jsonMessage = JSON.parse(event.data);
      _this.processAmbiGridStatus(jsonMessage);
    };

    // close the ws connection
    window.onbeforeunload = function() {
      ambientController.webSocketConnection.close();
    };
  };

  this.apiRequest = function(messageDictionary, $button) {
    if (!this.webSocketAvailable) {
      this.httpRequestFallback(messageDictionary);
    }

    var message = JSON.stringify(messageDictionary);
    this.webSocketConnection.send(message);
  };

  // ********** HTTP fallback ****************************************

  this.httpRequestFallback = function(messageDictionary) {
    console.log('HTTP fallback not yet imnplemented - sorry bro!');
    var uri = this.httpApiAddress + 'status';
    this.ajaxApiRequest(uri);
  };

  this.ajaxApiRequest = function(uri) {
    $.ajax({
      url: this.prepareUriForRequest(uri),
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

  this.prepareUriForRequest = function(uri) {
    if (uri.slice(-1) != '/') {
      uri = uri + '/';
    }

    // add the request ID we got from the server with the last response
    if (this.nextRequestID > 0) {
      this.nextRequestID = this.nextRequestID + 1;
      uri = uri + 'requestID/' + this.nextRequestID + '/';
    }

    return uri;
  };

}

var ambientController = new AmbientController();
ambientController.init();
