import os, pygame

path = "recordings/frames"
file_paths = os.listdir(path)
file_paths.sort()

files = []
for file in file_paths:
    number = int(file[file.find("_") + 1:file.find(".")])
    files.append(pygame.image.load(f"{path}/{file}"))


pygame.init()
game_name = "Frame Display"
display, clock = pygame.display.Info(), pygame.time.Clock()
pygame.display.set_caption(game_name)
width, height = display.current_w, display.current_h
center_x, center_y = width // 2, height // 2
win = pygame.display.set_mode((width, height))

running = True
display_images, frame = False, 0
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        # Key Events
        elif event.type == pygame.KEYUP:
            key = event.key
            print(event.unicode)
            if key == pygame.K_ESCAPE:
                running = False
            if key == pygame.K_g:
                if display_images:
                    frame = 0
                display_images = not display_images

    delta = clock.tick(60) / 1000

    win.fill((255, 255, 255))
    win.blit(files[frame % len(files)], (0, 0))
    if display_images:
        frame += 1
    pygame.display.update()



