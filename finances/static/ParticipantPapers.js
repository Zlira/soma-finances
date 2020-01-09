function addPaperFilters(event) {
  var participantEl = document.getElementById('id_classparticipation_set-2-participant')
  participantEl.addEventListener('change', function() {
      var url = new URL(
        '/finances/participant_papers/',
        window.location.protocol + '//' + window.location.host
      )
      if (!this.value) {return}
      url.search = new URLSearchParams({participant_id: this.value})
      fetch(url)
       .then(res => res.json())
       .then(res => {
           var options = constructOptions(res.participantPapers)
           setOptions("id_classparticipation_set-2-paper_used", options)
       })
  })
}


function setOptions(elId, options) {
    document.getElementById(elId).innerHTML = options
}


function constructOptions(participantPapers) {
  var optConstructor = (value, name) => `<option value="${value}">${name}</option>`
  var option = optConstructor('', '--------&nbsp;')
  return participantPapers.reduce(
    (acumulator, currVal) => acumulator + optConstructor(currVal.id, currVal.name),
    option
  )
}

document.addEventListener('DOMContentLoaded', addPaperFilters)
