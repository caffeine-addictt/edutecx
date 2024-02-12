
/**
 * Render textbook page
 * @returns {Promise<void>}
 */
const renderTextbooks = async () => {
  $('#textbook__container').empty();

  /** @type {APIJSON<TextbookGetData[]>} */
  const response = await fetch('/api/v1/textbook/list?per_page=4&criteria=or')
    .then(res => res.json())
    .catch(err => console.log(err));

  if (!response || response.status !== 200) {
    renderToast(response ? response.message : 'Something went wrong fetching textbooks!', 'danger');
  }
  else {
    response.data.forEach((item) => {
      $('#textbook__container').append(htmlToElement(formatString(deepCopy(textbookTemplate), {
        title: item.title,
        description: item.description,
        uri: item.cover_image
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
  const response = await fetch('/api/v1/classroom/list?per_page=4&criteria=or')
    .then(res => res.json())
    .catch(err => console.log(err));

  if (!response || response.status !== 200) {
    renderToast(response ? response.message : 'Something went wrong fetching classrooms!', 'danger');
  }
  else {
    response.data.forEach((item) => {
      $('#classroom__container').append(htmlToElement(formatString(deepCopy(classroomTemplate), {
        title: item.title,
      })))
    });
  };
};


// Initial Render
$(() => Promise.all([
  renderTextbooks().then(() => console.log('Fetched and rendered textbooks')).catch(err => console.log('Failed to fetch textbooks: ' + err)),
  renderClassrooms().then(() => console.log('Fetched and rendered classrooms')).catch(err => console.log('Failed to fetch classrooms: ' + err)),
]).then(() => console.log('Fetched and rendered!')).catch(err => console.log(err)));
