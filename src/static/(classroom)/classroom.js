
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
const renderTextbooks = async (textbookTemplate, div, selected, filteredList = false) => {
  const container = $(`#${div}`);
  container.empty();
  if ((filteredList || textbookList).length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        No textbooks available.
      </p>`
    ));
  } else if (selected != null) {
    if (selected.length === 0) {
      container.append(htmlToElement(
        `<p class="text-secondary fs-5 mb-0">
          No textbooks selected.
        </p>`
      ));
    } else {
      (filteredList || textbookList).forEach(textbookData => {
      if (selected.includes(textbookData.id)) {
        container.append(htmlToElement(formatString(deepCopy(textbookTemplate), {
        title: textbookData.title,
        textbook_id: textbookData.id,
        cover_image: textbookData.cover_image
      })));
      }
    });
    }
    
  } else {
    (filteredList || textbookList).forEach(textbookData => {
      container.append(htmlToElement(formatString(deepCopy(textbookTemplate), {
        title: textbookData.title,
        textbook_id: textbookData.id,
        cover_image: textbookData.cover_image
      })));
    });
  };
};

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
  const container = $('#assignment-list');
  container.empty();

  if ((filteredList || assignmentList).length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        No pending assignments.
      </p>`
    ));
  }
  else {
    template = deepCopy(assignmentTemplate);
    (filteredList || assignmentList).forEach(assignmentData => {
      container.append(htmlToElement(formatString(template, {
        title: assignmentData.title,
        duedate: assignmentData.due_date,
      })));
    });
  };
};




// Textbook Selection
var selected = textbooks;
if (selected == undefined) {
  selected = [];
}
function toggleSelection(textbook_id) {
  if (selected.includes(textbook_id)) {
    selected.splice(selected.indexOf(textbook_id), 1);
    $(`#${textbook_id}`).find('.card-body').removeClass('border border-dark');
  } else {
    selected.push(textbook_id);
    $(`#${textbook_id}`).find('.card-body').addClass('border border-dark');
  };
  console.log(selected);
}


// On DOM render
$(async () => {
  // Invite Link
  var invite_link = location.host + '/classrooms/join/' + invite_id;
  $('#invite-link').text(invite_link);
  $('#invitebutton').on('click', e => {
    $('#invite-link-modal').modal('show');
  });

  $('#close-invite-link-modal-big').on('click', e => $('#invite-link-modal').modal('hide'));
  $('#close-invite-link-modal-small').on('click', e => $('#invite-link-modal').modal('hide'));

  $('#confirm-copy-invite-link').on('click', async e => {
    navigator.clipboard.writeText(invite_link);
    renderToast('Link Copied!', 'success')
  })

  // Textbooks
  $('#textbookbutton').on('click', async (e) => {
    $('#textbook-modal').modal('show');
      textbookList = await fetchTextbooks();
      renderTextbooks(textbookTemplate, 'textbook-select-list', null);
      for (chosen of selected) {
        console.log(chosen);
        $(`#${chosen}`).find('.card-body').addClass('border border-dark');
      }
  });

  $('#close-textbook-modal-big').on('click', e => $('#textbook-modal').modal('hide'));
  $('#close-textbook-modal-small').on('click', e => $('#textbook-modal').modal('hide'));

  $('#confirm-textbook').on('click', async e => {
    e.preventDefault();
    renderToast('Updating class textbooks...', 'info');
  
    const data = selected;
      console.log(data);
  
    /**
     * @type {{status: 200; message: string; data: { classroom_id: string }}?}
     */
      const response = await fetch('/api/v1/classroom/edit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': getAccessToken()
        },
        body: JSON.stringify({
          classroom_id: classroom_id,
          textbook_ids: selected 
        })
      }).then(res => {
        if (res.ok) {
          return res.json();
        };
      });
      if (!response || response.status !== 200) renderToast(response ? response.message : 'Something went wrong!', 'danger');
      else {
        renderToast(response.message, 'success');
        window.location.reload();
      };
  })


  console.log(textbooks);
  textbookList = await fetchTextbooks();
  renderTextbooks(chosenTextbooksTemplate, 'selected-list', textbooks)
  
  assignmentList = await fetchAssignments();
  renderAssignments();
  

  

})
