# main.py
# Ben Morrison
import os, time

import pygame, math, random, pygame.gfxdraw
from random import randint, random
from physics.particle import *
from physics.bouncer import *
from pprint import pprint as pp

# Imports for gif
from PIL import Image
import glob

# Pygame setup and application stuff
game_name = "DVD Logo"
pygame.init()
display, clock = pygame.display.Info(), pygame.time.Clock()
width, height = display.current_w, display.current_h
center_x, center_y = width // 2, height // 2
win = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption(game_name)


# Functions
def screensaver():
    # Setting up loop variables
    running, paused, total_time, frames = True, False, 0, 0
    deltas = [.1 for _ in range(10)]

    # Load data
    particles = []
    bouncer = Bouncer((center_x, center_y), (0, 0), "uah_logo.png")
    velocity = (Vector2(width, height) - bouncer.get_br_corner()) / 5

    velocity.x *= (-1) ** randint(0, 1)
    velocity.y *= (-1) ** randint(0, 1)

    bouncer.velocity = velocity
    # Vector2(width - randint(0, 100), height - randint(0, 100)) / 10

    draw_bloom, recording = False, None
    partition_size, neighborhood_size = 20, 3
    neighborhood = []
    for y in range(neighborhood_size):
        for x in range(neighborhood_size):
            neighborhood.append((x - neighborhood_size // 2, y - neighborhood_size // 2))

    while running:
        delta = clock.tick(60) / 1000
        if recording:
            delta = 1 / 60

        delta = min(delta, 1/15)

        # Event handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            # Key Events
            elif event.type == pygame.KEYUP:
                key = event.key
                print(event.unicode)
                if key == pygame.K_ESCAPE:
                    return -1
                elif key == pygame.K_p:
                    paused = not paused
                elif key == pygame.K_r:
                    return 0
                elif key == pygame.K_SPACE:
                    # (self, position, velocity, size, explosion_time, explosion_size, acceleration, particles, color_generator=None, tier=0)
                    for i in range(5):
                        speed = 150 + 50 * (random() - .5)
                        angle = random() * math.pi / 4 + 3 * math.pi / 4 * randint(0, 1)
                        explosion_height = height * random() * .75

                        fx = 1
                        if angle > math.pi / 2:
                            fx = width - 1

                        particles.append(Firework(
                            (fx, height * random()),
                            (4 * speed * math.cos(angle), 2 * -speed * math.sin(angle)),
                            2 + random() * 2, 0, int(50 + 25 * random()),
                            0,  # normally 300
                            particles, None, 0
                        ))
                elif key == pygame.K_b:
                    draw_bloom = not draw_bloom
                elif key == pygame.K_F12:
                    if not recording:
                        frames = 0
                        recording = "recordings\\" + "".join(["abcdefghijklmnopqrstuvwxyz"[randint(0, 25)] for _ in range(10)])
                        if "frames" in os.listdir("recordings"):
                            os.rmdir("recordings/frames")
                            os.mkdir("recordings/frames")
                    else:
                        # Load up the frames
                        frames = []
                        imgs = glob.glob(f"recordings/frames/*.png")
                        for i in imgs:
                            new_frame = Image.open(i)
                            frames.append(new_frame)

                        # Save into a GIF file that loops forever
                        frames[0].save(f'{recording}.gif', format='GIF',
                                       append_images=frames[1:],
                                       save_all=True,
                                       optimize=True,
                                       duration=16, loop=1, quality=90)

                        # Remove the old frames
                        # for i in imgs:
                        #     os.remove(i)

                        # Remove the empty frames directory
                        # os.rmdir(recording)

                        recording = None

            elif event.type == pygame.KEYDOWN:
                pass

        # Ticking
        deltas.append(delta)
        deltas.pop(0)
        avg_delta = sum(deltas) / 10

        if not paused:
            total_time += delta
            for particle in particles:
                particle.tick(delta)
                pos = particle.position

                if not -width // 2 < pos.x < width * 1.5:
                    particle.alive = False
                if not -height // 2 < pos.y < height * 1.5:
                    particle.alive = False

            i = 0
            while i < len(particles):
                if not particles[i].alive:
                    particles.pop(i)
                else:
                    i += 1

            if bouncer.tick(delta):
                for i in range(5):
                    speed = 150 + 50 * (random() - .5)
                    angle = random() * math.pi / 2 + math.pi / 4
                    explosion_height = height * random() * .75

                    particles.append(Firework(
                        (width * random(), height - 1),
                        (speed * math.cos(angle), 6 * -speed * math.sin(angle)),
                        25, explosion_height, int(50 + 25 * random()),
                        150,  # normally 300
                        particles, None, 0
                    ))

        # Drawing
        render_time = time.time()
        win.fill((0, 0, 50))
        win.blit(bouncer.surf, bouncer.position)

        for particle in particles:
            # for i in range(10):
            #     win.blit(particle.color_generator.get_bloom(i/10), particle.position + (i * 25, 0))
            bloom = particle.get_bloom()
            if bloom:
                win.blit(bloom, particle.position - Vector2(bloom.get_size()) / 2)
            else:
                win.blit(particle.surf, particle.position - Vector2(particle.size) / 2)


        win.blit(surf.generate_text(f"Particle count: {len(particles)}\n"
                                    f"fps: {1 / max(deltas):.2f} < {1 / avg_delta:.2f} < {1 / min(deltas):.2f}\n"
                                    f"render time: {time.time() - render_time:03.3f}",
                                    spacing=15), (0, 0))

        if not paused and recording:
            pygame.image.save(win, f"recordings/frames/frame_{frames:010}.png")
            frames += 1

        pygame.display.update()

    return -1

def main():
    looping = True
    next_view = 0
    while looping:
        if next_view == -1:
            looping = False
        elif next_view == 0:
            next_view = screensaver()
        else:
            print(f"ERROR: View #{next_view} not found!")
            looping = False
    print("Quitting application!")


if __name__ == '__main__':
    main()

pygame.display.quit()
