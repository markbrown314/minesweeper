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
const IMG_WINNING_IMAGE = ASSET_PATH + "winning_image.png"
const IMG_LOOSING_IMAGE = ASSET_PATH + "loosing_image.png"

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
  if (game_preload_delay) {
    canvas.setAttribute('style', 'display:block')
    mine_count_label.textContent = "Click to Start"
    window.setInterval(game_timer, 1000)
    game_preload_delay = false
  }
  
  if (!game_running) {
    return
  }
  let game_cur_time = Date.now()
  let time_diff = game_cur_time - game_base_time
  let total_seconds = Math.floor(time_diff/1000)
  let seconds = total_seconds % 60
  let minutes = Math.floor(total_seconds/60) % 60
  let hours = Math.floor(total_seconds/3600) % 60
  game_time_label.textContent = time_format(hours) + ":" + time_format(minutes) + ":" + time_format(seconds)
}

document.addEventListener('contextmenu', e => e.preventDefault())
const canvas = document.getElementById('minesweeper_canvas')
const reset_button = document.getElementById('reset_button')
const undo_button = document.getElementById('undo_button')
const config_button = document.getElementById('config_button')
const mine_count_label = document.getElementById('mine_count')
const config_window = document.getElementById('config_window')
const close_button = document.getElementById('close_button')
const ctx = canvas.getContext('2d')
canvas.setAttribute('style', 'display:none')
let game_context = null
let game_running = false
let game_preload_delay = true
let force_repaint = false
const game_time_label = document.getElementById('game_time')
let game_base_time = null
const max_x = document.getElementById('max_x')
const max_y = document.getElementById('max_y')
const mines = document.getElementById('mines')
const difficulty_radio = document.getElementsByName('difficulty_radio')
const image_cache = {}

function tile_index(coord) {
  return Math.floor(coord/SQUARE_SIZE)
}

function reset_game() {
  game_time_label.textContent = "00:00:00"
  if (game_context) mine_count_label.textContent = game_context["mines"]
  game_base_time = Date.now()
  undo_button.disabled = false

}

/* keep track of old game map */
let old_game_map = null

function render_game_map() {
  let img = IMG_UNKNOWN_TILE
  const winning_condition = game_context["winning_condition"]
  const loosing_condition = game_context["loosing_condition"]
  for (let y = 0; y < game_context.max_y; y += 1) {
    for (let x = 0; x < game_context.max_x; x += 1) {
      const tile_id = ((x + 1) * game_context.max_x) + y + 1
      const tile = game_context.game_map[tile_id.toString()]
      if (old_game_map && !force_repaint) {
        /* only draw changes */
        if (old_game_map[tile_id.toString()] == tile) continue
      }

      switch(tile) {
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

  if (force_repaint) {
    force_repaint=false
  }

  if (winning_condition) {
    game_running = false
    undo_button.disabled = true
    render_image(IMG_WINNING_IMAGE, 50, 50, 150, 131)
    mine_count_label.textContent = "You Win!"
  }

  if (loosing_condition) {
    game_running = false
    render_image(IMG_LOOSING_IMAGE, 50, 50, 150, 131)
    mine_count_label.textContent = "Game Over!"
  }


  old_game_map = {...game_context.game_map}
}
function render_image(image_src, x, y, size_x, size_y, render = true) {
  if (!(image_src in image_cache) || !render) {
    const img = new Image
    img.src = image_src
    img.onload = function() {
      const canvas = document.createElement("canvas")
      const img_ctx = canvas.getContext("2d")
      img_ctx.drawImage(img, 0, 0, size_x, size_y)
      image_cache[image_src] = img_ctx.getImageData(0, 0, size_x, size_y)
      if (render) {
        ctx.putImageData(image_cache[image_src], x, y)
      }
    }
  }
  else {
    ctx.putImageData(image_cache[image_src], x, y)
  }
}

reset_button.onclick = function() {
  let x = max_x.value
  let y = max_y.value
  let mine_count = mines.value

  game_running = false
  old_game_map = null
  reset_game()
  undo_button.disabled = true
  socket.send("s (" + x + "," + y + "," + mine_count + ")")
}

undo_button.onclick = function() {
  socket.send("u")
  force_repaint = true
  mine_count_label.textContent = game_context["mines"] - game_context["flags"]
}


canvas.addEventListener('mousedown', e=> {
    let x = tile_index(e.offsetX) + 1
    let y = tile_index(e.offsetY) + 1
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
mine_count_label.textContent = "Loading..."
undo_button.disabled = true

for (let i = 0; i < difficulty_radio.length; i++) {
  difficulty_radio[i].addEventListener('click', function() {
    let radio = this
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

const preload_image_list = 
[ IMG_UNKNOWN_TILE,
  IMG_EMPTY_TILE,
]

window.setInterval(game_timer, 1000)

preload_image_list.forEach(function (item) {
  render_image(item, 0, 0, SQUARE_SIZE, SQUARE_SIZE, false) 
})

const socket = new WebSocket('ws://localhost:8081 ')
socket.addEventListener('message', function (event) {
    game_context = JSON.parse(event.data)
    window.requestAnimationFrame(render_game_map)
    if (canvas.width != game_context.max_x * SQUARE_SIZE ||
       canvas.height != game_context.max_y * SQUARE_SIZE) {
      canvas.width = game_context.max_x * SQUARE_SIZE
      canvas.height = game_context.max_y * SQUARE_SIZE
    }
    if (game_running) {
      mine_count_label.textContent = game_context["mines"] - game_context["flags"]
    }
  })

socket.addEventListener('error', function (event) {
    console.log('WebSocket error: ', event);
  alert('Connection Failed')
  });

socket.onclose = function(event) {
  console.log('WebSocket error: ', event);
  alert('Connection to Server Closed')
};