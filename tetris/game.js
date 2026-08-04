(() => {
  const COLS = 10;
  const ROWS = 20;
  const BLOCK = 30;
  const HIGH_SCORE_KEY = "tetris-high-score";

  const COLORS = {
    I: "#5b9fd4",
    O: "#d4b45b",
    T: "#9b7fd4",
    S: "#5bd48a",
    Z: "#d45b5b",
    J: "#5b6fd4",
    L: "#d48a5b",
  };

  const SHAPES = {
    I: [
      [0, 0, 0, 0],
      [1, 1, 1, 1],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
    ],
    O: [
      [1, 1],
      [1, 1],
    ],
    T: [
      [0, 1, 0],
      [1, 1, 1],
      [0, 0, 0],
    ],
    S: [
      [0, 1, 1],
      [1, 1, 0],
      [0, 0, 0],
    ],
    Z: [
      [1, 1, 0],
      [0, 1, 1],
      [0, 0, 0],
    ],
    J: [
      [1, 0, 0],
      [1, 1, 1],
      [0, 0, 0],
    ],
    L: [
      [0, 0, 1],
      [1, 1, 1],
      [0, 0, 0],
    ],
  };

  const PIECE_TYPES = Object.keys(SHAPES);

  const boardCanvas = document.getElementById("board");
  const nextCanvas = document.getElementById("next");
  const boardCtx = boardCanvas.getContext("2d");
  const nextCtx = nextCanvas.getContext("2d");

  const scoreEl = document.getElementById("score");
  const highScoreEl = document.getElementById("high-score");
  const levelEl = document.getElementById("level");
  const linesEl = document.getElementById("lines");
  const startBtn = document.getElementById("start-btn");
  const overlay = document.getElementById("overlay");
  const overlayText = document.getElementById("overlay-text");
  const overlayBtn = document.getElementById("overlay-btn");

  let grid = createEmptyGrid();
  let current = null;
  let nextType = randomType();
  let score = 0;
  let highScore = loadHighScore();
  let lines = 0;
  let level = 1;
  let dropInterval = 1000;
  let lastDrop = 0;
  let running = false;
  let paused = false;
  let gameOver = false;
  let rafId = null;

  highScoreEl.textContent = String(highScore);

  function createEmptyGrid() {
    return Array.from({ length: ROWS }, () => Array(COLS).fill(null));
  }

  function loadHighScore() {
    const stored = localStorage.getItem(HIGH_SCORE_KEY);
    const value = Number(stored);
    return Number.isFinite(value) && value > 0 ? value : 0;
  }

  function saveHighScore(value) {
    localStorage.setItem(HIGH_SCORE_KEY, String(value));
  }

  function randomType() {
    return PIECE_TYPES[Math.floor(Math.random() * PIECE_TYPES.length)];
  }

  function rotateMatrix(matrix) {
    const size = matrix.length;
    const rotated = Array.from({ length: size }, () => Array(size).fill(0));
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        rotated[x][size - 1 - y] = matrix[y][x];
      }
    }
    return rotated;
  }

  function spawnPiece() {
    const type = nextType;
    nextType = randomType();
    const shape = SHAPES[type].map((row) => row.slice());
    const piece = {
      type,
      shape,
      x: Math.floor((COLS - shape[0].length) / 2),
      y: 0,
    };

    if (collides(piece, piece.x, piece.y, piece.shape)) {
      endGame();
      return null;
    }

    drawNext();
    return piece;
  }

  function collides(piece, offsetX, offsetY, shape) {
    for (let y = 0; y < shape.length; y++) {
      for (let x = 0; x < shape[y].length; x++) {
        if (!shape[y][x]) continue;
        const nx = offsetX + x;
        const ny = offsetY + y;
        if (nx < 0 || nx >= COLS || ny >= ROWS) return true;
        if (ny >= 0 && grid[ny][nx]) return true;
      }
    }
    return false;
  }

  function mergePiece() {
    const { shape, x, y, type } = current;
    for (let py = 0; py < shape.length; py++) {
      for (let px = 0; px < shape[py].length; px++) {
        if (!shape[py][px]) continue;
        const gy = y + py;
        const gx = x + px;
        if (gy >= 0) grid[gy][gx] = type;
      }
    }
  }

  function clearLines() {
    let cleared = 0;
    for (let y = ROWS - 1; y >= 0; y--) {
      if (grid[y].every((cell) => cell)) {
        grid.splice(y, 1);
        grid.unshift(Array(COLS).fill(null));
        cleared++;
        y++;
      }
    }

    if (cleared > 0) {
      const points = [0, 100, 300, 500, 800];
      score += points[cleared] * level;
      lines += cleared;
      level = Math.floor(lines / 10) + 1;
      dropInterval = Math.max(100, 1000 - (level - 1) * 80);
      updateStats();
    }
  }

  function updateStats() {
    scoreEl.textContent = String(score);
    levelEl.textContent = String(level);
    linesEl.textContent = String(lines);

    if (score > highScore) {
      highScore = score;
      highScoreEl.textContent = String(highScore);
      saveHighScore(highScore);
    }
  }

  function move(dx, dy) {
    if (!current || !running || paused || gameOver) return false;
    const nx = current.x + dx;
    const ny = current.y + dy;
    if (!collides(current, nx, ny, current.shape)) {
      current.x = nx;
      current.y = ny;
      return true;
    }
    return false;
  }

  function rotate() {
    if (!current || !running || paused || gameOver) return;
    const rotated = rotateMatrix(current.shape);
    const kicks = [0, -1, 1, -2, 2];
    for (const kick of kicks) {
      if (!collides(current, current.x + kick, current.y, rotated)) {
        current.shape = rotated;
        current.x += kick;
        return;
      }
    }
  }

  function hardDrop() {
    if (!current || !running || paused || gameOver) return;
    while (move(0, 1)) {
      score += 2;
    }
    lockPiece();
    updateStats();
  }

  function softDrop() {
    if (!move(0, 1)) {
      lockPiece();
    } else {
      score += 1;
      updateStats();
    }
  }

  function lockPiece() {
    mergePiece();
    clearLines();
    current = spawnPiece();
  }

  function drawCell(ctx, x, y, color, size) {
    ctx.fillStyle = color;
    ctx.fillRect(x * size, y * size, size, size);
    ctx.strokeStyle = "rgba(0, 0, 0, 0.35)";
    ctx.lineWidth = 1;
    ctx.strokeRect(x * size + 0.5, y * size + 0.5, size - 1, size - 1);
  }

  function drawBoard() {
    boardCtx.clearRect(0, 0, boardCanvas.width, boardCanvas.height);

    boardCtx.strokeStyle = "#1f2123";
    boardCtx.lineWidth = 1;
    for (let x = 0; x <= COLS; x++) {
      boardCtx.beginPath();
      boardCtx.moveTo(x * BLOCK, 0);
      boardCtx.lineTo(x * BLOCK, ROWS * BLOCK);
      boardCtx.stroke();
    }
    for (let y = 0; y <= ROWS; y++) {
      boardCtx.beginPath();
      boardCtx.moveTo(0, y * BLOCK);
      boardCtx.lineTo(COLS * BLOCK, y * BLOCK);
      boardCtx.stroke();
    }

    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS; x++) {
        const cell = grid[y][x];
        if (cell) drawCell(boardCtx, x, y, COLORS[cell], BLOCK);
      }
    }

    if (current) {
      const { shape, x, y, type } = current;
      for (let py = 0; py < shape.length; py++) {
        for (let px = 0; px < shape[py].length; px++) {
          if (shape[py][px]) {
            drawCell(boardCtx, x + px, y + py, COLORS[type], BLOCK);
          }
        }
      }
    }
  }

  function drawNext() {
    nextCtx.clearRect(0, 0, nextCanvas.width, nextCanvas.height);
    const shape = SHAPES[nextType];
    const size = 24;
    const offsetX = (nextCanvas.width / size - shape[0].length) / 2;
    const offsetY = (nextCanvas.height / size - shape.length) / 2;

    for (let y = 0; y < shape.length; y++) {
      for (let x = 0; x < shape[y].length; x++) {
        if (shape[y][x]) {
          drawCell(nextCtx, offsetX + x, offsetY + y, COLORS[nextType], size);
        }
      }
    }
  }

  function showOverlay(text, buttonLabel) {
    overlayText.textContent = text;
    overlayBtn.textContent = buttonLabel;
    overlay.classList.remove("hidden");
  }

  function hideOverlay() {
    overlay.classList.add("hidden");
  }

  function endGame() {
    gameOver = true;
    running = false;
    paused = false;
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
    startBtn.textContent = "Play Again";
    showOverlay("Game Over", "Play Again");
  }

  function resetGame() {
    grid = createEmptyGrid();
    score = 0;
    lines = 0;
    level = 1;
    dropInterval = 1000;
    lastDrop = 0;
    gameOver = false;
    paused = false;
    nextType = randomType();
    current = spawnPiece();
    updateStats();
    drawBoard();
  }

  function startGame() {
    if (rafId) cancelAnimationFrame(rafId);
    resetGame();
    if (gameOver) return;
    running = true;
    hideOverlay();
    startBtn.textContent = "Restart";
    lastDrop = performance.now();
    rafId = requestAnimationFrame(loop);
  }

  function togglePause() {
    if (!running || gameOver) return;
    paused = !paused;
    if (paused) {
      showOverlay("Paused", "Resume");
    } else {
      hideOverlay();
      lastDrop = performance.now();
      rafId = requestAnimationFrame(loop);
    }
  }

  function loop(timestamp) {
    if (!running || paused || gameOver) return;

    if (timestamp - lastDrop >= dropInterval) {
      if (!move(0, 1)) {
        lockPiece();
      }
      lastDrop = timestamp;
    }

    drawBoard();
    rafId = requestAnimationFrame(loop);
  }

  document.addEventListener("keydown", (event) => {
    const keys = ["ArrowLeft", "ArrowRight", "ArrowDown", "ArrowUp", " ", "p", "P"];
    if (keys.includes(event.key)) event.preventDefault();

    if (event.key === "p" || event.key === "P") {
      if (running && !gameOver) togglePause();
      return;
    }

    if (!running || paused || gameOver) return;

    switch (event.key) {
      case "ArrowLeft":
        move(-1, 0);
        break;
      case "ArrowRight":
        move(1, 0);
        break;
      case "ArrowDown":
        softDrop();
        break;
      case "ArrowUp":
        rotate();
        break;
      case " ":
        hardDrop();
        break;
      default:
        break;
    }

    drawBoard();
  });

  startBtn.addEventListener("click", startGame);

  overlayBtn.addEventListener("click", () => {
    if (gameOver) {
      startGame();
    } else if (paused) {
      togglePause();
    }
  });

  drawBoard();
  drawNext();
})();
