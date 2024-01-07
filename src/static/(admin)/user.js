
// let userTemplate = '';

/**
 * Track how many times graph is drawn to apply weighted cooldown
 * @type {number}
 */
let times = 0;




/**
 * Fetch and draw graph
 * @param {boolean} initialRender - Whether this is the initial render
 * @returns {Promise<void>}
 */
const fetchGraphURI = async (initialRender = false) => {
  $('#graph__button').attr('disabled', true);
  $('#graph__button').text('Drawing...');
  if (!initialRender) renderToast('Drawing Graph...', 'info');

  $('#svg-render').empty();

  /**
   * @type {Response}
   */
  const response = await fetch('/dashboard/graph', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': getAccessToken()
    },
    body: JSON.stringify({
      "graphFor": "User"
    })
  })

  if (!response.ok) {
    renderToast('Failed to fetch Graph', 'danger');
  }
  else {
    const svg = await response.text();
  
    $('#svg-render').empty();
    $('#svg-render').append(htmlToElement(svg));
    console.log('Fetched SVG')
  };

  // Countdown
  let countdown;
  let iterations = 0;
  const iterationsRequired = ((2 ** times) + 30);
  countdown = setInterval(() => {
    if (iterations === iterationsRequired) {
      clearInterval(countdown);
      $('#graph__button').text('Resend Email');
      $('#graph__button').attr('disabled', false);
    }
    else {
      $('#graph__button').text(`Resend Email (${iterationsRequired - iterations}s)`);
      iterations++;
    };
  }, 1000);

  times++;
};




/**
 * Render user entry
 * @param {{
 *   user_id      : string;
 *   email        : string;
 *   status       : 'Active' | 'Locked';
 *   username     : string;
 *   privilege    : 'Student' | 'Educator' | 'Admin';
 *   profile_image: string | null;
 *   created_at   : number;
 *   last_login   : number;
 * }} user - The user to render
 * @returns {void}
 */
const renderUser = (user) => {
  const newEntry = htmlToElement(formatString(deepCopy(userTemplate), {
    'user_id'      : user.user_id,
    'user_email'   : user.email,
    'user_status'  : user.status,
    'user_type'    : user.privilege,
  }));

  // Add hooks
  if (user.privilege === 'Admin') {
    $(newEntry).find('#user__manage_button').remove();
  }
  else {
    $(newEntry).find('#user__manage_button').on('click', () => {
      const username = $('#update-user-username');
      const email = $('#update-user-email');
      const status = $('#update-user-status');
      const privilege = $('#update-user-privileges');

      // Change modal values
      $('#modal-long-title').text(`Manage ${user.username}`);
      username.val(user.username);
      email.val(user.email);
      status.val(user.status);
      privilege.val(user.privilege);
  
      // Add hooks
      const submitButton = $('#update-user-modal').find('#confirmed-update-user')
      submitButton.on('click', async () => {
        submitButton.attr('disabled', true);
        submitButton.text('Updating...');

        const response = await fetch('/api/v1/user/edit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getAccessToken()
          },
          body: JSON.stringify({
            "user_id": user.user_id,
            "username": user.username !== username.val() ? username.val() : '',
            "email": user.email !== email.val() ? email.val() : '',
            "status": user.status !== status.val() ? status.val() : '',
            "privilege": user.privilege !== privilege.val() ? privilege.val() : '',
          })
        }).then(res => {
          if (res.ok) {
            return res.json();
          };
        });


        if (!response || response.status !== 200) {
          renderToast(response ? response.message : 'Failed to update user', 'danger');
        }
        else {
          if (response.message) renderToast(response.message, 'success');
          fetchUserData();
        };

        submitButton.text('Update Account');
        $('#update-user-modal').modal('hide');
        submitButton.off('click');
        submitButton.attr('disabled', false);
      });
  
  
      // Show modal
      $('#update-user-modal').modal('show');
    });
  };

  $('#user__container').append(newEntry);
}




/**
 * Stream filtered query
 * @param {boolean} initialRender - Whether this is the initial render
 * @returns {Promise<void>}
 */
const fetchUserData = async (initialRender = false) => {
  $('#user__button').attr('disabled', true);
  $('#user__button').text('Fetching...');
  if (!initialRender) renderToast('Fetching users...', 'info');

  $('#user__container').empty();

  let searchParams = ((new URL(location.href)).searchParams)
  let criteria = searchParams.get('criteria')
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or'

  searchParams.set('requestFor', 'User')
  searchParams.set('criteria', criteria)

  /**
   * @type {{
   *   status : 200;
   *   message: string;
   *   data: Array.<{
   *     user_id      : string;
   *     email        : string;
   *     status       : 'Active' | 'Locked';
   *     username     : string;
   *     privilege    : 'Student' | 'Educator' | 'Admin';
   *     profile_image: string | null;
   *     created_at   : number;
   *     last_login   : number;
   *   }>;
   * } | {
   *   status: 500;
   *   message: string;
   * }}
   */
  const response = await fetch(`/api/v1/user/list?${searchParams.toString()}`, {
    method: 'GET',
    headers: {
      'X-CSRF-TOKEN': getAccessToken()
    }
  }).then(async res => await res.json())

  if (response.status !== 200) {
    console.log(response.message);
    renderToast('Failed to fetch users!', 'danger');
  }
  else if (!response.data || response.data.length === 0) {
    $('#user__container').empty();
    $('#user__container').append('<p class="text-center">No users found</p>');
  }
  else {
    $('#user__container').empty();
    response.data.forEach(renderUser);
  };
  
  // Countdown
  let countdown;
  let iterations = 0;
  countdown = setInterval(() => {
    if (iterations === 30) {
      clearInterval(countdown);
      $('#user__button').text('Reload Users');
      $('#user__button').attr('disabled', false);
    }
    else {
      $('#user__button').text(`Reload Users (${30 - iterations}s)`);
      iterations++;
    };
  }, 1000);
};




// Run in parallel
$(() => Promise.all([ fetchGraphURI(), fetchUserData() ])
  .then(values => console.log(values))
  .catch(err => console.log(err)));


$(() => {
  // Hooks
  $('#graph__button').on('click', async e => await fetchGraphURI(true));
  $('#user__button').on('click',  async e => await fetchUserData(true));

  // Modal hooks
  $('#update-user-modal').find('#close-update-user-modal-big').on('click', () => {
    $('#update-user-modal').find('#confirm-update-user').off('click');
    $('#update-user-modal').modal('hide');
  });
  $('#update-user-modal').find('#close-update-user-modal-small').on('click', () => {
    $('#update-user-modal').find('#confirm-update-user').off('click');
    $('#update-user-modal').modal('hide');
  });
});
