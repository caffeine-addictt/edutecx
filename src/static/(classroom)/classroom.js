// On DOM render
$(() => {
  var invite_link = location.host + '/classrooms/join/' + invite_id;
  $('#invite-link').text(invite_link);
  $('#invitebutton').on('click', e => {
  $('#invite-link-modal').modal('show');
  console.log("clicked invite")
});

$('#close-invite-link-modal-big').on('click', e => $('#invite-link-modal').modal('hide'));
$('#close-invite-link-modal-small').on('click', e => $('#invite-link-modal').modal('hide'));

$('#confirm-copy-invite-link').on('click', async e => {
  navigator.clipboard.writeText(invite_link);
  renderToast('Link Copied!', 'success')
})
})
