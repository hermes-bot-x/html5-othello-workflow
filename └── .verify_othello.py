
## Game Rules

Implement standard Othello/Reversi rules on an 8x8 board.

### Board

- The board is 8 columns by 8 rows.
- Coordinates may be represented internally as zero-based row/column indexes.
- Initial board setup:
  - White at row 3, col 3
  - White at row 4, col 4
  - Black at row 3, col 4
  - Black at row 4, col 3

### Players

- Black moves first.
- Human is always Black.
- AI is always White.

### Legal Moves

A move is legal if:

- The target square is empty.
- In at least one of the 8 directions, the placed disc brackets one or more opponent discs between the new disc and another disc of the current player.

Directions:

- North
- North-east
- East
- South-east
- South
- South-west
- West
- North-west

### Move Application

When a legal move is played:

- Place the current player's disc.
- Flip all opponent discs captured in every valid direction.
- Switch turns unless the opponent has no legal moves.
- If the opponent has no legal moves but the current player still has legal moves, the opponent's turn is skipped.
- If neither player has legal moves, the game ends.

### Game End

The game ends when:

- The board is full, or
- Neither Black nor White has any legal move.

Winner:

- Black wins if Black has more discs.
- White wins if White has more discs.
- Otherwise the game is a draw.

## User Experience Requirements

### Human Interaction

- Human clicks a legal square to place a Black disc.
- Clicking an illegal square should not change the game state.
- During AI turn, human clicks should be ignored.
- After the human move, the AI should respond automatically after a short delay.

### Legal-Move Hints

- Show hints for the current human player's legal moves.
- Hints should only appear for Black's turn.
- Hints should not appear during White AI turn.
- Hints should be visually subtle but clear.

### Score Display

Show live counts for:

- Black discs
- White discs

### Turn Display

Show the current state clearly:

- Black to move
- White thinking
- Black has no legal moves, turn skipped
- White has no legal moves, turn skipped
- Game over with winner/draw message

### Restart

Provide a restart button that:

- Resets the board to the standard initial position.
- Sets Black as the current player.
- Clears game-over state.
- Re-renders the board and UI.

## Visual Design

### Theme

Use a polished dark UI.

Suggested style direction:

- Dark page background
- Centered game container
- Green Othello board
- Rounded board cells
- Black and white discs with subtle shadows
- Soft hover states
- Clear status panels
- Accessible contrast
- Responsive layout for desktop and mobile

### Layout

Suggested page sections:

- Title/header
- Status panel:
  - Black score
  - White score
  - Current turn/status
  - Restart button
- Board area
- Small footer/help text explaining:
  - "You are Black"
  - "Legal moves are highlighted"

### Responsiveness

- Board should scale to fit narrow screens.
- Maintain square board cells.
- Avoid horizontal scrolling on mobile.

## JavaScript Architecture

Use ES modules with clear separation of concerns.

### `js/board.js`

Responsible for pure game rules and board state utilities.

Exports should include functions/constants such as:

- `BOARD_SIZE`
- `EMPTY`
- `BLACK`
- `WHITE`
- `createInitialBoard()`
- `cloneBoard(board)`
- `getOpponent(player)`
- `isOnBoard(row, col)`
- `getFlipsForMove(board, row, col, player)`
- `isLegalMove(board, row, col, player)`
- `getLegalMoves(board, player)`
- `applyMove(board, row, col, player)`
- `countDiscs(board)`
- `isBoardFull(board)`
- `getGameStatus(board, currentPlayer)`

Notes:

- Keep this module pure.
- Do not access the DOM.
- Do not mutate inputs unless explicitly documented.
- Prefer returning new board states from `applyMove`.

### `js/ai.js`

Responsible for choosing White's move.

Exports should include:

- `chooseAiMove(board, player)`

Initial AI strategy may be simple but should be reasonable.

Acceptable approaches:

1. Greedy:
   - Evaluate all legal moves.
   - Choose the move that flips the most discs.
   - Add positional weighting for corners/edges if desired.

2. Shallow search:
   - Evaluate each candidate move.
   - Apply the move.
   - Penalize moves that give Black strong responses.
   - Prefer corners and stable-looking edges.

Recommended simple scoring:

- Corners: very high bonus
- Edges: moderate bonus
- Squares adjacent to empty corners: penalty
- Disc flips: small positive value

Tie-breaking:

- Deterministic tie-breaking is acceptable.
- Random tie-breaking among equal top moves is also acceptable.

### `js/ui.js`

Responsible for DOM rendering and DOM event binding helpers.

Exports should include functions such as:

- `createBoardElement(container, onCellClick)`
- `renderBoard(container, board, options)`
- `renderScores(scoreElements, counts)`
- `renderStatus(statusElement, statusText)`
- `setRestartHandler(button, handler)`

UI responsibilities:

- Render 64 board cells.
- Render discs.
- Render legal hints.
- Apply CSS classes for:
  - Empty cells
  - Black discs
  - White discs
  - Legal hints
  - Disabled/AI turn state

Notes:

- Keep game state orchestration out of this file where practical.
- UI functions may read/write DOM but should not implement rules.

### `js/main.js`

Responsible for application state and orchestration.

Responsibilities:

- Initialize board state.
- Track current player.
- Track whether AI is thinking.
- Render the UI.
- Handle human clicks.
- Call rule functions from `board.js`.
- Call AI function from `ai.js`.
- Manage pass-turn logic.
- Detect game over.
- Restart the game.

Suggested state:

