import {
  BLACK, WHITE, createInitialBoard, legalMoves, applyMove, countDiscs, nextTurn, winner,
} from './board.js';
import { chooseMove } from './ai.js';
import { buildBoardDom, renderBoard, setHud, showOverlay, hideOverlay } from './ui.js';

const boardEl = document.getElementById('board');
const cells = buildBoardDom(boardEl);

let board = createInitialBoard();
let turn = BLACK;
let busy = false;
let lastMove = null;
let gameOver = false;

const refresh = () => {
  const legal = gameOver || turn !== BLACK || busy ? [] : legalMoves(board, BLACK);
  renderBoard(cells, board, legal, lastMove);
  const { black, white } = countDiscs(board);
  let turnText = 'Game over';
  if (!gameOver) {
    if (busy && turn === WHITE) turnText = 'AI thinking…';
    else if (turn === BLACK) turnText = 'Your turn';
    else turnText = "White's turn";
  }
  setHud({
    black, white, turnText,
    blackActive: !gameOver && turn === BLACK,
    whiteActive: !gameOver && turn === WHITE,
  });
};

const endIfNeeded = () => {
  if (!gameOver) return;
  const { black, white } = countDiscs(board);
  const w = winner(board);
  let title = 'Draw';
  if (w === BLACK) title = 'You win!';
  else if (w === WHITE) title = 'AI wins';
  showOverlay(title, `Black ${black} · White ${white}`);
};

const afterMove = (playerWhoMoved) => {
  const n = nextTurn(board, playerWhoMoved);
  if (n.gameOver) {
    gameOver = true; turn = null; refresh(); endIfNeeded(); return;
  }
  turn = n.turn;
  refresh();
  if (!gameOver && turn === WHITE) window.setTimeout(aiPlay, 320);
};

const place = (r, c, player) => {
  const res = applyMove(board, r, c, player);
  if (!res) return false;
  board = res.board; lastMove = [r, c]; return true;
};

const aiPlay = () => {
  if (gameOver || turn !== WHITE) return;
  busy = true; refresh();
  const move = chooseMove(board, WHITE);
  busy = false;
  if (!move) {
    if (legalMoves(board, BLACK).length) { turn = BLACK; refresh(); return; }
    gameOver = true; turn = null; refresh(); endIfNeeded(); return;
  }
  place(move[0], move[1], WHITE);
  afterMove(WHITE);
};

const onCellClick = (r, c) => {
  if (gameOver || busy || turn !== BLACK) return;
  if (!place(r, c, BLACK)) return;
  afterMove(BLACK);
};

for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++)
  cells[r][c].addEventListener('click', () => onCellClick(r, c));

const newGame = () => {
  board = createInitialBoard(); turn = BLACK; busy = false; lastMove = null; gameOver = false;
  hideOverlay(); refresh();
};

document.getElementById('new-game-btn').addEventListener('click', newGame);
document.getElementById('overlay-btn').addEventListener('click', newGame);
window.addEventListener('keydown', (e) => {
  if (e.key === 'r' || e.key === 'R') { e.preventDefault(); newGame(); }
});

refresh();
