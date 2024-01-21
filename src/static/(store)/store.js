
/**
 * Textbooks List
 * @type {Array.<{
 *   id: string;
 *    id: string;
 *   title: string;
 *   description: string;
 *   categories: string[];
 *   price: number;
 *   uri: string;
 *   status: 'Available' | 'Unavailable' | 'DMCA';
 *   cover_image: string | null;
 *   created_at: number;
 *   updated_at: number;
 * }>}
 */
let textbookList = [];




/**
 * Fetch Textbooks
 * @type {Promise<Array.<{
 *   id: string;
 *   author_id: string;
 *   title: string;
 *   description: string;
 *   categories: string[];
 *   price: number;
 *   uri: string;
 *   status: 'Available' | 'Unavailable' | 'DMCA';
 *   cover_image: string | null;
 *   created_at: number;
 *   updated_at: number;
 * }>>}
 */
const fetchTextbooks = async () => {
  let searchParams = ((new URL(location.href)).searchParams);
  let criteria = searchParams.get('criteria');
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or';

  searchParams.set('criteria', criteria);

  /**
   * @type {{
   *   status: number;
   *   message: string;
   *   data?: Array.<{
   *     id: string;
   *     author_id: string;
   *     title: string;
   *     description: string;
   *     categories: string[];
   *     price: number;
   *     uri: string;
   *     status: 'Available' | 'Unavailable' | 'DMCA';
   *     cover_image: string | null;
   *     created_at: number;
   *     updated_at: number;
   *   }>
   * } | void}
   */
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
 * @param {Array.<{
 *   id: string;
 *   author_id: string;
 *   title: string;
 *   description: string;
 *   categories: string[];
 *   price: number;
 *   uri: string;
 *   status: 'Available' | 'Unavailable' | 'DMCA';
 *   cover_image: string | null;
 *   created_at: number;
 *   update_at: number;
 * }>?} filteredList
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
        id: textbookData.id,
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
