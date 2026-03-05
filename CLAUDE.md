# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dev dependencies (activate venv first)
pip install -e ".[dev]"

# Run all tests
pytest -q

# Run a single test file
pytest tests/test_board_init.py -q

# Run a single test by name
pytest tests/test_castling.py::test_kingside_castling -q

# Lint
ruff check .

# Type check
mypy src
```

The project uses a `.venv` at the repo root. On Windows/PowerShell: `.\.venv\Scripts\Activate.ps1`.

## Running the App

```bash
# CLI (UCI-style input)
python -m portfolio_chess

# Tkinter GUI
python -m portfolio_chess.ui_tk
```

## Architecture

The codebase is a rules-first chess engine with no external dependencies (stdlib only). Source lives under `src/portfolio_chess/` with a `core/` layer and thin UI layers on top.

### Layer structure

```
core/types.py     - Color, PieceType, Piece, CastlingRights, square_to_index/index_to_square
core/move.py      - Move dataclass (from_sq, to_sq, promotion); Move.from_uci()
core/board.py     - Board dataclass: pieces dict[int, Piece], FEN I/O, apply_move, position_key
core/rules.py     - Rules: legal_moves, is_legal, is_checkmate, is_stalemate, is_insufficient_material
core/notation.py  - SAN generation, PGN formatting
core/game.py      - Game: orchestrates Board + Rules, tracks history, handles draw/resign/terminal state
cli.py            - CLI REPL using Game
ui_tk.py          - Standalone Tkinter entrypoint
ui/app.py         - Tkinter BoardApp widget
```

### Key design details

- **Board representation**: 64-square flat dict `pieces: dict[int, Piece]` where index = `rank * 8 + file` (a1=0, h1=7, a8=56, h8=63).
- **Move generation**: `Rules._pseudo_legal_moves()` generates candidate moves per piece type; then `_is_king_safe_after_move()` filters illegal ones. Castling checks pass-through squares for attacks.
- **Move application**: `Board.apply_move()` mutates the board in place (including en passant capture removal, castling rook teleport, promotion).
- **Draw detection**: Threefold repetition and 50-move rule are **automatically applied** (not claim-based). `Game.position_counts` tracks FEN-derived position keys.
- **FEN/SAN**: `Board.from_fen()` / `Board.to_fen()` for serialization. SAN is generated in `notation.py` before `apply_move` is called (needs the pre-move board to disambiguate).
- **Game flow**: `Game.make_move(Move)` → validates legality → generates SAN → applies move → checks terminal state.

### CI

GitHub Actions (`.github/workflows/ci.yml`): pytest is required; ruff and mypy are non-blocking (`continue-on-error: true`).
