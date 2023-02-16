function o2PreventNonNumInput(event) {
  var charStr = String.fromCharCode(event.keyCode);
  if ( (event.keyCode > 31) && (!charStr.match(/^[0-9]+$/)) )
    event.preventDefault();
}

function o2OnEnterCleanNonNumInputAndStay(event) {
  if (event.keyCode === 13) {
    clean = event.target.value.replace(/\D/g,'');
    if (event.target.value != clean) {
      event.preventDefault();
      event.target.value = clean;
    }
  }
}

function o2CleanNonNumKeys(event) {
  event.target.value = event.target.value.replace(/\D/g,'');
}

function o2PreventNonANumInput(event) {
  var charStr = String.fromCharCode(event.keyCode);
  if ( (event.keyCode > 31) && (!charStr.match(/^[0-9A-Za-z]+$/)) )
    event.preventDefault();
}

function o2OnEnterCleanNonANumInputAndStay(event) {
  if (event.keyCode === 13) {
    clean = event.target.value.replace(/[^0-9A-Za-z]/g,'');
    if (event.target.value != clean) {
      event.preventDefault();
      event.target.value = clean;
    }
  }
}

function o2CleanNonANumKeys(event) {
  event.target.value = event.target.value.replace(/[^0-9A-Za-z]/g,'');
}

function o2NoNonUpANumInput(event) {
  var charStr = String.fromCharCode(event.keyCode);
  if ( (event.keyCode > 31) && (!charStr.match(/^[0-9A-Z]+$/)) )
    event.preventDefault();
}

function o2OnEnterCleanNonUpANumInputAndStay(event) {
  if (event.keyCode === 13) {
    clean = event.target.value.replace(/[^0-9A-Z]/g,'');
    if (event.target.value != clean) {
      event.preventDefault();
      event.target.value = clean;
    }
  }
}

function o2CleanNonUpANumKeys(event) {
  event.target.value = event.target.value.replace(/[^0-9A-Z]/g,'');
}
