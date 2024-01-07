
// let saleTemplate = '';

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
};




/**
 * Stream filtered query
 * @param {boolean} initialRender - Whether this is the initial render
 * @returns {Promise<void>}
 */
const fetchSaleData = async (initialRender = false) => {
  $('#sale__button').attr('disabled', true);
  $('#sale__button').text('Fetching...');
  if (!initialRender) renderToast('Fetching sales...', 'info');

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
   *     type        : 'OneTime' | 'Subscription';
   *     sale_id     : string;
   *     user_id     : string;
   *     discount_id : string | null;
   *     textbook_ids: string[];
   *     paid        : number;
   *     paid_at     : number;
   *     total_cost  : number;
   *   }>;
   * } | void}
   */
  const response = await fetch(`/api/v1/sale/list?${searchParams.toString()}`, {
    method: 'GET',
    headers: {
      'X-CSRF-TOKEN': getAccessToken()
    }
  }).then(res => {
    if (res.ok) {
      return res.json();
    };
  });

  if (!response || response.status !== 200) {
    console.log(response.message);
    renderToast('Failed to fetch sales!', 'danger');
  }
  else if (!response?.data || response.data.length === 0) {
    $('#sale__container').empty();
    $('#sale__container').append('<p class="text-center">No sales found</p>');
  }
  else {
    $('#sale__container').empty();
    
    response.data.forEach(sale => {
      const newSaleEntry = htmlToElement(formatString(deepCopy(saleTemplate), {
        'sale_id'     : sale.sale_id,
        'user_id'     : sale.user_id,
        'discount_id' : sale.discount_id,
        'paid'        : sale.paid,
        'paid_date'   : (new Date(sale.paid_at)).toDateString(),
        'total_cost'  : sale.total_cost
      }))

      const textbookIds = $(newSaleEntry).find('#sale__textbookids')
      sale.textbook_ids.forEach(textbookId => {
        textbookIds.append(htmlToElement(formatString(
          '<a href="/textbook/{textbook_id}" target="_blank" class="textbook__link">{textbook_id}</a>',
          { 'textbook_id' : textbookId }
        )))
      })

      $('#sale__container').append(newSaleEntry);
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
};




// Run in parallel
$(() => Promise.all([ fetchGraphURI(true), fetchSaleData(true) ])
  .then(values => console.log(values))
  .catch(err => console.log(err)));


$(() => {
  // Hooks
  $('#graph__button').on('click', async e => await fetchGraphURI());
  $('#sale__button').on('click',  async e => await fetchSaleData());
});
