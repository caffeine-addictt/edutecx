
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
    classroomList.data.forEach(classroomData => {
      container.append(htmlToElement(
        `<div class="classroom__card rounded-3">
          <a href="/classroom/${classroomData.id}" class="d-flex flex-row gap-4 align-items-center">
            <img src="${classroomData.cover_image || '/static/assets/images/classroom_default.jpg'}" alt="Classroom Cover Image" />

            <h3 class="text-secondary fs-5 mb-0">
              ${classroomData.title}
            </h3>

          </a>
        </div>`));
    });
  };
};



// On DOM Render
$(() => {
  renderClassrooms();
});