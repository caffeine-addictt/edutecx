
/**
 * Track how many times graph is drawn to apply weighted cooldown
 * @type {number}
 */
let times = 0;




/**
 * Fetch and draw graph
 * @returns {Promise<void>}
 */
const fetchGraphURI = async () => {
  $('#graph__button').attr('disabled', true);
  $('#graph__button').text('Drawing...');
  renderToast('Drawing Graph...', 'info');

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
}




/**
 * Stream filtered query
 * @returns {Promise<void>}
 */
const fetchUserData = async () => {
  $('#user__button').attr('disabled', true);
  $('#user__button').text('Fetching...');
  renderToast('Fetching users...', 'info');

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
  const response = await fetch(`/dashboard/get?${searchParams.toString()}`, {
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
    // Render no users
  }
  else {
    $('#user__container').empty();
    response.data.forEach(user => {
      // Render macros for users
      $('#user__container').append(`${user.username}`);
    });
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
}




// Run in parallel
$(() => Promise.all([ fetchGraphURI(), fetchUserData() ])
  .then(values => console.log(values))
  .catch(err => console.log(err)));


$(() => {
  // Hooks
  $('#graph__button').on('click', async e => await fetchGraphURI());
  $('#user__button').on('click',  async e => await fetchUserData());
});
