const MAX_X = 10
const MAX_Y = 10
const SQUARE_SIZE = 25

const ASSET_PATH = "assets/"
const IMG_UNKNOWN_TILE = ASSET_PATH + "unknown_tile.png"
const IMG_EMPTY_TILE = ASSET_PATH + "empty_tile.png"

document.addEventListener('contextmenu', e => e.preventDefault())
var canvas = document.getElementById('minesweeper_canvas')
const ctx = canvas.getContext('2d')

function tile_index(coord) {
  return Math.floor(coord/SQUARE_SIZE)
}

function snap_to_grid(coord) {
  return Math.floor(coord/SQUARE_SIZE) * SQUARE_SIZE
}

function draw(ctx) {
  var gray = true
    for (y = 0; y < MAX_X * SQUARE_SIZE; y += SQUARE_SIZE) {
      for (x = 0; x < MAX_X * SQUARE_SIZE; x += SQUARE_SIZE) {
        render_image(IMG_UNKNOWN_TILE, x, y)
    }  
  }
}

function render_image(image_src, x, y) {
  var img = new Image
  img.src = image_src
  img.onload = function() {
    ctx.drawImage(img, x, y, SQUARE_SIZE, SQUARE_SIZE)
  }
}

console.log("Minesweeper")

canvas.addEventListener('mousedown', e=> {
    console.log("mouse down: X: " + e.offsetX + " Y: " + e.offsetY + " button: " + e.button)
    render_image(IMG_EMPTY_TILE, snap_to_grid(e.offsetX), snap_to_grid(e.offsetY))  
  })

draw(ctx)
canvas.width = MAX_X * SQUARE_SIZE
canvas.height = MAX_Y * SQUARE_SIZE
