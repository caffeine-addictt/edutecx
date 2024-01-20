
// let textbookTemplate = '';

/**
 * Track how many times graph is drawn to apply weighted cooldown
 * @type {number}
 */
let times = 0;

/**
 * The mounted modal callback
 * True will close the modal, false will not
 * @type {null | () => Promise<boolean>}
 */
let modalCallback;

/**
 * The mounted modal reset
 * @type {null | () => void}
 */
let modalReset;




/**
 * Render Modal Error
 * @param {string} message
 * @returns {void}
 */
const renderModalError = (message) => {
  $('#update-textbook-error').text(message);
  $('#update-textbook-error-parent').removeClass('d-none');
};




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
 * Render textbook entry
 * @param {{
 *   id: string;
 *   author_id: string;
 *   title: string;
 *   description: string;
 *   categories: string[];
 *   price: number;
 *   discount: number;
 *   uri: string;
 *   status: 'Uploading' | 'Uploaded';
 *   cover_image: string | null;
 *   created_at: number;
 *   updated_at: number;
 * }} textbook - The textbook to render
 * @returns {void}
 */
const renderTextbook = (textbook) => {
  const newEntry = htmlToElement(formatString(deepCopy(textbookTemplate), {
    'textbook_id'       : textbook.id,
    'textbook_author'   : textbook.author_id,
    'textbook_title'    : textbook.title,
    'textbook_price'    : textbook.price,
    'textbook_discount' : textbook.discount,
    'textbook_status'   : textbook.status
  }));

  // Add hooks
  $(newEntry).find('#textbook__manage_button').on('click', () => {
    const title = $('#update-textbook-title');
    const categories = $('#update-textbook-categories');
    const price = $('#update-textbook-price');
    const discount = $('#update-textbook-discount');
    const status = $('#update-textbook-status');

    // Change modal values
    $('#modal-long-title').text(`Manage ${textbook.title}`);
    title.val(textbook.title);
    categories.val(textbook.categories);
    price.val(textbook.price);
    discount.val(textbook.discount);
    status.val(textbook.status);

    // Add hooks
    console.log('Mounting modal callback...')
    const submitButton = $('#update-textbook-modal').find('#confirmed-update-textbook')
    modalCallback = async () => {
      submitButton.attr('disabled', true);
      submitButton.text('Updating...');

      const response = await fetch('/api/v1/textbook/edit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-TOKEN': getAccessToken()
        },
        body: JSON.stringify({
          textbook_id: textbook.id,
          title      : textbook.title !== $('#update-textbook-title').val() ? $('#update-textbook-title').val() : null,
          categories : textbook.categories !== $('#update-textbook-categories').val() ? $('#update-textbook-categories').val() : null,
          price      : textbook.price !== parseFloat($('#update-textbook-price').val()) ? parseFloat($('#update-textbook-price').val()) : null,
          discount   : textbook.discount !== parseFloat($('#update-textbook-discount').val()) ? parseFloat($('#update-textbook-discount').val()) : null,
        })
      }).then(res => {
        try {
          return res.json();
        } catch (e) {
          renderToast('Failed to update textbook', 'danger');
          submitButton.text('Update Textbook');
          submitButton.attr('disabled', false);
          renderModalError('Failed to update textbook');
          return false;
        };
      });


      if (response.status !== 200) {
        renderToast(response.message, 'danger');
        renderModalError(response.message);
      }
      else {
        renderToast(response.message, 'success');
        fetchTextbookData(true);
      };

      submitButton.text('Update Textbook');
      submitButton.attr('disabled', false);
    };


    // Show modal
    $('#update-textbook-modal').modal('show');
    return true;
  });


  $('#textbook__container').append(newEntry);
}




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
   * } | void}
   */
  const response = await fetch(`/api/v1/textbook/list?${searchParams.toString()}`, {
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
    if (response) console.log(response.message);
    renderToast('Failed to fetch textbooks!', 'danger');
  }
  else if (!response?.data || response.data.length === 0) {
    $('#textbook__container').empty();
    $('#textbook__container').append('<p class="text-center w-100">No textbooks found</p>');
  }
  else {
    $('#textbook__container').empty();
    $('#update-textbook-category').empty();

    let renderedCategories = [];
    response.data.forEach(textbook => {
      for (const category of textbook.categories) {
        if (!renderedCategories.includes(category)) {
          $('#update-textbook-category').append(`<option value="${category}">${category}</option>`);
          renderedCategories.push(category);
        };
      };
      renderTextbook(textbook)
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




$(async () => {
  // Hooks
  $('#graph__button').on('click', async e => await fetchGraphURI());
  $('#textbook__button').on('click',  async e => await fetchTextbookData());

  // Modal hooks
  $('#update-tetxbook-modal').find('#confirmed-update-textbook').on('click', async e => {
    let closeModal = true;

    try {
      if (modalCallback) {
        closeModal = await modalCallback();
      };
    }
    finally {
      if (closeModal) {
        $('#update-textbook-modal').modal('hide');
        modalCallback = null;
        modalReset = null;
      }
      else if (modalReset) modalReset();
    };
  })
  $('#update-tetxbook-modal').find('#close-update-tetxbook-modal-big').on('click', () => {
    $('#update-tetxbook-modal').modal('hide');
    modalCallback = null;
    modalReset = null;
  });
  $('#update-tetxbook-modal').find('#close-update-tetxbook-modal-small').on('click', () => {
    $('#update-tetxbook-modal').modal('hide');
    modalCallback = null;
    modalReset = null;
  });


  // Run in parallel
  await Promise.all([ fetchGraphURI(true), fetchTextbookData(true) ])
    .then(values => console.log(values))
    .catch(err => console.log(err));
});
