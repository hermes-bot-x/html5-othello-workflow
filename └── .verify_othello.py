#!/usr/bin/env python3
"""Verify the static HTML5 Othello/Reversi project.

This script is intentionally dependency-free. It performs static checks for the
planned GitHub Pages app, optionally runs pure JavaScript rule tests through
Node.js when available, and verifies that the project can be served by Python's
built-in HTTP server.
"""

from __future__ import annotations

import contextlib
import http.client
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    Path("index.html"),
    Path("css/style.css"),
    Path("js/board.js"),
    Path("js/ai.js"),
    Path("js/ui.js"),
    Path("js/main.js"),
]

SOURCE_FILES = [
    Path("index.html"),
    Path("css/style.css"),
    Path("js/board.js"),
    Path("js/ai.js"),
    Path("js/ui.js"),
    Path("js/main.js"),
]

DISALLOWED_EXTERNAL_MARKERS = [
    "https://",
    "http://",
    "unpkg",
    "jsdelivr",
    "cdnjs",
]

BOARD_EXPORTS = [
    "BOARD_SIZE",
    "EMPTY",
    "BLACK",
    "WHITE",
    "createInitialBoard",
    "cloneBoard",
    "getOpponent",
    "isOnBoard",
    "getFlipsForMove",
    "isLegalMove",
    "getLegalMoves",
    "applyMove",
    "countDiscs",
    "isBoardFull",
    "getGameStatus",
]


class VerificationError(Exception):
    """Raised when a verification check fails."""


