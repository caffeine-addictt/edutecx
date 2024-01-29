
/**
 * Textbooks List
 * @type {Array.<TextbookGetData>}
 */
let textbookList = [];




/**
 * Fetch Textbooks
 * @returns {Promise<Array.<TextbookGetData>>}
 */
const fetchTextbooks = async () => {
  let searchParams = ((new URL(location.href)).searchParams);
  let criteria = searchParams.get('criteria');
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or';

  searchParams.set('requestFor', 'Sale');
  searchParams.set('criteria', criteria);


  /** @type {APIJSON<TextbookGetData[]> | void} */
  const data = await fetch(`/api/v1/textbook/list?${searchParams.toString()}`, {
    method: 'GET',
    headers: { 'X-CSRF-TOKEN': getAccessToken() }
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
      `<p class="text-secondary fs-5 mb-0">
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
  classroomList = await fetchTextbooks();
  renderTextbooks();


  // Hooks
});
