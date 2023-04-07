import pygame
import numpy as np
import colorsys

##### CONFIG #####
window_size = 720

pixel_count = 20 # must be a factor of window_size

pixel_type = 1


grid_col = (200,) * 3
rect_col = (100, 100, 255)
##################

if window_size % pixel_count != 0:
    raise Exception("pixel_count must be a factor of window_size")

pixel_size = window_size // pixel_count

pixel_max_idx = pixel_count - 1

# pygame init
pygame.init()
window = pygame.display.set_mode((window_size, window_size))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)



# pixel type colors
pixel_type_cols = tuple(tuple(int(val * 255) for val in colorsys.hsv_to_rgb(h/360, 0.5, 1)) for h in range(0, 360, 36))
#print(pixel_type_cols)


# array of pixels
map = np.zeros((pixel_count, pixel_count), dtype=np.int8)
# rectangles generated from map using greedy voxel merging
rectangles = []



def greedy_voxel_merging():
    map_copy = map.copy()


    for y in range(pixel_count):
        block_size_x = 0
        block_size_y = 1

        last_val = 0

        block_scan_start = None
        for x in range(pixel_count):

            if map_copy[y][x] == 1:
                block_size_x += 1

                if last_val == 0:
                    block_scan_start = x
                    block_scan_y = y
                    
                    last_val = 1

            if (map_copy[y][x] == 0 or x == pixel_max_idx) and block_scan_start != None:
                last_val = 0

                block_scan_end = block_scan_start + block_size_x

                fit = True
                while block_scan_y <= pixel_max_idx and fit:
                    block_scan_y += 1
                    for val in map_copy[block_scan_y][block_scan_start:block_scan_end]:
                        if val == 0:
                            fit = False
                            break
                    
                    if fit:
                        # set the values to 0 so they are not used again
                        map_copy[block_scan_y][block_scan_start:block_scan_end] = 0

                        block_size_y += 1
                    else:
                        break

                rectangles.append((block_scan_start, y, block_size_x, block_size_y))
                
                block_size_x = 0
                block_size_y = 1
                block_scan_start = None

    print("====================")
    print(rectangles)
    print(len(rectangles))
    print("====================")



greedy_voxel_merging()

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
            pixel_type = 10 if i == 0 else i


    # pixel placement
    if pygame.mouse.get_pressed()[0]:
        mouse_pos = pygame.mouse.get_pos()

        mouse_tile_pos = (mouse_pos[0] // pixel_size, mouse_pos[1] // pixel_size)

        if not mouse_pressed:
            mouse_place_val = pixel_type if map[mouse_tile_pos[1]][mouse_tile_pos[0]] == 0 else 0
            mouse_pressed = True
        

        if last_mouse_tile_pos != mouse_tile_pos:
            map[mouse_tile_pos[1]][mouse_tile_pos[0]] = mouse_place_val

            # greedy merging in a loop for now
            rectangles = []
            greedy_voxel_merging()


        last_mouse_tile_pos = mouse_tile_pos
    else:
        mouse_pressed = False
        last_mouse_tile_pos = None


    window.fill((0, 0, 0))

    # draw grid lines
    for i in range(pixel_count):
        pygame.draw.line(window, grid_col, (0, i * pixel_size), (window_size, i * pixel_size))
        pygame.draw.line(window, grid_col, (i * pixel_size, 0), (i * pixel_size, window_size))

    # draw all pixels:
    for y in range(pixel_count):
        for x in range(pixel_count):
            if map[y][x] != 0:
                pygame.draw.rect(window, pixel_type_cols[map[y][x] - 1], (x * pixel_size, y * pixel_size, pixel_size, pixel_size))

    # draw rectangles with thickness
    for rect in rectangles:
        pygame.draw.rect(window, rect_col, (rect[0] * pixel_size, rect[1] * pixel_size, rect[2] * pixel_size, rect[3] * pixel_size), 5)
    
    # draw pixel type text
    text = font.render(f"Pixel type: {pixel_type}", True, pixel_type_cols[pixel_type - 1])
    window.blit(text, (10, 5))

    # update
    pygame.display.update()
    clock.tick(60)