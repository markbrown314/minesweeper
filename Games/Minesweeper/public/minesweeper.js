/* Minesweeper WebSocket Client */
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

const DIFFICULTY_BEGINNER = "0"
const DIFFICULTY_MODERATE = "1"
const DIFFICULTY_EXPERT = "2"


function time_format(input) {
  if (input < 10) {
    return "0" + input
  }
  else return input
}
function game_timer() {
  if (!game_running) {
    return
  }
  var game_cur_time = Date.now()
  var time_diff = game_cur_time - game_base_time
  var total_seconds = Math.floor(time_diff/1000)
  var seconds = total_seconds % 60
  var minutes = Math.floor(total_seconds/60) % 60
  var hours = Math.floor(total_seconds/3600) % 60
  game_time_label.textContent = time_format(hours) + ":" + time_format(minutes) + ":" + time_format(seconds)
}

document.addEventListener('contextmenu', e => e.preventDefault())
var canvas = document.getElementById('minesweeper_canvas')
var reset_button = document.getElementById('reset_button')
var undo_button = document.getElementById('undo_button')
var config_button = document.getElementById('config_button')
var mine_count_label = document.getElementById('mine_count')
var config_window = document.getElementById('config_window')
var close_button = document.getElementById('close_button')
const ctx = canvas.getContext('2d')
var game_context = null
var game_running = false
var game_time_label = document.getElementById('game_time')
var game_base_time = null
var max_x = document.getElementById('max_x')
var max_y = document.getElementById('max_y')
var mines = document.getElementById('mines')
var difficulty_radio = document.getElementsByName('difficulty_radio')

window.setInterval(game_timer, 1000)

function tile_index(coord) {
  return Math.floor(coord/SQUARE_SIZE)
}

function snap_to_grid(coord) {
  return Math.floor(coord/SQUARE_SIZE) * SQUARE_SIZE
}

function reset_game() {
  game_time_label.textContent = "00:00:00"
  mine_count_label.textContent = "?"
  game_base_time = Date.now()
  undo_button.disabled = false

}

/* keep track of old game map */
var old_game_map = null
function render_game_map(ctx, game_context) {
  var img = IMG_UNKNOWN_TILE
  var winning_condition = game_context["winning_condition"]
  for (y = 0; y < game_context.max_y; y += 1) {
    for (x = 0; x < game_context.max_x; x += 1) {
      var tile_id = ((x + 1) * game_context.max_x) + y + 1
      var gc = game_context.game_map[tile_id.toString()]
      if (old_game_map) {
        /* only draw changes */
        if (old_game_map[tile_id.toString()] == game_context.game_map[tile_id.toString()]) {
          continue
        }
      }
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
    game_running = false
    undo_button.disabled = true
    render_image("assets/winning_image.png", 50, 50, 150, 131)
    mine_count_label.textContent = "0"
  }

  old_game_map = {...game_context.game_map}
}
function render_image(image_src, x, y, size_x, size_y) {
  var img = new Image
  img.src = image_src
  img.onload = function() {
    ctx.drawImage(img, x, y, size_x, size_y)
  }
}

reset_button.onclick = function() {
  x = max_x.value
  y = max_y.value
  mine_count = mines.value

  game_running = false
  old_game_map = null
  reset_game()
  undo_button.disabled = true
  socket.send("s (" + x + "," + y + "," + mine_count + ")")
}

undo_button.onclick = function() {
  if (!game_running) {
    return
  }
  socket.send("u")
}


canvas.addEventListener('mousedown', e=> {
    x = tile_index(e.offsetX) + 1
    y = tile_index(e.offsetY) + 1
    if (e.button == 0) {
      socket.send("! (" + x + "," + y +")")
    }
    if (e.button == 2) {
      socket.send("? (" + x + "," + y +")")
    }
    
    if (game_running == false) {
      reset_game()
      game_running = true
      undo_button.disabled = false
    }
  })

  config_button.onclick = function() {
    config_window.style.display = "block";
  }

  close_button.onclick = function(){
    config_window.style.display = "none";    
  }

/* main */
console.log("Minesweeper")
reset_game()
undo_button.disabled = true

for (i = 0; i < difficulty_radio.length; i++) {
  difficulty_radio[i].addEventListener('click', function() {
    radio = this
    switch(radio.value) {
      case DIFFICULTY_BEGINNER:
        max_x.value = 10
        max_y.value = 10
        mines.value = 10
        break
      case DIFFICULTY_MODERATE:
        max_x.value = 16
        max_y.value = 16
        mines.value = 40
        break
      case DIFFICULTY_EXPERT:
        max_x.value = 30
        max_y.value = 16
        mines.value = 99
        break
    }
  })
}

const socket = new WebSocket('ws://localhost:8081 ')
socket.addEventListener('message', function (event) {
    game_context = JSON.parse(event.data)
    render_game_map(ctx, game_context)
    if (canvas.width != game_context.max_x * SQUARE_SIZE ||
       canvas.height != game_context.max_y * SQUARE_SIZE) {
      canvas.width = game_context.max_x * SQUARE_SIZE
      canvas.height = game_context.max_y * SQUARE_SIZE
    }
    if (game_running) {
      mine_count_label.textContent = game_context["mines"] - game_context["flags"]
    }
  })