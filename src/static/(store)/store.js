
/**
 * Textbooks List
 * @type {Array.<TextbookGetData>}
 */
let textbookList = [];




/**
 * Fetch Textbooks
 * @type {Promise<Array.<TextbookGetData>>}
 */
const fetchTextbooks = async () => {
  let searchParams = ((new URL(location.href)).searchParams);
  let criteria = searchParams.get('criteria');
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or';

  searchParams.set('criteria', criteria);

  /** @type {APIJSON<TextbookGetData[]> | void} */
  const data = await fetch(`/api/v1/textbook/list?${searchParams.toString()}`, {
    method: 'GET',
    headers: { 'X-CSRF-TOKEN': getAccessToken() }
  }).then(res => {
    if (res.ok) {
      return res.json();
    };
  });
  
  if (!data || data.status !== 200) {
    renderToast('Failed to fetch textbooks', 'danger');
    if (data) console.log(data.message);
    return data?.data || new Array();
  };

  return data.data
}




/**
 * Render Textbooks
 * @param {Array.<TextbookGetData>} filteredList
 * @returns {Promise<void>}
 */
const renderTextbooks = async (filteredList = false) => {
  const container = $('#listingContainer');
  container.empty();

  if ((filteredList || textbookList).length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        No textbooks available.
      </p>`
    ));
  }
  else {
    console.log(filteredList || textbookList);
    (filteredList || textbookList).forEach(textbookData => {
      container.append(htmlToElement(formatString(deepCopy(template), {
        title: textbookData.title,
        author_id: textbookData.author_id,
        id: textbookData.id,
        price: textbookData.price,
        cover_image: textbookData.cover_image
      })));
    });
  };
};




/**
 * Handle Filtering
 * @returns {void}
 */
const handleFiltering = () => {
  // TODO: Generate NEW array from `textbookList`
  // TODO: Call renderTextbooks( newFilteredTextbooks );
}




// On DOM Render
$(async () => {
  textbookList = await fetchTextbooks();
  renderTextbooks();
});


// Hooks
$(() => {
  // TODO: Handle query and filtering
})
