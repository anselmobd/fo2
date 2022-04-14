function o2SetPageAndSubmit(page) {
  document.getElementById('id_{{field}}').value = page;
  document.{{form}}.submit();
}

function o2SetPage1AndSubmit() {
  document.getElementById('id_{{field}}').value = '1';
  document.{{form}}.submit();
}
