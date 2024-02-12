
/** @type {{[key: string]: string;}} */
let defaultValues = {};




const handleChange = () => {
  const profileImage = $('#profile__image');
  if (profileImage.attr('src') !== '') {
    $('#pfp-icon').addClass('visually-hidden');
  }
  else {
    $('#pfp-icon').removeClass('visually-hidden');
  };

  for (const key in defaultValues) {
    if (
      ((defaultValues[key] || '') !== $(`[id='${key}']`).val())
      ||
      (key === 'profile__image' && (defaultValues[key] || '') !== $(`[id='${key}']`).attr('src'))
    ) {

      // Animate "Cancel Changes" button to visible
      $('#cancel-changes-button').removeClass('opacity-0 disabled');
      $('#cancel-changes-button').addClass('opacity-100');

      // Ungrey save button
      $('#submit').attr('disabled', false);
      return;
    };
  };

  // Animate "Cancel Changes" button to not visible
  $('#cancel-changes-button').removeClass('opacity-100');
  $('#cancel-changes-button').addClass('opacity-0 disabled');

  // Grey save button
  $('#submit').attr('disabled', true);
};




// Hooks
$(() => {
  defaultValues = {
    'username': $('#username').val() || '',
    'email': $('#email').val() || '',
    'password': '',
    'confirmPassword': '',
    'profile__image': $('#profile__image').attr('src') || '',
  }

  for (const key in defaultValues) {
    $(`[id='${key}']`).on('input', handleChange);
  };

  $(`[id='profile__input']`).on('change', e => {
    let currentSrc = $('#profile__image').attr('src');

    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = a => {
        currentSrc = a.target.result;
        $('#profile__image').attr('src', a.target.result);
        handleChange();
      };
      reader.readAsDataURL(e.target.files[0]);
    };
  });

  handleChange();
});


// Event Listeners
$(() => {
  $('#cancel-changes-button').on('click', () => {
    for (const key in defaultValues) {
      $(`[id='${key}']`).val(defaultValues[key]);
    };
    $('#profile__image').attr('src', defaultValues['profile__image']);
    handleChange();
  });




  // Update Account Details Flow
  $('#profileForm').on('submit', e => {
    e.preventDefault();
    $('#update-account-modal').modal('show');
  });

  $('#close-update-account-modal-big').on('click', () => $('#update-account-modal').modal('hide'));
  $('#close-update-account-modal-small').on('click', () => $('#update-account-modal').modal('hide'));

  $('#confirmed-update-account').on('click', async () => {
    $('#update-account-modal').modal('hide');
    renderToast('Updating account...', 'info');

    // Generate formData
    const formattedData = new FormData();
    formattedData.append('user_id', `${user_id}`);
    if (defaultValues['username'] !== ($('#username').val() || '')) formattedData.append('username', $('#username').val());
    if (defaultValues['email'] !== ($('#email').val() || '')) formattedData.append('email', $('#email').val());
    if (defaultValues['password'] !== ($('#password').val() || '')) formattedData.append('password', $('#password').val());
    if (defaultValues['profile__image'] !== ($('#profile__image').attr('src') || '')) formattedData.append('upload', $('#profile__input')[0].files[0]);

    /**
     * Update account
     * @type {{status: number; message: string;}}
     */
    const response = await fetch('/api/v1/user/edit', {
      method: 'POST',
      headers: { 'X-CSRF-TOKEN': getAccessToken() },
      body: formattedData
    }).then(async res => await res.json());

    if (response.status === 200) {
      renderToast(response.message, 'success');
      document.location.reload();
    }
    else if (response.status === 401) {
      // Handle edge case where access token expires
      renderToast('Your session has expired. Please log in again.', 'danger');
      document.location.href = `/login?callbackURI=${encodeURIComponent(document.location.href)}`;
    }
    else {
      renderToast(response.message, 'danger');
    };

  })




  // Delete Account Flow
  $('#delete-account-button').on('click', () => {
    $('#delete-account-modal').modal('show');
  });

  $('#close-delete-account-modal-big').on('click', () => $('#delete-account-modal').modal('hide'));
  $('#close-delete-account-modal-small').on('click', () => $('#delete-account-modal').modal('hide'));

  $('#confirmed-delete-account').on('click', async () => {
    $('#delete-account-modal').modal('hide');
    renderToast('Deleting account...', 'info');

    /**
     * Delete account
     * @type {{status: number; message: string;}}
     */
    const response = await fetch('/api/v1/user/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': getAccessToken()
      },
      body: JSON.stringify({ user_id: user_id })
    }).then(async res => await res.json());

    if (response.status === 200) {
      renderToast(response.message, 'success');
      window.location = '/';
    } else {
      renderToast(response.message, 'danger');
    };

  });
})
