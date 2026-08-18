export const EMPTY = 0, BLACK = 1, WHITE = 2, SIZE = 8;
const DIRS = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];

export const opponent = (p) => (p === BLACK ? WHITE : BLACK);
export const inBounds = (r, c) => r >= 0 && r < SIZE && c >= 0 && c < SIZE;

export const createInitialBoard = () => {
  const b = Array.from({ length: SIZE }, () => Array(SIZE).fill(EMPTY));
  b[3][3] = WHITE; b[3][4] = BLACK; b[4][3] = BLACK; b[4][4] = WHITE;
  return b;
};

export const cloneBoard = (board) => board.map((row) => row.slice());

export const flipsAt = (board, r, c, player) => {
  if (!inBounds(r, c) || board[r][c] !== EMPTY) return [];
  const opp = opponent(player);
  const flips = [];
  for (const [dr, dc] of DIRS) {
    const path = [];
    let rr = r + dr, cc = c + dc;
    while (inBounds(rr, cc) && board[rr][cc] === opp) {
      path.push([rr, cc]); rr += dr; cc += dc;
    }
    if (path.length && inBounds(rr, cc) && board[rr][cc] === player) flips.push(...path);
  }
  return flips;
};

export const isLegal = (board, r, c, player) => flipsAt(board, r, c, player).length > 0;

export const legalMoves = (board, player) => {
  const m = [];
  for (let r = 0; r < SIZE; r++) for (let c = 0; c < SIZE; c++)
    if (isLegal(board, r, c, player)) m.push([r, c]);
  return m;
};

export const applyMove = (board, r, c, player) => {
  const flips = flipsAt(board, r, c, player);
  if (!flips.length) return null;
  const next = cloneBoard(board);
  next[r][c] = player;
  for (const [fr, fc] of flips) next[fr][fc] = player;
  return { board: next, flips };
};

export const countDiscs = (board) => {
  let black = 0, white = 0;
  for (const row of board) for (const cell of row) {
    if (cell === BLACK) black++; else if (cell === WHITE) white++;
  }
  return { black, white };
};

export const nextTurn = (board, player) => {
  const opp = opponent(player);
  if (legalMoves(board, opp).length) return { turn: opp, passed: false, gameOver: false };
  if (legalMoves(board, player).length) return { turn: player, passed: true, gameOver: false };
  return { turn: null, passed: true, gameOver: true };
};

export const winner = (board) => {
  const { black, white } = countDiscs(board);
  if (black > white) return BLACK;
  if (white > black) return WHITE;
  return EMPTY;
};
