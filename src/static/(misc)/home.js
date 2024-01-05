

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
  let tpage = searchParams.get('tpage');
  tpage = tpage ? tpage : 1;
  searchParams.set('tpage', tpage);

  textbookFetchController = new AbortController();

  /**
   * @type {{
   *   status : 200;
   *   message: string;
   *   data: Array.<{
   *     user_id            : string;
   *     textbook_id        : string;
   *     editabletextbook_id: string;
   *     uri                : string;
   *     status             : 'Uploading' | 'Uploaded';
   *     created_at         : number;
   *     updated_at         : number;
   *   }>;
   * } | {
   *   status : 500;
   *   message: string;
   * }}
   */
  const response = await fetch(`/api/v1/textbook/list?${searchParams.toString()}`, {
    method: 'GET',
    signal: textbookFetchController.signal
  }).then(async res => await res.json());

  if (response.status !== 200) {
    renderToast(response.message, 'danger');
  }
  else {
    response.data.forEach((item) => {
      $('#textbook__container').append(htmlToElement(`${item.uri}`));
    })
  }

  // Undisable forward/previous button
}



// Initial Render
$(() => {
  renderTextbookPage();

})
