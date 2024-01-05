
/** @type {{[key: string]: string;}} */
let defaultValues = {};




const handleChange = e => {
  for (const key in defaultValues) {
    if ((defaultValues[key] || '') !== $(`[id='${key}']`).val()) {

      // Animate "Cancel Changes" button to visible
      $('#cancelChanges').removeClass('opacity-0');
      $('#cancelChanges').addClass('opacity-100');

      // Ungrey save button
      $('#submit').attr('disabled', false);

      console.log('Changes detected');
      return;
    };
  };

  // Animate "Cancel Changes" button to not visible
  $('#cancelChanges').removeClass('opacity-100');
  $('#cancelChanges').addClass('opacity-0');

  // Grey save button
  $('#submit').attr('disabled', true);

  console.log('No changes');
};




// Hooks
$(() => {
  defaultValues = {
    'Username'            : $('#Username').val() || '',
    'Email'               : $('#Email').val() || '',
    'Change Password'     : $('#Change Password').val() || '',
    'Confirm New Password': $('#Confirm New Password').val() || ''
  }

  for (const key in defaultValues) {
    $(`[id='${key}']`).on('change', handleChange);
  };
});
