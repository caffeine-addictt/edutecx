
/**
 * Render textbook page
 * @returns {Promise<void>}
 */
const renderTextbooks = async () => {
  $('#textbook__container').empty();

  /** @type {APIJSON<TextbookGetData[]>} */
  const response = await fetch('/api/v1/textbook/owned?per_page=4&max_per_page=4&criteria=or')
    .then(res => res.json())
    .catch(err => console.log(err));

  if (!response || response.status !== 200) {
    renderToast(response ? response.message : 'Something went wrong fetching textbooks!', 'danger');

  }
  else if (!!!response.data.length) {
    $('#textbook__container').append(htmlToElement(
      `
      <a class="col text-decoration-none" href="/store" style="max-width:15rem;">
        <div class="card mb-3 mt-5">
          <div class="card-body d-flex flex-column align-items-center justify-content-center">
            <img alt="Add textbooks" src="/static/assets/icons/add_icon.png" class="img-fluid mb-4" style="min-width:200px; max-width:200px; min-height:220px; max-height:220px;">
            <h5 class="card-title text-dark fw-bold text-center mb-0">
              Browse textbooks
            </h5>
          </div>
        </div>
      </a>
      `
    ))

  }
  else {
    response.data.slice(0, 3).forEach((item) => {
      $('#textbook__container').append(htmlToElement(formatString(deepCopy(textbookTemplate), {
        title: item.title,
        description: item.description,
        id: item.id,
        uri: item.cover_image ?? ''
      })))
    });
  };
};


/**
 * Render classroom page
 * @returns {Promise<void>}
 */
const renderClassrooms = async () => {
  $('#classroom__container').empty();

  /** @type {APIJSON<ClassroomGetData[]>} */
  const response = await fetch('/api/v1/classroom/list?per_page=4&max_per_page=4&criteria=or')
    .then(res => res.json())
    .catch(err => console.log(err));

  if (!response || response.status !== 200) {
    renderToast(response ? response.message : 'Something went wrong fetching classrooms!', 'danger');
  }
  else if (!!!response.data.length) {
    $('#classroom__container').append(htmlToElement(
      `
      <a class="col text-decoration-none" href="/classrooms/new" style="max-width:15rem;">
        <div class="card mb-3 mt-5">
          <div class="card-body d-flex flex-column align-items-center justify-content-center">
            <img alt="Add Class" src="/static/assets/icons/add_icon.png" class="img-fluid mb-4" style="min-width:200px; max-width:200px; min-height:220px; max-height:220px;">
            <h5 class="card-title text-dark fw-bold text-center mb-0">
              Create Classroom
            </h5>
          </div>
        </div>
      </a>
      `
    ))
  } else {
    response.data.slice(0, 3).forEach((item) => {
      $('#classroom__container').append(htmlToElement(formatString(deepCopy(classroomTemplate), {
        title: item.title,
        id: item.id
      })))
    });
  };
};


// Initial Render
$(() => Promise.all([
  renderTextbooks().then(() => console.log('Fetched and rendered textbooks')).catch(err => console.log('Failed to fetch textbooks: ' + err)),
  renderClassrooms().then(() => console.log('Fetched and rendered classrooms')).catch(err => console.log('Failed to fetch classrooms: ' + err)),
]).then(() => console.log('Fetched and rendered!')).catch(err => console.log(err)));
