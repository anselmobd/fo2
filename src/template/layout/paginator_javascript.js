function o2SetPageAndSubmit(page) {
  document.getElementById('id_page').value = page;
  document.{{form}}.submit();
}

function o2SetPage1AndSubmit() {
  document.getElementById('id_page').value = '1';
  document.{{form}}.submit();
}
