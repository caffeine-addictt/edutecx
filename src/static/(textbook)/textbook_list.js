
/**
 * Textbooks List
 * @type {Array.<TextbookGetData>}
 */
let textbookList = [];

/** @type {AbortController?} */
let fetchController;




/**
 * Fetch Textbooks
 * @returns {Promise<Array.<TextbookGetData>>}
 */
const fetchTextbooks = async () => {
  // Abort previous
  if (fetchController) fetchController.abort();
  fetchController = new AbortController();

  let searchParams = ((new URL(location.href)).searchParams);
  let criteria = searchParams.get('criteria');
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or';

  searchParams.set('criteria', criteria);


  /** @type {APIJSON<TextbookGetData[]> | void} */
  const data = await fetch(`/api/v1/textbook/list?${searchParams.toString()}`, {
    method: 'GET',
    headers: { 'X-CSRF-TOKEN': getAccessToken() },
    signal: fetchController.signal
  }).then(res => res.json()).catch(e => console.log(e));

  if (!data || data.status !== 200) {
    renderToast('Failed to fetch textbooks', 'danger');
    if (data) console.log(data.message);
    return data?.data || new Array();
  };

  return data.data;
};




/**
 * Render Classrooms
 * @param {Array.<TextbookGetData>?} filteredList
 * @returns {Promise<void>}
 */
const renderTextbooks = async (filteredList) => {
  const container = $('#textbooks__container');
  container.empty();

  if ((filteredList || textbookList).length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0" style="text-align:center;">
        You do not have any textbooks.
        Purchase one <a href='/store'>here</a>!
      </p>`
    ));
  }
  else {
    template = deepCopy(cardTemplate);
    (filteredList || textbookList).forEach(textbookData => {
      container.append(htmlToElement(formatString(template, {
        title: textbookData.title,
        description: textbookData.description,
        id: textbookData.id
      })));
    });
  };
};




// On DOM Render
$(async () => {
  textbookList = await fetchTextbooks();
  renderTextbooks();


  // Hooks
  const searchInput = $('#searchbar');
  searchInput.on('input', () => {
    renderTextbooks(filterTextbooks(textbookList, searchInput.val()));
  });
});
