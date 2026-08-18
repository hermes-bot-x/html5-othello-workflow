# HTML5 Othello

You play **Black** vs a simple positional **AI (White)**.

## Controls
- Click highlighted cells to move
- **New game** or **R** to restart

## Workflow used
- Plan: Aider + GPT-5.5 (ChatGPT via Codex proxy :8650)
- Act: Aider + GLM 5.2 (with Lead cleanup after bad edit paths)
- Stack on **coder** profile env

## Verify
```bash
python3 .verify_othello.py
```
