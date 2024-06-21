import pygame as pg
import random
import math

pg.init()
FPS = 60

WIDTH,HEIGHT = 800,800
ROWS,COLS = 4,4

RECT_WIDTH = WIDTH//ROWS
RECT_HEIGHT = HEIGHT//COLS

OUTLINE_COLOR = (187,173,160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205,192,180)
FONT_COLOR = (119,110,101)

WINDOW = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("2048")
FONT = pg.font.SysFont("comicsans", 60, bold=True)
MOVE_SPEED = 40

class Tile:
    COLORS = [
        (237,229,218),
        (238,225,201),
        (243,178,122),
        (246,150,101),
        (247,124,95),
        (247,95,59),
        (237,208,115),
        (237,204,99),
        (236,202,80),
    ]

    def __init__(self,value, row, col) -> None:
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color =  self.get_color()
        pg.draw.rect(window, color, (self.x , self.y, RECT_WIDTH, RECT_HEIGHT))
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text, 
            (
                self.x + (RECT_WIDTH/2 - text.get_width()/2),
                self.y + (RECT_HEIGHT/2 - text.get_height()/2)
            )
        )

    def set_pos(self, ceil = False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x/ RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x/ RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

def grid(window):
    for row in range(1,ROWS):
        y = row * RECT_HEIGHT
        pg.draw.line(window, OUTLINE_COLOR, (0,y), (WIDTH,y), OUTLINE_THICKNESS)

    for col in range(1,COLS):
        x = col * RECT_HEIGHT
        pg.draw.line(window, OUTLINE_COLOR, (x,0), (x,HEIGHT), OUTLINE_THICKNESS)

    pg.draw.rect(window,OUTLINE_COLOR, (0,0,WIDTH,HEIGHT), OUTLINE_THICKNESS)

def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)
    for tile in tiles.values():
        tile.draw(window)
    grid(window)
    pg.display.update()

def get_random_pos(tiles):
    """
    generates a random (row,col) that isn't already occupied for a tile
    """
    row, col = None, None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)
        # if there isnt a tile occupying [row][col] then generate a tile at this location
        if f"{row}{col}" not in tiles:
            break
    return row,col

def update_tiles(window, tiles, sorted_tiles):
    """
    'sorted_tiles' used in 'move_tiles' is a sorted version of 'tiles' which is only temporarily used

    here 'tiles' is wiped clean and the contents of 'sorted_tiles' is assigned to 'tiles'
    """
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window,tiles)

def end_move(tiles):
    """
    when a move ends do the following:
        check if the board is full; game over if it is
        generate a new tile in random unoccupied space
    """
    if len(tiles) == 16:
        return "lost"
    
    row, col = get_random_pos(tiles)
    val = random.randrange(1,10)
    if val <= 8:
        val = 2
    else:
        val = 4
    tiles[f"{row}{col}"] = Tile(val, row, col)
    return "continue"

def move_tiles(window, tiles, clock, direction):
    """
    Moves tiles in the direction inputs pressed and merges tiles when necessary
    """
    updated = True
    # tells us which blocks have already merged in a movement bc we dont want to merge multiple sets of tiles
    # i.e. we dont allow merged blocks to continuously merge in one movement: 2:2 -> 4:4 -> 8
    blocks = set()

    if direction == "left":
        # sort the tiles from left to right so the leftest tile moves left first 
        # followed by the second most leftest and so on
        sort_func = lambda x: x.col

        reverse = False

        # specifies how much we want to move each tile by each frame
        delta = (-MOVE_SPEED, 0)

        # if the column is at 0 then the tile is as far left as it can go
        boundary_check = lambda tile: tile.col == 0

        # returns the tile to the left if there is one 
        # to check if the current tile will be blocked or merge
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")

        # checks if a merge should occur based on the current movement
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_SPEED

        # if the tile to the left isnt the same value stop moving to the right of it (RECT_WIDTH)
        move_check = lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_SPEED
        
        ceil = True

    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_SPEED, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_SPEED
        move_check = lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_SPEED < next_tile.x
        ceil = False

    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_SPEED)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_SPEED
        move_check = lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_SPEED
        ceil = True

    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_SPEED)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_SPEED
        move_check = lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_SPEED < next_tile.y
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles)

    return end_move(tiles)

def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        val = random.randrange(1,10)
        if val <= 8:
            val = 2
        else:
            val = 4
        tiles[f"{row}{col}"] = Tile(val, row, col)
    return tiles


def main(window):
    clock = pg.time.Clock()
    run = True

    tiles = generate_tiles()
    while run:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT or event.key == pg.K_a:
                    move_tiles(window, tiles, clock, "left")
                if event.key == pg.K_RIGHT or event.key == pg.K_d:
                    move_tiles(window, tiles, clock, "right")
                if event.key == pg.K_UP or event.key == pg.K_w:
                    move_tiles(window, tiles, clock, "up")
                if event.key == pg.K_DOWN or event.key == pg.K_s:
                    move_tiles(window, tiles, clock, "down")
        draw(WINDOW, tiles)

    pg.quit()
    
if __name__ == "__main__":
    main(WINDOW)