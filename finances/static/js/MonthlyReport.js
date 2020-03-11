function fillReport(svgId, detailsId, data, scaleSize) {
    console.log(data);
    const svg = document.getElementById(svgId);
    const { height, width } = svg.getBoundingClientRect();
    const dataLength = Object.keys(data).length - 1;
    const svgNs = "http://www.w3.org/2000/svg";

    delete data['total'];
    data = Object.entries(data);
    data.sort((first, second) => first[1].total < second[1].total);

    let textCont, text, group, y, bar, setDetials, counter = 0;
    const sectionHeight = height / dataLength;
    const barHeight = 30;
    const leftMargin = 150;
    const rightMargin = 20;
    for (let [sectionName, sectionReport] of data) {
        if (sectionName === 'total') {continue;}
        y = sectionHeight * (counter + .5);
        textCont = document.createElementNS(svgNs, 'text');
        textCont.setAttribute('text-anchor', 'end');
        textCont.setAttribute('x', leftMargin - 5);
        textCont.setAttribute('y', y);
        textCont.setAttribute('dominant-baseline', 'middle');
        textCont.setAttribute('fill', 'black');
        text = document.createTextNode(`${sectionName} ${sectionReport.total} грн`);
        textCont.appendChild(text);

        bar = document.createElementNS(svgNs, 'rect');
        bar.setAttribute('x', leftMargin);
        bar.setAttribute('y', y - barHeight/2);
        bar.setAttribute('height', barHeight);
        bar.setAttribute(
            'width',
            (width - leftMargin - rightMargin) / scaleSize * sectionReport.total
        );

        group = document.createElementNS(svgNs, 'g');
        // group.setAttribute('onclick', "console.log('hi')");
        group.setAttribute("style", "pointer-events: bounding-box;");
        group.appendChild(textCont);
        group.appendChild(bar);

        svg.appendChild(group);
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