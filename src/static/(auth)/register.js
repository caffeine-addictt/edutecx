
$(() => {

  var form = document.querySelector('.needs-validation');

  form.addEventListener('submit', e => {
    e.preventDefault();
    form.classList.add('was-validated');

    if (form.checkValidity()) {
      console.log("Good");
    };
  }, false);

});
 
