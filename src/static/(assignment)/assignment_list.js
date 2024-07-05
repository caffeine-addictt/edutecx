
/**
 * Assignments List
 * @type {AssignmentGetData[]}
 */
let assignmentList = [];




/**
 * Fetch Assignments
 * @type {Promise<AssignmentGetData[]>}
 */
const fetchAssignments = async () => {
  const searchParams = ((new URL(location.href)).searchParams);
  searchParams.set('criteria', searchParams.get('criteria') || 'or');

  /**
   * @type {APIJSON<AssignmentGetData[]> | void}
   */
  const data = await fetch(`/api/v1/assignment/list?${searchParams.toString()}`, {
    method: 'GET',
    headers: { 'X-CSRF-TOKEN': getAccessToken() }
  }).then(res => res.json()).catch(err => console.log(err));

  if (!data || data.status !== 200) {
    renderToast('Failed to fetch assignments', 'danger');
    if (data) console.log(data.message);
    return data?.data || new Array();
  };

  return data.data;
};




/**
 * Render Assignments
 * @param {AssignmentGetData[]?} filteredList
 * @returns {Promise<void>}
 */
const renderAssignments = async (filteredList) => {
  const container = $('#assignment__container');
  container.empty();

  if ((filteredList || assignmentList).length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        Yay! You do have have any pending assignments.
      </p>`
    ));
  }
  else {
    const template = deepCopy(assignmentTemplate);
    (filteredList || assignmentList).forEach(assignmentData => {
      container.append(htmlToElement(formatString(template, {
        title: assignmentData.title,
        requirements: assignmentData.requirements,
      })));
    });
  };
};




/**
 * Handle Filtering
 * @returns {void}
 */
const handleFiltering = () => {
  // TODO: Generate NEW array from `assignmentList`
  // TODO: Call renderAssignments( newFilteredAssignments );
}




// On DOM Render
$(async () => {
  assignmentList = await fetchAssignments();
  renderAssignments();
});


// Hooks
$(() => {
  // TODO: Handle query and filtering
})
