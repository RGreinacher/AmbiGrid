function AmbientController() {
  'use strict';
  /*jslint browser: true*/
  /*global $ */
  /*global console */

  var _this = this;
  var serverIP = '172.20.3.17';
  var serverIP = '127.0.0.1';
  var httpPort = 4444;
  var wsPort = 4445;

  this.wsServerAddress = 'ws://' + serverIP + ':' + wsPort;
  this.webSocketConnection;
  this.webSocketAvailable = false;

  this.sliders;
  this.colorSliderState = false; // can be 'hsl', 'rgb' or false
  this.nextRequestID = -1;

  // ********** init elements ****************************************

  this.init = function() {
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
    setTimeout(function() {
      _this.updateStatusWithDetails();
    }, 500);
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
    var timeDisplay;

    noUiSlider.create(fadeOutTimeSlider, {
      start: 1200,
      connect: 'lower',
      step: 1,
      range: { min: 5, max: 3600 },
    });

    timeDisplay = document.getElementById('fade-out-time-display');

    fadeOutTimeSlider.noUiSlider.on('update', function(values, handle) {
      var time = _this.secondsToTimeString(parseInt(values[handle]));
      timeDisplay.innerHTML = time;
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

  // ********** processing routines ****************************************

  this.processAmbiGridStatus = function(json) {
    if (json.update == 'all' || json.update == 'details') {
      this.updateStatusDetails(json);
    }

    if (json.update == 'all' || json.update == 'status') {
      this.updateStatusInformationText(json);
      this.updateSliderPositions(json);
      this.updateColors(json);
    }
  };

  this.updateStatusDetails = function(json) {
    if (('currentLightness' in json) && ('currentFPS' in json)) {
      $('#ambiGrid-lightness').html(
        Number((json.currentLightness * 100).toFixed(2)) + '%'
      );
      $('#ambiGrid-frame-rate').html(json.currentFPS);
    }
  };

  this.updateStatusInformationText = function(json) {
    if ('fadeOutIn' in json) {
      $('#ambiGrid-status').html(json.status + ' (fading out)');
      $('#ambiGrid-time-to-fade-out').html(json.fadeOutIn / 60);
      this.sliders[6].noUiSlider.set(
        parseInt(json.fadeOutIn / 60)
      );
    } else {
      $('#ambiGrid-status').html(json.status);
      $('#ambiGrid-time-to-fade-out').html('-');
    }
  };

  this.updateSliderPositions = function(json) {
    // set HSL slider if those are currently not in use
    if (!this.colorSliderState || this.colorSliderState == 'rgb') {
      this.sliders[0].noUiSlider.set(json.baseColorHue);
      this.sliders[1].noUiSlider.set(json.baseColorSaturation);
      this.sliders[2].noUiSlider.set(json.baseColorLightness);
    }

    // set RGB slider if those are currently not in use
    if (!this.colorSliderState || this.colorSliderState == 'hsl') {
      this.sliders[3].noUiSlider.set(json.baseColorRed);
      this.sliders[4].noUiSlider.set(json.baseColorGreen);
      this.sliders[5].noUiSlider.set(json.baseColorBlue);
    }

    $('#ambiGrid-base-color-hex').val(json.baseHexColor);
  };

  this.updateColors = function(json) {
    // set back the color information to the UI as preview
    var sliderBackgrnd = 'rgba(0, 0, 0, ' + (1 - json.baseColorLightness) + ')';
    $('#lightness').css('background-color', sliderBackgrnd);
    $('#hue').css('background-color', json.baseHexColor);
    $('.jumbotron').css('background-color', json.baseHexColor);
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
      $('#ambiGrid-address').html('disconnected');
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
      this.initWebSocket();
    }

    var message = JSON.stringify(messageDictionary);
    this.webSocketConnection.send(message);
  };

  // ********** helper ****************************************

  this.secondsToTimeString = function(secs) {
    var hours = Math.floor(secs / (60 * 60));
    var divisorForMinutes = secs % (60 * 60);
    var minutes = Math.floor(divisorForMinutes / 60);
    var seconds = Math.ceil(divisorForMinutes % 60);

    var time = '';
    var postfix = 'sec';

    if (seconds < 10) {
      time = '0' + seconds;
    } else {
      time = seconds;
    }

    if (minutes > 0) {
      time = minutes + ':' + time;
      postfix = 'min';
    }

    if (hours > 0) {
      time = hours + ':' + time;
      postfix = 'h';
    }

    return time + ' ' + postfix;
  };

}

var ambientController = new AmbientController();
ambientController.init();
