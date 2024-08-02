let selectedCell = null;
let fromPosition = null;

function selectCell(row, col, cellElement) {
    if (selectedCell) {
        selectedCell.classList.remove('selected');
    }

    if (fromPosition) {
        // Questo è il secondo clic, invia la mossa
        const toPosition = { row, col };
        makeMove(fromPosition, toPosition);
        fromPosition = null;
    } else {
        // Questo è il primo clic, memorizza la posizione
        fromPosition = { row, col };
        selectedCell = cellElement;
        cellElement.classList.add('selected');
    }
}

function makeMove(from, to) {
    const data = {
        rp: from.row,
        cp: from.col,
        rm: to.row,
        cm: to.col
    };

    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('message').innerText = data.message;
        if (data.status === 'ok') {
            // Esegui la mossa dell'IA dopo la mossa del giocatore
            aiMove();
        }
        if (data.status === 'finished') {
            location.reload();
        }
    });
}

function aiMove() {
    fetch('/ai_move', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('message').innerText = data.message;
        if (data.status === 'ok' || data.status === 'finished') {
            location.reload();
        }
    });
}
