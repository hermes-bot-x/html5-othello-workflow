import { EMPTY, BLACK, WHITE } from './board.js';

export const buildBoardDom = (root) => {
  root.innerHTML = '';
  const cells = [];
  for (let r = 0; r < 8; r++) {
    const row = [];
    for (let c = 0; c < 8; c++) {
      const cell = document.createElement('button');
      cell.type = 'button';
      cell.className = 'cell';
      cell.dataset.r = String(r);
      cell.dataset.c = String(c);
      cell.setAttribute('aria-label', `Row ${r + 1} column ${c + 1}`);
      const hint = document.createElement('span');
      hint.className = 'hint';
      hint.setAttribute('aria-hidden', 'true');
      cell.appendChild(hint);
      root.appendChild(cell);
      row.push(cell);
    }
    cells.push(row);
  }
  return cells;
};

export const renderBoard = (cells, board, legal, lastMove) => {
  const set = new Set(legal.map(([r, c]) => `${r},${c}`));
  for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) {
    const el = cells[r][c];
    el.classList.toggle('legal', set.has(`${r},${c}`));
    el.classList.toggle('last', !!(lastMove && lastMove[0] === r && lastMove[1] === c));
    const v = board[r][c];
    let disc = el.querySelector('.disc');
    if (v === EMPTY) { if (disc) disc.remove(); continue; }
    const color = v === BLACK ? 'black' : 'white';
    if (!disc) {
      disc = document.createElement('span');
      disc.className = `disc ${color} place`;
      el.appendChild(disc);
    } else if (!disc.classList.contains(color)) {
      disc.classList.remove('black', 'white', 'place');
      disc.classList.add(color);
    }
  }
};

export const setHud = ({ black, white, turnText, blackActive, whiteActive }) => {
  document.getElementById('score-black-value').textContent = String(black);
  document.getElementById('score-white-value').textContent = String(white);
  document.getElementById('turn-indicator').textContent = turnText;
  document.getElementById('score-black').classList.toggle('active', blackActive);
  document.getElementById('score-white').classList.toggle('active', whiteActive);
};

export const showOverlay = (title, text) => {
  document.getElementById('overlay-title').textContent = title;
  document.getElementById('overlay-text').textContent = text;
  document.getElementById('overlay').classList.remove('hidden');
};

export const hideOverlay = () => document.getElementById('overlay').classList.add('hidden');
