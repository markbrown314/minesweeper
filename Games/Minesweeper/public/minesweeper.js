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
const IMG_FLAG_TILE = ASSET_PATH + "flag_tile.png"


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
  for (y = 0; y < game_context.max_y; y += 1) {
    for (x = 0; x < game_context.max_x; x += 1) {
      var tile_id = ((x + 1) * game_context.max_x) + y + 1
      var gc = game_context.game_map[tile_id.toString()]
      //console.log("x = " + x + " y = " + y + " gc = " + gc + " tid = ", tile_id)

      switch(game_context.game_map[tile_id.toString()]) {
        case "#":
          img = IMG_UNKNOWN_TILE
          break
        case ".":
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
        case "*":
          img = IMG_MINE_HIT_TILE
          break
        case "?":
          img = IMG_FLAG_TILE
          break
        }
      render_image(img, x * SQUARE_SIZE, y * SQUARE_SIZE)
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

reset_button.onclick = function() {
  max_x = game_context.max_x
  max_y = game_context.max_y
  socket.send("s (" + x + "," + y +")")
}

undo_button.onclick = function() {
  socket.send("u")
}


canvas.addEventListener('mousedown', e=> {
    //console.log("mouse down: X: " + e.offsetX + " Y: " + e.offsetY + " button: " + e.button)
    var x = tile_index(e.offsetX) + 1
    var y = tile_index(e.offsetY) + 1
    console.log("button " + e.button)
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
    canvas.width = game_context.max_x * SQUARE_SIZE
    canvas.height = game_context.max_y * SQUARE_SIZE   
  })