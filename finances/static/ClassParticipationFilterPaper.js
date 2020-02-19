// DONE don't update options on every focus
// DONE add listeners to new fieldsets
// DONE limit js only to the change page (also for adding participant papers)
// DONE options should be at the select box not jumping outside
// DONE set paper used to none if the participant is changed

// ?TODO make selection 100% wide
// TODO remove original choices
// TODO check if paper belongs to a participant after save
// TODO test on both change and add pages
// TODO after all of this is complete deploy to pythonanywhere


async function fetchParticipantsPapers(participant_id) {
  const protocol = window.location.protocol;
  const host = window.location.host;
  const path = `finances/participant/${participant_id}/papers`;
  const url = new URL(`${protocol}//${host}/${path}`)
  const response = await fetch(url)
  return await response.json()
}


function constructOptions(participantPapers) {
  var optConstructor = (value, name, daysInUse, timesUsed) =>
    `<option value="${value}">${name} (використовується ${daysInUse} днів, ${timesUsed} раз)</option>`
  const emptyOption = '<option value="">--------&nbsp;</option>'
  return participantPapers.reduce(
    (accumulator, currVal) =>
      accumulator + optConstructor(currVal.id, currVal.name,
                                   currVal.days_in_use, currVal.times_used),
    emptyOption
  )
}


class ParticipationForm {
  constructor(node) {
    this.node = node
    this.participantField = this.node.querySelector(
      '.field-participant select'
    )
    this.paperUsedField = this.node.querySelector(
      '.field-paper_used select'
    )
  }

  init = () => {
    // this incidentally also updates the fields when the page
    // is loaded, because select2 initialization triggers 'change' event
    // but, maybe this should be done explicitly
    this.addParticipantChangeListener()
  }

  getCurrentParticipantId = () => {
    const participantData = (
      django.jQuery('#' + this.participantField.id)
      .select2('data')
    )
    if (participantData.length > 0) {
      return participantData[0].id
    }
    return null
  }

  getCurrentPaperId = () => {
    return parseInt(this.paperUsedField.value)
  }

  addParticipantChangeListener = () => {
    django.jQuery(this.participantField).on(
      'change', this.updatePaperOptions
    )
  }

  updatePaperOptions = () => {
    const currentPaperId = this.getCurrentPaperId()
    const participantId = this.getCurrentParticipantId()
    if (participantId === this.paperOptionsSetFor) {
      return
    }
    if (!participantId) {
      this.paperUsedField.innerHTML = constructOptions([])
      this.paperOptionsSetFor = participantId
      return
    }
    fetchParticipantsPapers(participantId).then(
      response => {
        const papers = response['participantPapers']
        const options = constructOptions(papers)
        this.paperUsedField.innerHTML = options
        if (papers.map(paper => paper.id).includes(currentPaperId)) {
          this.paperUsedField.value = currentPaperId
        }
        this.paperOptionsSetFor = participantId
      }
    )
  }

}


function* getFormsFromParticipationSet(fieldset) {
  const nodes = fieldset.querySelectorAll('table tbody tr')
  for (const node of nodes) {
    if (node.id.startsWith('classparticipation_set') &&
       !node.classList.contains('empty-form')) {
      yield node
    }
  }
}


function initParticipantForm(formNode) {
  const form = new ParticipationForm(formNode)
  form.init()
  return form
}


function selectClassParticipationSets() {
  const fieldsetClass = 'class-participation-fieldset'
  const fieldset = document.getElementsByClassName(fieldsetClass)[0]
  for (const formNode of getFormsFromParticipationSet(fieldset)) {
    initParticipantForm(formNode)
  }
}


function main() {
  selectClassParticipationSets()
  django.jQuery(document).on(
    'formset:added',
    (e, row, formsetName) => {
      if (formsetName === 'classparticipation_set') {
        initParticipantForm(row[0])
      }
    })
}

document.addEventListener('DOMContentLoaded', main)
