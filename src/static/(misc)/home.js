

/**
 * Textbook fetch controller to stop fetch request
 * @type {AbortController | null}
 */
let textbookFetchController;




/**
 * Render textbook page based on `tpage` searchparams
 * @returns {Promise<void>}
 */
const renderTextbookPage = async () => {
  // Disable forward/previous button

  textbookFetchController?.abort();
  $('#textbook__container').empty();

  // Render dummy

  let searchParams = ((new URL(location.href)).searchParams);
  let page = searchParams.get('page');
  page = page ? page : 1;
  searchParams.set('page', page);

  textbookFetchController = new AbortController();

  /**
   * @type {APIJSON<TextbookGetData[]>}
   */
  const response = await fetch(`/api/v1/textbook/list?${searchParams.toString()}`, {
    method: 'GET',
    signal: textbookFetchController.signal
  }).then(res => res.json()).catch(err => console.log(err));

  if (!response || response.status !== 200) {
    renderToast(response ? response.message : 'Something went wrong!', 'danger');
  }
  else {
    response.data.forEach((item) => {
      $('#textbook__container').append(htmlToElement(`${item.uri}`));
    });
  };

  // Undisable forward/previous button
};



// Initial Render
$(() => {
  renderTextbookPage();
});
