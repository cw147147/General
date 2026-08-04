# Tetris

A simple browser Tetris game with score, level, and a persisted high score.

## Play

Open `tetris/index.html` in a browser, or serve the folder:

```bash
cd tetris
python3 -m http.server 8080
```

Then visit http://localhost:8080

## Controls

| Key | Action |
| --- | --- |
| ← → | Move |
| ↑ | Rotate |
| ↓ | Soft drop |
| Space | Hard drop |
| P | Pause |

High score is stored in the browser via `localStorage`.
