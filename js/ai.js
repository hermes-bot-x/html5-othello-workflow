import { WHITE, BLACK, legalMoves, applyMove, countDiscs } from './board.js';

const CORNERS = new Set(['0,0','0,7','7,0','7,7']);
const BAD = new Set(['1,1','1,6','6,1','6,6','0,1','1,0','0,6','1,7','6,0','7,1','6,7','7,6']);

const wpos = (r, c) => {
  const k = `${r},${c}`;
  if (CORNERS.has(k)) return 100;
  if (BAD.has(k)) return -25;
  if (r === 0 || r === 7 || c === 0 || c === 7) return 10;
  return 1;
};

const evalBoard = (board) => {
  const { black, white } = countDiscs(board);
  let pos = 0;
  for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) {
    if (board[r][c] === WHITE) pos += wpos(r, c);
    else if (board[r][c] === BLACK) pos -= wpos(r, c);
  }
  const mob = legalMoves(board, WHITE).length - legalMoves(board, BLACK).length;
  return (white - black) * 3 + pos + mob * 2;
};

export const chooseMove = (board, player = WHITE) => {
  const moves = legalMoves(board, player);
  if (!moves.length) return null;
  let best = null, bestScore = -Infinity;
  for (const [r, c] of moves) {
    const res = applyMove(board, r, c, player);
    if (!res) continue;
    let s = evalBoard(res.board);
    if (player === BLACK) s = -s;
    s += Math.random() * 0.4;
    if (s > bestScore) { bestScore = s; best = [r, c]; }
  }
  return best;
};
