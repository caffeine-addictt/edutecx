
/**
 * Textbooks List
 * @type {Array.<{
 *   id: string;
 *   author_id: string;
 *   description: string;
 *   categories: string[];
 *   price: number;
 *   discount: number;
 *   uri: string;
 *   status: 'Available' | 'Unavailable' | 'DMCA';
 *   cover_image: string | null;
 *   created_at: number;
 *   update_at: number;
 * }>}
 */
let textbookList = [];




/**
 * Fetch Textbooks
 * @type {Promise<Array.<{
 *   id: string;
 *   author_id: string;
 *   description: string;
 *   categories: string[];
 *   price: number;
 *   discount: number;
 *   uri: string;
 *   status: 'Available' | 'Unavailable' | 'DMCA';
 *   cover_image: string | null;
 *   created_at: number;
 *   update_at: number;
 * }>>}
 */
const fetchTextbooks = async () => {

  /**
   * @type {{
   *   id: string;
   *   author_id: string;
   *   description: string;
   *   categories: string[];
   *   price: number;
   *   discount: number;
   *   uri: string;
   *   status: 'Available' | 'Unavailable' | 'DMCA';
   *   cover_image: string | null;
   *   created_at: number;
   *   update_at: number;
   *  }>
   * } | null}
   */
  // const data = await fetch('/api/v1/textbook/list', {
  //   method: 'GET',
  //   headers: { 'X-CSRF-TOKEN': getAccessToken() }
  // }).then(res => {
  //   if (res.ok) {
  //     return res.json();
  //   };
  // });
  const data = {
    message: "Good",
    status: 200,
    data:[{

      id: '12345',
      author_id: '7889',
      description: 'Great',
      categories: ['nice', 'good', 'great'],
      price: 79.10,
      discount: 0.5,
      uri: 'dgfsdf324',
      status: 'Available' | 'Unavailable' | 'DMCA',
      cover_image: null,
      created_at: 100,
      update_at: 1
    }
  ]};
  
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
 *   description: string;
 *   categories: string[];
 *   price: number;
 *   discount: number;
 *   uri: string;
 *   status: 'Available' | 'Unavailable' | 'DMCA';
 *   cover_image: string | null;
 *   created_at: number;
 *   update_at: number;
 * }>?} filteredList
 * @returns {Promise<void>}
 */
const renderTextbooks = async (filteredList) => {
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
    (filteredList || textbookList).forEach(textbookData => {
      container.append(htmlToElement(formatString(deepCopy(template), {
        title: textbookData.title,
        author: textbookData.owner_username,
        id: textbookData.id
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
