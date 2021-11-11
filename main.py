# main.py
# Ben Morrison
import os, time as tim

import pygame, math, random, pygame.gfxdraw
from random import randint, random
from physics.particle import *
from physics.bouncer import *
from pprint import pprint as pp

# Imports for gif
from PIL import Image
import glob

# Imports for mp
import pickle

# Pygame setup and application stuff
game_name = "DVD Logo"
pygame.init()
display, clock = pygame.display.Info(), pygame.time.Clock()
width, height = display.current_w // 2, display.current_h // 2
center_x, center_y = width // 2, height // 2
win = pygame.display.set_mode((width, height))
pygame.display.set_caption(f"{game_name} {width}x{height}")


# Functions
def screensaver():
    # Setting up loop variables
    running, paused, time, frames = True, False, 0, 0
    deltas = [.1 for _ in range(10)]

    # Load data
    particles = []
    bouncer = Bouncer((center_x, center_y), Vector2(width - randint(0, 100), height - randint(0, 100)) / 10, "uah_logo.png")

    draw_bloom, recording = False, None
    logging = False
    partition_size = 20

    neighborhood_size = 5
    neighborhood = []
    for y in range(neighborhood_size):
        for x in range(neighborhood_size):
            neighborhood.append((x - neighborhood_size//2, y - neighborhood_size//2))

    while running:
        delta = clock.tick(60) / 1000
        delta = 1 / 60
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
                    for i in range(1):
                        speed = 150 + 50 * (random() - .5)
                        angle = random() * math.pi / 2 + math.pi / 4
                        particles.append(Firework(
                            (width * random(), height - 1),
                            (speed * math.cos(angle), -speed * math.sin(angle)),
                            25, 2 + random() * 2, int(50 + 25 * random()),
                            150,  # normally 300
                            particles, None, 0
                        ))
                elif key == pygame.K_b:
                    draw_bloom = not draw_bloom
                elif key == pygame.K_F12:
                    if not recording:
                        frames = 0
                        recording = "recordings\\" + "".join(["abcdefghijklmnopqrstuvwxyz"[randint(0, 25)] for _ in range(10)])
                        os.mkdir(recording)
                    else:
                        # Load up the frames
                        frames = []
                        imgs = glob.glob(f"{recording}/*.png")
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
                        for i in imgs:
                            os.remove(i)

                        # Remove the empty frames directory
                        os.rmdir(recording)

                        recording = None
                elif key == pygame.K_F11:
                    logging = not logging

            elif event.type == pygame.KEYDOWN:
                pass

        # Ticking
        deltas.append(delta)
        deltas.pop(0)
        avg_delta = sum(deltas) / 10

        if not paused:
            time += delta
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
            bouncer.tick(delta)

        # Drawing
        render_time = tim.time()
        win.fill((0, 0, 50))
        # win.blit(bouncer.surf, bouncer.position)

        particle_map = [[[] for _ in range(height // partition_size)] for _ in range(width // partition_size)]
        for particle in particles:
            win.blit(particle.surf, particle.position)

            # Bloom stuff
            pos = particle.position + (particle.size / 2)

            if 0 <= pos.x < width and 0 <= pos.y < height:
                particle_map[int(pos.x // partition_size)][int(pos.y // partition_size)].append(
                    [[int(pos.x * 100) / 100, int(pos.y * 100) / 100], [int(value * 100) / 100 for value in particle.color]]
                )
        # print("-----------------------------------------------")
        # print(",\n".join([str(ele) for ele in particle_map]))
        # ---------------------------------------------------------------------------------------------------- Bloom ---

        if draw_bloom:
            bloom_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            # print("-----------------------------------")
            # print(",\n".join(f"[{', '.join([str(ele2) for ele2 in ele])}]" for ele in pygame.surfarray.pixels3d(bloom_surf)))
            p_width, p_height = int(width // partition_size), int(height // partition_size)

            # Looping through each partition L -> R then T -> B
            for partition_y in range(p_height):
                for partition_x in range(p_width):
                    nearby_particles = []
                    nearby_particles += particle_map[partition_x][partition_y]
                    # Grabbing neighboring partitions
                    for x, y in neighborhood:
                        if 0 <= partition_x + x < p_width and 0 <= partition_y + y < p_height:
                            nearby_particles += particle_map[partition_x + x][partition_y + y]

                    if not nearby_particles:
                        continue

                    # Looping over each particle within the partition
                    for x in range(partition_size):
                        for y in range(partition_size):
                            pos = Vector2(partition_x * partition_size + x, partition_y * partition_size + y)

                            # Finding minimum distance from a particle
                            min_dist, closest_part = width, None
                            for part_pos, color in nearby_particles:
                                part_pos = Vector2(part_pos)
                                dist = Vector2(part_pos - pos).magnitude()
                                if dist < min_dist:
                                    min_dist = dist
                                    closest_part = color

                            intensity = 1
                            if min_dist != 0:
                                intensity = 100 / (min_dist ** 2)

                            color = [closest_part[i] for i in range(3)] + [min(255, 255 // 8 * intensity)]
                            # print(color)
                            bloom_surf.set_at((int(pos.x), int(pos.y)), color)
                            # win.set_at((int(pos.x), int(pos.y)), (255, 0, 0))

            win.blit(bloom_surf, (0, 0))

        win.blit(surf.generate_text(f"Particle count: {len(particles)}\n"
                                    f"fps: {1/max(deltas):.2f} < {1/avg_delta:.2f} < {1/min(deltas):.2f}\n"
                                    f"render time: {tim.time() - render_time:03.3f}",
                                    spacing=15), (0, 0))

        if not paused and recording:
            pygame.image.save(win, f"{recording}/frame_{frames:010}.png")

        if not paused and logging:
            byte_file = open(f"bins/particles_{frames:06}.dat", "wb")
            pickle.dump(particle_map, byte_file)
            byte_file.close()

        if not paused and (recording or logging):
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
