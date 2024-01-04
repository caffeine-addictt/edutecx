
let code = '';
let times = 0;

/**
 * Send Resend Request
 * @param {MouseEvent} e
 * @returns {Promise<void>}
 */
const sendResendRequest = async e => {
  $('#resend-email-button').attr('disabled', true);
  $('#resend-email-button').text('Sending...');
  renderToast('Requesting verification email...', 'info');

  /** 
   * @type {{
   *   status : number;
   *   message: string;
   * }}
   */
  const response = await fetch('/api/v1/send-verification-email', {
    method: 'POST',
    headers: { 'X-CSRF-TOKEN': getAccessToken() }
  }).then(async res => await res.json())


  if (response.status === 200) {
    renderToast(response.message, 'success');
  }
  else {
    renderToast(response.message, 'danger');
  };

  // Countdown
  let countdown;
  let iterations = 0;
  const iterationsRequired = ((2 ** times) + 30);
  countdown = setInterval(() => {
    if (iterations === iterationsRequired) {
      clearInterval(countdown);
      $('#resend-email-button').text('Resend Email');
      $('#resend-email-button').attr('disabled', false);
    }
    else {
      $('#resend-email-button').text(`Resend Email (${iterationsRequired - iterations}s)`);
      iterations++;
    };
  }, 1000);
}




/**
 * Send Verify Request
 * @param {MouseEvent} e
 * @returns {Promise<void>}
 */
const sendVerifyRequest = async e => {
  $('#verify-email-button').attr('disabled', true);

  if (!code || code === '') {
    renderToast('Please enter verification code', 'danger');
    $('#verify-email-button').attr('disabled', false);
    return;
  }

  renderToast('Verifying email...', 'info');

  /**
   * @type {{
   *   status : number;
   *   message: string;
   * }}
   */
  const response = await fetch('/api/v1/verify-email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': getAccessToken()
    },
    body: JSON.stringify({
      token: code
    })
  }).then(async res => await res.json())

  if (response.status === 200) {
    renderToast(response.message, 'success');
    setTimeout(() => window.location = '/', 2000);
    return;
  }
  else {
    renderToast(response.message, 'danger');

    // Countdown
    let countdown;
    let iterations = 0;
    countdown = setInterval(() => {
      if (iterations === 10) {
        clearInterval(countdown);
        $('#verify-email-button').text('Verify Email');
        $('#verify-email-button').attr('disabled', false);
      }
      else {
        $('#verify-email-button').text(`Verify Email (${10 - iterations}s)`);
        iterations++;
      };
    })
  }
}




$(async () => {
  // Hook on render
  $('#verification-code').on('input', e => code = e.target.value)
  $('#verify-email-button').on('click', async e => await sendVerifyRequest(e))
  $('#resend-email-button').on('click', async e => await sendResendRequest(e))
})
