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
  }

  addParticipantChangeListener = () => {
    django.jQuery('#' + this.participantField.id).on(
      'select2:select', (e) => console.log(e.params.data)
    )
  }

  addPaperFieldOnFocusListener = () => {
    this.paperUsedField.addEventListener('focus', this.updatePaperOptions)
  }

  updatePaperOptions = () => {
    const participantId = django.jQuery('#' + this.participantField.id).select2('data')[0]['id']
    fetchParticipantsPapers(participantId).then(
      papers => {
        const options = constructOptions(papers['participantPapers'])
        this.paperUsedField.innerHTML = options
        console.log(options)
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


function selectClassParticipationSets() {
  const fieldsetClass = 'class-participation-fieldset'
  const fieldset = document.getElementsByClassName(fieldsetClass)[0]
  const forms = []
  for (const formNode of getFormsFromParticipationSet(fieldset)) {
    forms.push(new ParticipationForm(formNode))
  }

  for (const form of forms) {
    form.addPaperFieldOnFocusListener()
    form.addParticipantChangeListener()
  }
}

function main() {
  selectClassParticipationSets()
  // django.jQuery(document).on('formset:added', () => console.log('added'))
}

document.addEventListener('DOMContentLoaded', main)
