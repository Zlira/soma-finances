function fillReport(svgId, data, scaleSize) {
    const svg = document.getElementById(svgId);
    const { height, width } = svg.getBoundingClientRect();
    const dataLength = Object.keys(data).length - 1;
    const svgNs = "http://www.w3.org/2000/svg";

    delete data['total'];
    data = Object.entries(data);
    data.sort((first, second) => first[1].total < second[1].total);

    let textCont, text, y, bar, counter = 0;
    const sectionHeight = height / dataLength;
    const barHeight = 30;
    for (let [sectionName, sectionReport] of data) {
        if (sectionName === 'total') {continue;}
        y = sectionHeight * (counter + .5);
        textCont = document.createElementNS(svgNs, 'text');
        textCont.setAttribute('x', '10');
        textCont.setAttribute('y', y);
        textCont.setAttribute('dominant-baseline', 'middle');
        text = document.createTextNode(sectionName);
        textCont.appendChild(text);

        bar = document.createElementNS(svgNs, 'rect');
        bar.setAttribute('x', 20);
        bar.setAttribute('y', y - barHeight/2);
        bar.setAttribute('height', barHeight)
        bar.setAttribute('width', (width - 20 * 2) / scaleSize * sectionReport.total);

        svg.appendChild(textCont);
        svg.appendChild(bar);
        counter ++;
    }
}

function getScaleSize(data) {
    const earnings = data.earnings;
    delete earnings['total'];
    const maxEarnings = Math.max(...Object.values(earnings).map(e => e.total));
    const expenses = data.expenses;
    delete expenses['total'];
    const maxExpenses = Math.max(...Object.values(expenses).map(e => e.total));
    const max = Math.max(maxExpenses, maxEarnings);
    return Math.ceil(max / 200) * 200;
}