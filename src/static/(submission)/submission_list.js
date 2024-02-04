
/**
 * Submission List
 * @type {SubmissionGetData[]}
 */
let submissionList = [];


/**
 * Fetch Submissions
 * @type {Promise<SubmissionGetData[]>}
 */
const fetchSubmissions = async () => {
  let searchParams = ((new URL(location.href)).searchParams);
  let criteria = searchParams.get('criteria');
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or';
  searchParams.set('criteria', criteria);

  /**
   * @type {APIJSON<SubmissionGetData[]> | void}
   */
  const data = await fetch(`/api/v1/submission/list?${searchParams.toString()}`, {
    method: 'GET',
    headers: { 'X-CSRF-TOKEN': getAccessToken() }
  }).then(res => res.json()).catch(err => console.log(err));

  if (!data || data.status !== 200) {
    renderToast('Failed to fetch submissions', 'danger');
    if (data) console.log(data.message);
    return data?.data || new Array();
  };

  return data.data;
};


/**
 * Render Submissions
 * @param {SubmissionGetData[]} filteredList
 * @returns {Promise<void>}
 */
const renderSubmissionList = async (filteredList) => {
  const container = $('#submission__container');
  container.empty();

  if ((filteredList || submissionList).length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        You have not submitted to any assignments.
      </p>`
    ));
  }
  else {
    template = deepCopy(cardTemplate);
    (filteredList || submissionList).forEach(submissionData => {
      container.append(htmlToElement(formatString(template, {
        id: submissionData.submission_id,
        submission_date: new Date(submissionData.submitted_at).toLocaleString(),
        comment_count: submissionData.comments.length,
      })));
    });
  };
};


$(() => {
  fetchSubmissions().then((/**@type{SubmissionGetData[]}*/data) => {
    submissionList = data;
    renderSubmissionList();
  });
});
