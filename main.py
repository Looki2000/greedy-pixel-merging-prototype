import pygame
import numpy as np
import colorsys
import os

##### CONFIG #####
window_size = 720

pixel_count = 20 # must be a factor of window_size

pixel_material = 1


grid_col = (200,) * 3


debug = False
debug_fps = 8
##################

if window_size % pixel_count != 0:
    raise Exception("window_size must be divisible by pixel_count without remainder")

pixel_size = window_size // pixel_count
half_pixel_size = pixel_size / 2

pixel_max_idx = pixel_count - 1

# pygame init
pygame.init()
window = pygame.display.set_mode((window_size, window_size))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)



# pixel material colors
pixel_material_cols = tuple(tuple(int(val * 255) for val in colorsys.hsv_to_rgb(h/360, 0.5, 1)) for h in range(0, 360, 36))

# rect material colors
rect_cols = tuple(tuple(int(val * 255) for val in colorsys.hsv_to_rgb(h/360, 1, 0.75)) for h in range(0, 360, 36))


def draw_map():
    # draw grid lines
    for i in range(pixel_count):
        pygame.draw.line(window, grid_col, (0, i * pixel_size), (window_size, i * pixel_size))
        pygame.draw.line(window, grid_col, (i * pixel_size, 0), (i * pixel_size, window_size))

    # draw all pixels:
    for y in range(pixel_count):
        for x in range(pixel_count):
            if map[y][x] != 0:
                pygame.draw.rect(window, pixel_material_cols[map[y][x] - 1], (x * pixel_size, y * pixel_size, pixel_size, pixel_size))


# array of pixels
if "map.npy" in os.listdir():
    map = np.load("map.npy")
    print("loaded map from map.npy file")
else:
    map = np.zeros((pixel_count, pixel_count), dtype=np.int8)
    print("map.npy not found, creating new map")


# rectangles generated from map using greedy pixel merging
# format: [x1, y1, x2, y2, material]
rectangles = []

def greedy_voxel_merging():
    map_copy = map.copy()

    for y in range(pixel_count):        
        last_material = 0

        for x in range(pixel_count):

            #### block starting/ending detections ####

            block_ended = False

            # if material changed
            if map_copy[y][x] != last_material:
                ## if block ended
                # material switch NOT from air
                if last_material != 0:
                    block_end_x = x
                    block_ended = True

                # if new block just started AND NOT block ended while new one starting
                if map_copy[y][x] != 0 and not block_ended:
                    block_start_x = x

            ## if block ended
            # end of map row on NOT air
            if x == pixel_max_idx and map_copy[y][x] != 0:
                block_end_x = x + 1
                block_ended = True
                last_material = map_copy[y][x]


            ############################################

            if block_ended:
                if debug:
                    pygame.draw.circle(window, (255, 0, 0), (block_start_x * pixel_size, y * pixel_size + half_pixel_size - 5), 5)
                    pygame.draw.circle(window, (0, 255, 0), (block_end_x * pixel_size, y * pixel_size + half_pixel_size + 5), 5)
                    pygame.display.update()
                    clock.tick(debug_fps)

                # scanning for other rows under existing row that can be included in the block
                block_end_y = y
                invalid_row = False
                while True:
                    block_end_y += 1

                    # if the end of the map is reached, break the loop
                    if block_end_y == pixel_count:
                        break

                    # check if all materials in row are the same as the block's material
                    for x2 in range(block_start_x, block_end_x):
                        if debug:
                            pygame.draw.circle(window, (255, 0, 255), (x2 * pixel_size + half_pixel_size, block_end_y * pixel_size + half_pixel_size-5), 5)
                            pygame.display.update()
                            clock.tick(debug_fps)

                        if map_copy[block_end_y][x2] != last_material:
                            invalid_row = True
                            break

                    if invalid_row:
                        break
                    # "else continue"

                    # set all values of next row that will be added to the block to 0 to prevent them from being treeated as a new block in the next y loop iteration
                    map_copy[block_end_y][block_start_x:block_end_x] = 0

                    if debug:
                        for i in range(block_start_x, block_end_x):
                            pygame.draw.circle(window, (0, 0, 255), (i * pixel_size + half_pixel_size, block_end_y * pixel_size + half_pixel_size), 5)
                        pygame.display.update()
                        clock.tick(debug_fps)

                # add block to rectangles list
                rectangles.append([block_start_x, y, block_end_x, block_end_y, last_material - 1])

                if debug:
                    # draw last rectangle
                    #pygame.draw.rect(window, rect_cols[rect[4]], (rect[0] * pixel_size, rect[1] * pixel_size, (rect[2] - rect[0]) * pixel_size, (rect[3] - rect[1]) * pixel_size), 5)
                    pygame.draw.rect(window, rect_cols[last_material - 1], (block_start_x * pixel_size, y * pixel_size, (block_end_x - block_start_x) * pixel_size, (block_end_y - y) * pixel_size), 5)

                # if last block is touching current block, use current position as current block's start position
                if map_copy[y][x] != 0:
                    block_start_x = x

            last_material = map_copy[y][x]


if debug:
    draw_map()

greedy_voxel_merging()

if debug:
    debug = False

last_mouse_tile_pos = None
mouse_pressed = False

# main loop
while True:
    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # get key presses for 1-9,0 (0 is 10)
    keys = pygame.key.get_pressed()
    for i in range(10):
        if keys[pygame.K_0 + i]:
            pixel_material = 10 if i == 0 else i


    # pixel placement
    if pygame.mouse.get_pressed()[0]:
        mouse_pos = pygame.mouse.get_pos()

        mouse_tile_pos = (mouse_pos[0] // pixel_size, mouse_pos[1] // pixel_size)

        if not mouse_pressed:
            mouse_place_material = pixel_material if map[mouse_tile_pos[1]][mouse_tile_pos[0]] == 0 else 0
            mouse_pressed = True
        

        if last_mouse_tile_pos != mouse_tile_pos:
            map[mouse_tile_pos[1]][mouse_tile_pos[0]] = mouse_place_material

            # greedy merging in a loop for now
            rectangles = []
            greedy_voxel_merging()


        last_mouse_tile_pos = mouse_tile_pos
    elif mouse_pressed:
        mouse_pressed = False
        last_mouse_tile_pos = None

        # save map array to file
        np.save("map.npy", map)
        print("map saved")


    window.fill((0, 0, 0))

    draw_map()

    # draw rectangles with thickness
    for rect in rectangles:
        pygame.draw.rect(window, rect_cols[rect[4]], (rect[0] * pixel_size, rect[1] * pixel_size, (rect[2] - rect[0]) * pixel_size, (rect[3] - rect[1]) * pixel_size), 5)
    
    # draw pixel type text
    text = font.render(f"Pixel type: {pixel_material}", True, pixel_material_cols[pixel_material - 1])
    window.blit(text, (10, 5))

    # update
    pygame.display.update()
    clock.tick(60)