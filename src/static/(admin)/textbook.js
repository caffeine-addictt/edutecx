
// let textbookTemplate = '';

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
      "graphFor": "Textbook"
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
};




/**
 * Stream filtered query
 * @param {boolean} initialRender - Whether this is the initial render
 * @returns {Promise<void>}
 */
const fetchTextbookData = async (initialRender = false) => {
  $('#textbook__button').attr('disabled', true);
  $('#textbook__button').text('Fetching...');
  if (!initialRender) renderToast('Fetching textbooks...', 'info');

  $('#textbook__container').empty();

  let searchParams = ((new URL(location.href)).searchParams)
  let criteria = searchParams.get('criteria')
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or'

  searchParams.set('requestFor', 'Textbook')
  searchParams.set('criteria', criteria)

  /**
   * @type {{
   *   status : 200;
   *   message: string;
   *   data: Array.<{
   *     id: string;
   *     author_id: string;
   *     title: string;
   *     description: string;
   *     categories: string[];
   *     price: number;
   *     discount: number;
   *     uri: string;
   *     status: 'Uploading' | 'Uploaded';
   *     cover_image: string | null;
   *     created_at: number;
   *     updated_at: number;
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
    renderToast('Failed to fetch textbooks!', 'danger');
  }
  else if (!response.data || response.data.length === 0) {
    // Render no textbooks
  }
  else {
    $('#textbook__container').empty();
    response.data.forEach(textbook => {
      // Render macros for textbooks
      $('#textbook__container').append(`${textbook.title}`);
    });
  };
  
  // Countdown
  let countdown;
  let iterations = 0;
  countdown = setInterval(() => {
    if (iterations === 30) {
      clearInterval(countdown);
      $('#textbook__button').text('Reload Textbooks');
      $('#textbook__button').attr('disabled', false);
    }
    else {
      $('#textbook__button').text(`Reload Textbooks (${30 - iterations}s)`);
      iterations++;
    };
  }, 1000);
};




// Run in parallel
$(() => Promise.all([ fetchGraphURI(), fetchTextbookData() ])
  .then(values => console.log(values))
  .catch(err => console.log(err)));


$(() => {
  // Hooks
  $('#graph__button').on('click', async e => await fetchGraphURI(true));
  $('#textbook__button').on('click',  async e => await fetchTextbookData(true));

  // Modal hooks
  $('#update-tetxbook-modal').find('#close-update-tetxbook-modal-big').on('click', () => {
    $('#update-tetxbook-modal').find('#confirm-update-tetxbook').off('click');
    $('#update-tetxbook-modal').modal('hide');
  });
  $('#update-tetxbook-modal').find('#close-update-tetxbook-modal-small').on('click', () => {
    $('#update-tetxbook-modal').find('#confirm-update-tetxbook').off('click');
    $('#update-tetxbook-modal').modal('hide');
  });
});
