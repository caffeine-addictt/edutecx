
/**
 * Render Classrooms
 * @returns {Promise<void>}
 */
const renderClassrooms = async () => {
  /**
   * @type {{
   *   status: number;
   *   message: string;
   *   data: Array.<{
   *     id: string;
   *     title: string;
   *     description: string;
   *     cover_image: string | null;
   *     created_at: number
   *   }>
   * }}
   */
  const classroomList = await fetch('/api/v1/classroom/list', {
    method: 'GET',
    headers: { 'X-CSRF-TOKEN': getAccessToken() }
  }).then(res => res.json());
  console.log(classroomList)

  if (classroomList.status !== 200) return renderToast(classroomList.message, 'danger');

  const container = $('#classroom__container');
  if (classroomList.data.length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        You are not in any classrooms. Ask your teacher for a classroom invite link.
      </p>`
    ));
  }
  else {
    template = deepCopy(tile);
    classroomList.data.forEach(classroomData => {
      container.append(htmlToElement(formatString(template, { title: classroomData.title, teacher: classroomData.owner_id })));
    });
  };
};



// On DOM Render
$(() => {
  renderClassrooms();
});