
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

  // Ignore aborted
  if (fetchController?.signal?.aborted) return textbookList;

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
  searchInput.text((new URL(location.href)).searchParams.get('query') || '');

  /** @type {ReturnType<setTimeout>?} */
  let queryToRun;


  // 500ms debounce for search inputs
  searchInput.on('input', (/** @type {JQuery.Input} */e) => {
    searchInput.text(e.target.value.trim());

    if (queryToRun) {clearTimeout(queryToRun); console.log('clearing');};
    queryToRun = setTimeout(async () => {
      const searchParams = ((new URL(location.href)).searchParams);
      if (searchInput.text()) searchParams.set('query', searchInput.text());
      else searchParams.delete('query');

      const stringifiedParams = searchParams.toString();
      if (stringifiedParams === location.search) return;

      // Modify URL
      const newURL = `${location.pathname}${stringifiedParams ? `?${stringifiedParams}` : ''}`;
      if (newURL === location.href) return;

      // Modify URL if possible else Reload
      if (window?.history?.pushState) {
        window.history.pushState({}, '', newURL);

        textbookList = await fetchTextbooks();
        renderTextbooks();
      }
      else {
        location.href = newURL;
      };
    }, 500);
  });
});
