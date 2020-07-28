const SQUARE_SIZE = 25

const ASSET_PATH = "assets/"
const IMG_UNKNOWN_TILE = ASSET_PATH + "unknown_tile.png"
const IMG_EMPTY_TILE = ASSET_PATH + "empty_tile.png"
const IMG_ONE_TILE = ASSET_PATH + "one_tile.png"
const IMG_TWO_TILE = ASSET_PATH + "two_tile.png"
const IMG_THREE_TILE = ASSET_PATH + "three_tile.png"
const IMG_FOUR_TILE = ASSET_PATH + "four_tile.png"
const IMG_FIVE_TILE = ASSET_PATH + "five_tile.png"
const IMG_SIX_TILE = ASSET_PATH + "six_tile.png"
const IMG_SEVEN_TILE = ASSET_PATH + "seven_tile.png"
const IMG_EIGHT_TILE = ASSET_PATH + "eight_tile.png"
const IMG_MINE_HIT_TILE = ASSET_PATH + "mine_red_tile.png"
const IMG_MINE_TILE = ASSET_PATH + "mine_tile.png"
const IMG_FLAG_TILE = ASSET_PATH + "flag_tile.png"
const IMG_WRONG_TILE = ASSET_PATH + "wrong_tile.png"

const TILE_EMPTY = "."
const TILE_MINE = "*"
const TILE_FLAG = "?"
const TILE_WRONG = "X"
const TILE_HIDDEN = "#"
const TILE_MINE_HIT = "!"

document.addEventListener('contextmenu', e => e.preventDefault())
var canvas = document.getElementById('minesweeper_canvas')
var reset_button = document.getElementById('reset_button')
var undo_button = document.getElementById('undo_button')
const ctx = canvas.getContext('2d')
var game_context = null

function tile_index(coord) {
  return Math.floor(coord/SQUARE_SIZE)
}

function snap_to_grid(coord) {
  return Math.floor(coord/SQUARE_SIZE) * SQUARE_SIZE
}

function render_game_map(ctx, game_context) {
  var img = IMG_UNKNOWN_TILE
  var winning_condition = game_context["winning_condition"]
  for (y = 0; y < game_context.max_y; y += 1) {
    for (x = 0; x < game_context.max_x; x += 1) {
      var tile_id = ((x + 1) * game_context.max_x) + y + 1
      var gc = game_context.game_map[tile_id.toString()]
      
      switch(gc) {
        case TILE_HIDDEN:
          img = IMG_UNKNOWN_TILE
          break
        case TILE_EMPTY:
          img = IMG_EMPTY_TILE
          break
        case "1":
          img = IMG_ONE_TILE
          break
        case "2":
          img = IMG_TWO_TILE
          break
        case "3":
          img = IMG_THREE_TILE
          break
        case "4":
          img = IMG_FOUR_TILE
          break
        case "5":
          img = IMG_FIVE_TILE
          break
        case "6":
          img = IMG_SIX_TILE
          break
        case "7":
          img = IMG_SEVEN_TILE
          break
        case "8":
          img = IMG_EIGHT_TILE
          break
        case TILE_MINE:
          img = IMG_MINE_TILE
          break
        case TILE_MINE_HIT:
          img = IMG_MINE_HIT_TILE
          break
        case TILE_FLAG:
          img = IMG_FLAG_TILE
          break
        case TILE_WRONG:
          img = IMG_WRONG_TILE
          break
        }
      render_image(img, x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
    }  
  }
  if (winning_condition) {
    render_image("assets/winning_image.png", 50, 50, 150, 131)
  }
}
function render_image(image_src, x, y, size_x, size_y) {
  var img = new Image
  img.src = image_src
  img.onload = function() {
    ctx.drawImage(img, x, y, size_x, size_y)
  }
}

console.log("Minesweeper")

reset_button.onclick = function() {
  max_x = game_context.max_x
  max_y = game_context.max_y
  socket.send("s (" + x + "," + y +")")
}

undo_button.onclick = function() {
  socket.send("u")
}


canvas.addEventListener('mousedown', e=> {
    var x = tile_index(e.offsetX) + 1
    var y = tile_index(e.offsetY) + 1
    if (e.button == 0) {
      socket.send("! (" + x + "," + y +")")
    }
    if (e.button == 2) {
      socket.send("? (" + x + "," + y +")")
    }
  })

const socket = new WebSocket('ws://localhost:8081 ')
socket.addEventListener('message', function (event) {
    game_context = JSON.parse(event.data)
    render_game_map(ctx, game_context)
    if (canvas.width != game_context.max_x * SQUARE_SIZE ||
       canvas.height != game_context.max_y * SQUARE_SIZE) {
      canvas.width = game_context.max_x * SQUARE_SIZE
      canvas.height = game_context.max_y * SQUARE_SIZE
    }
  })