def read_text(path: Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def pass_check(name: str) -> None:
    print(f"[PASS] {name}")


def skip_check(name: str, reason: str) -> None:
    print(f"[SKIP] {name}: {reason}")


def fail_check(name: str, error: Exception) -> None:
    print(f"[FAIL] {name}")
    print(f"       {error}")


def check_required_files() -> None:
    missing = [str(path) for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        raise VerificationError("Missing required files: " + ", ".join(missing))


def check_no_external_dependencies() -> None:
    existing_sources = [path for path in SOURCE_FILES if (ROOT / path).is_file()]
    if not existing_sources:
        raise VerificationError("No source files found to inspect.")

    offenders: list[str] = []
    for path in existing_sources:
        text = read_text(path).lower()
        for marker in DISALLOWED_EXTERNAL_MARKERS:
            if marker in text:
                offenders.append(f"{path}: contains {marker!r}")

    if offenders:
        raise VerificationError("; ".join(offenders))


def check_html_structure() -> None:
    html_path = ROOT / "index.html"
    if not html_path.is_file():
        raise VerificationError("index.html is missing.")

    html = html_path.read_text(encoding="utf-8").lower()
    required_markers = {
        "board container": "board",
        "black score": "black",
        "white score": "white",
        "status or turn element": "status",
        "restart button": "restart",
        "stylesheet link": "./css/style.css",
        "module script": 'type="module"',
        "main module": "./js/main.js",
    }

    missing = [
        description
        for description, marker in required_markers.items()
        if marker not in html
    ]

    if missing:
        raise VerificationError("Missing expected HTML markers: " + ", ".join(missing))


def check_module_references() -> None:
    main_path = ROOT / "js/main.js"
    ai_path = ROOT / "js/ai.js"

    if not main_path.is_file():
        raise VerificationError("js/main.js is missing.")
    if not ai_path.is_file():
        raise VerificationError("js/ai.js is missing.")

    main = main_path.read_text(encoding="utf-8")
    ai = ai_path.read_text(encoding="utf-8")

    expected_main_imports = ["./board.js", "./ai.js", "./ui.js"]
    missing_main_imports = [
        module_path for module_path in expected_main_imports if module_path not in main
    ]

    if missing_main_imports:
        raise VerificationError(
            "js/main.js is missing imports for: " + ", ".join(missing_main_imports)
        )

    if "chooseAiMove" in ai and "./board.js" not in ai:
        raise VerificationError(
            "js/ai.js appears to implement AI logic but does not import ./board.js."
        )

    combined = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in [Path("js/main.js"), Path("js/ai.js"), Path("js/ui.js")]
        if (ROOT / path).is_file()
    ).lower()

    for marker in DISALLOWED_EXTERNAL_MARKERS:
        if marker in combined:
            raise VerificationError(f"Module source contains external marker {marker!r}.")


def check_static_rule_exports() -> None:
    board_path = ROOT / "js/board.js"
    if not board_path.is_file():
        raise VerificationError("js/board.js is missing.")

    source = board_path.read_text(encoding="utf-8")
    missing = [name for name in BOARD_EXPORTS if name not in source]
    if missing:
        raise VerificationError(
            "js/board.js is missing expected rule exports: " + ", ".join(missing)
        )


def run_node_rule_tests() -> bool:
    node = shutil.which("node")
    if not node:
        skip_check("pure rules dynamic tests", "node not found")
        return False

    test_source = textwrap.dedent(
        """
        import assert from 'node:assert/strict';
        import {
          BLACK,
          WHITE,
          EMPTY,
          createInitialBoard,
          getLegalMoves,
          getFlipsForMove,
          isLegalMove,
          applyMove,
          countDiscs,
          getGameStatus
        } from './js/board.js';

        const board = createInitialBoard();
        const initialCounts = countDiscs(board);
        assert.equal(initialCounts.black, 2, 'initial black count');
        assert.equal(initialCounts.white, 2, 'initial white count');

        assert.equal(getLegalMoves(board, BLACK).length, 4, 'initial black legal moves');
        assert.equal(getLegalMoves(board, WHITE).length, 4, 'initial white legal moves');

        assert.equal(isLegalMove(board, 2, 3, BLACK), true, 'known opening move legal');
        assert.equal(isLegalMove(board, 0, 0, BLACK), false, 'known illegal move rejected');

        const flips = getFlipsForMove(board, 2, 3, BLACK);
        assert.equal(flips.length, 1, 'known opening move flips one disc');

        const afterMove = applyMove(board, 2, 3, BLACK);
        const afterCounts = countDiscs(afterMove);
        assert.equal(afterCounts.black, 4, 'black count after opening move');
        assert.equal(afterCounts.white, 1, 'white count after opening move');
        assert.equal(board[2][3], EMPTY, 'applyMove does not mutate original board');

        const multiDirectionBoard = [
          [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
          [EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, EMPTY],
          [EMPTY, EMPTY, WHITE, WHITE, WHITE, EMPTY, EMPTY, EMPTY],
          [EMPTY, BLACK, WHITE, EMPTY, WHITE, BLACK, EMPTY, EMPTY],
          [EMPTY, EMPTY, WHITE, WHITE, WHITE, EMPTY, EMPTY, EMPTY],
          [EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, EMPTY],
          [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
          [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        ];

        const multiFlips = getFlipsForMove(multiDirectionBoard, 3, 3, BLACK);
        assert.equal(multiFlips.length, 8, 'multi-direction capture');

        const cornerBoard = [
          [EMPTY, WHITE, BLACK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
          [WHITE, WHITE, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
          [BLACK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
          [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
          [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
          [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
          [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
          [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        ];

        assert.equal(isLegalMove(cornerBoard, 0, 0, BLACK), true, 'corner capture legal');
        assert.equal(getFlipsForMove(cornerBoard, 0, 0, BLACK).length, 3, 'corner captures');

        const status = getGameStatus(board, BLACK);
        assert.equal(typeof status, 'object', 'game status returns object');

        console.log('Node rule tests passed.');
        """
    ).strip()

    with tempfile.NamedTemporaryFile(
        "w",
        suffix=".mjs",
        dir=ROOT,
        encoding="utf-8",
        delete=False,
    ) as temp_file:
        temp_file.write(test_source)
        temp_path = Path(temp_file.name)

    try:
        subprocess.run(
            [node, str(temp_path)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    finally:
        with contextlib.suppress(OSError):
            temp_path.unlink()

    return True


def check_pure_rules() -> None:
    check_static_rule_exports()
    run_node_rule_tests()


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def check_local_http_startup() -> None:
    if not (ROOT / "index.html").is_file():
        raise VerificationError("index.html is missing.")

    port = find_free_port()
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        last_error: Exception | None = None

        for _ in range(30):
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=1)
                raise VerificationError(
                    "HTTP server exited early. "
                    f"stdout={stdout.strip()!r} stderr={stderr.strip()!r}"
                )

            try:
                connection = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
                connection.request("GET", "/index.html")
                response = connection.getresponse()
                body = response.read().decode("utf-8", errors="replace")
                connection.close()

                if response.status != 200:
                    raise VerificationError(f"Expected HTTP 200, got {response.status}.")
                if "othello" not in body.lower() and "reversi" not in body.lower():
                    raise VerificationError(
                        "index.html served, but expected Othello/Reversi marker missing."
                    )
                return
            except (ConnectionError, OSError, VerificationError) as error:
                last_error = error
                time.sleep(0.1)

        if last_error is None:
            raise VerificationError("HTTP server did not respond.")
        raise VerificationError(f"HTTP server did not become ready: {last_error}")
    finally:
        process.terminate()
        with contextlib.suppress(subprocess.TimeoutExpired):
            process.wait(timeout=3)
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)


def run_check(name: str, check: Callable[[], None]) -> bool:
    try:
        check()
    except Exception as error:
        fail_check(name, error)
        return False

    pass_check(name)
    return True


def main() -> int:
    checks: list[tuple[str, Callable[[], None]]] = [
        ("required files", check_required_files),
        ("no external dependencies", check_no_external_dependencies),
        ("html structure", check_html_structure),
        ("module references", check_module_references),
        ("pure rules", check_pure_rules),
        ("local HTTP startup", check_local_http_startup),
    ]

    all_passed = True
    for name, check in checks:
        all_passed = run_check(name, check) and all_passed

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
