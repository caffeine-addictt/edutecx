
/**
 * Classrooms List
 * @type {Array.<{
*     id: string;
*     owner_id: string;
*     owner_username: string;
*     title: string;
*     description: string;
*     cover_image: string | null;
*     created_at: number
 * }>}
 */
let classroomList = [];




/**
 * Fetch Classrooms
 * @type {Promise<Array.<{
 *   id: string;
 *   owner_id: string;
 *   owner_username: string;
 *   title: string;
 *   description: string;
 *   cover_image: string | null;
 *   created_at: number
 * }>>}
 */
const fetchClassrooms = async () => {

  /**
   * @type {{
   *   status: number;
   *   message: string;
   *   data: Array.<{
   *     id: string;
   *     owner_id: string;
   *     owner_username: string;
   *     title: string;
   *     description: string;
   *     cover_image: string | null;
   *     created_at: number
   *   }>
   * } | null}
   */
  const data = await fetch('/api/v1/classroom/list', {
    method: 'GET',
    headers: { 'X-CSRF-TOKEN': getAccessToken() }
  }).then(res => {
    if (res.ok) {
      return res.json();
    };
  });

  if (!data || data.status !== 200) {
    renderToast('Failed to fetch classrooms', 'danger');
    if (data) console.log(data.message);
    return data?.data || new Array();
  };

  return data.data
}




/**
 * Render Classrooms
 * @returns {Promise<void>}
 */
const renderClassrooms = async () => {
  const container = $('#classroom__container');
  container.empty();

  if (classroomList.length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        You are not in any classrooms. 
        Join with an invite link or <a href='/classrooms/new'>create one</a>!
      </p>`
    ));
  }
  else {
    template = deepCopy(tile);
    classroomList.forEach(classroomData => {
      container.append(htmlToElement(formatString(template, {
        title: classroomData.title,
        teacher: classroomData.owner_username,
        id: classroomData.id
      })));
    });
  };
};




// On DOM Render
$(async () => {
  classroomList = await fetchClassrooms();
  renderClassrooms();
});


// Hooks
$(() => {
  // TODO: Handle query and filtering
})
