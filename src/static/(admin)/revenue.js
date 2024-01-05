
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
      "graphFor": "Revenue"
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
      $('#graph__button').text('Redraw Graph');
      $('#graph__button').attr('disabled', false);
    }
    else {
      $('#graph__button').text(`Redraw Graph (${iterationsRequired - iterations}s)`);
      iterations++;
    };
  }, 1000);

  times++;
}




/**
 * Stream filtered query
 * @returns {Promise<void>}
 */
const fetchSaleData = async () => {
  $('#sale__button').attr('disabled', true);
  $('#sale__button').text('Fetching...');
  renderToast('Fetching sales...', 'info');

  $('#sale__container').empty();

  let searchParams = ((new URL(location.href)).searchParams)
  let criteria = searchParams.get('criteria')
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or'

  searchParams.set('requestFor', 'Sale')
  searchParams.set('criteria', criteria)

  /**
   * @type {{
   *   status : 200;
   *   message: string;
   *   data: Array.<{
   * 
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
    renderToast('Failed to fetch sales!', 'danger');
  }
  else if (!response.data || response.data.length === 0) {
    // Render no sales
  }
  else {
    $('#sale__container').empty();
    response.data.forEach(sale => {
      // Render macros for sales
      $('#sale__container').append(`${sale.title}`);
    });
  };
  
  // Countdown
  let countdown;
  let iterations = 0;
  countdown = setInterval(() => {
    if (iterations === 30) {
      clearInterval(countdown);
      $('#sale__button').text('Reload Sales');
      $('#sale__button').attr('disabled', false);
    }
    else {
      $('#sale__button').text(`Reload Sales (${30 - iterations}s)`);
      iterations++;
    };
  }, 1000);
}




// Run in parallel
$(() => Promise.all([ fetchGraphURI(), fetchSaleData() ])
  .then(values => console.log(values))
  .catch(err => console.log(err)));


$(() => {
  // Hooks
  $('#graph__button').on('click', async e => await fetchGraphURI());
  $('#sale__button').on('click',  async e => await fetchSaleData());
});
