let FIELDSETS = []


async function fetchPaperData(paper_id) {
    const url = new URL(
      '/finances/paper/',
      window.location.protocol + '//' + window.location.host
    )
    url.search = new URLSearchParams({paper_id: paper_id})
    const res = await fetch(url)
    return await res.json()
}


// TODO if 'volunteer field is check set price to 0
class Fieldset {
    constructor(node) {
        this.node = node
        this.paperField = this.node.querySelector('.field-paper select')
        this.priceField = this.node.querySelector('.field-price input')
        this.currentPaperPrice = undefined
        this.totalPrice = this.priceField.value
        this.priceLabel = undefined

        this.getCurrentPaperId = this.getCurrentPaperId.bind(this)
        this.initEventListeners = this.initEventListeners.bind(this)
        this.onPaperChange = this.onPaperChange.bind(this)
        this.onPriceChange = this.onPriceChange.bind(this)
        this.updatePriceLabel = this.updatePriceLabel.bind(this)

        this.initEventListeners()
    }

    initEventListeners() {
        this.paperField.addEventListener('change', this.onPaperChange)
        this.priceField.addEventListener('change', this.onPriceChange)
    }

    getCurrentPaperId() {
        return this.paperField.value
    }

    onPaperChange() {
        let currentPaperId = this.getCurrentPaperId()
        if (!currentPaperId) {
            this.currentPaperPrice = undefined
            this.updatePriceLabel()
            return
        }
        fetchPaperData(currentPaperId).then(
            res => {
                const paperData = res
                this.currentPaperPrice = paperData.price
                this.priceField.value = this.currentPaperPrice
                this.totalPrice = this.currentPaperPrice
                this.updatePriceLabel()
            }
        )
    }

    updatePriceLabel() {
        if (!this.priceLabel) {
            this.priceLabel = document.createElement('span')
            this.priceField.parentNode.appendChild(this.priceLabel)
        }
        let labelInnerHtml = ''
        if (this.currentPaperPrice) {
            const priceDiff = this.totalPrice - this.currentPaperPrice
            labelInnerHtml =`${this.currentPaperPrice} грн + ${priceDiff} пожертви`
        }
        this.priceLabel.innerHTML = labelInnerHtml
    }

    onPriceChange() {
        this.totalPrice = parseInt(this.priceField.value)
        if (this.currentPaperPrice && this.currentPaperPrice > this.totalPrice) {
            this.totalPrice = this.currentPaperPrice
            this.priceField.value = this.totalPrice
        }
        this.updatePriceLabel()
    }
}

function initAddPaperFieldsets() {
    const fieldsetNodes = document.querySelectorAll('.add-participant-paper')
    fieldsetNodes.forEach(
        node => FIELDSETS.push(new Fieldset(node))
    )
}

document.addEventListener('DOMContentLoaded', initAddPaperFieldsets)