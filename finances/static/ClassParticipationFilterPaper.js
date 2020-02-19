// DONE don't update options on every focus
// DONE add listeners to new fieldsets

// TODO make selection 100% wide
// TODO limit js only to the change page (also for adding participant papers)
// TODO options should be at the select box not jumping outside
// TODO when updating options keep the selected one?
// TODO set paper used to none if the participant is changed
// TODO remove original choices
// TODO check if paper belongs to a participant after save
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
      accumulator + optConstructor(currVal.id, currVal.name, currVal.days_in_use, currVal.times_used),
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
    // this.updatePaperOptions()
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

  addPaperFieldOnFocusListener = () => {
    this.paperUsedField.addEventListener('focus', this.updatePaperOptions)
  }

  updatePaperOptions = () => {
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
      papers => {
        const options = constructOptions(papers['participantPapers'])
        this.paperUsedField.innerHTML = options
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
  form.addPaperFieldOnFocusListener()
  return form
}

function selectClassParticipationSets() {
  const fieldsetClass = 'class-participation-fieldset'
  const fieldset = document.getElementsByClassName(fieldsetClass)[0]
  const forms = []
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

document.addEventListener('DOMContentLoaded', ()=> {setTimeout(main, 1000)})
