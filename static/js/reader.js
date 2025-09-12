// reader.js
let pdfDoc = null,
    pageNum = START_PAGE,
    pageCount = 0,
    canvas = document.getElementById('pdfRender'),
    ctx = canvas.getContext('2d');

const scale = 1.2;  // escala de exibição

function renderPage(num) {
    pdfDoc.getPage(num).then(function(page) {
        const viewport = page.getViewport({ scale: scale });
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderCtx = {
            canvasContext: ctx,
            viewport: viewport
        };

        page.render(renderCtx).promise.then(function () {
            document.getElementById('pageNum').textContent = num;
            document.getElementById('pageCount').textContent = pageCount;

            // Salva progresso após renderizar a página
            saveProgress(num);
        });
    });
}

function queueRenderPage(num) {
    if (num < 1 || num > pageCount) {
        return;
    }
    pageNum = num;
    renderPage(pageNum);
}

function onPrevPage() {
    if (pageNum <= 1) {
        return;
    }
    pageNum--;
    renderPage(pageNum);
}

function onNextPage() {
    if (pageNum >= pageCount) {
        return;
    }
    pageNum++;
    renderPage(pageNum);
}

function saveProgress(page) {
    fetch('/save_progress', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            pdf_name: PDF_NAME,
            page: page
        })
    }).then(response => {
        // opcional: tratar resposta
        return response.json();
    }).then(json => {
        if (json.status !== "ok") {
            console.error("Erro ao salvar progresso:", json);
        }
    }).catch(err => {
        console.error("Erro de rede:", err);
    });
}

document.getElementById('prevPage').addEventListener('click', onPrevPage);
document.getElementById('nextPage').addEventListener('click', onNextPage);


// Carrega o PDF com PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = "{{ url_for('static', filename='pdfjs/pdf.worker.js') }}";

const url = `/static/pdfs/${PDF_NAME}`;

pdfjsLib.getDocument(url).promise.then(function(pdf) {
    pdfDoc = pdf;
    pageCount = pdf.numPages;
    document.getElementById('pageCount').textContent = pageCount;
    // renderiza a página inicial
    renderPage(pageNum);
});
