# main.py
# Ben Morrison


import pygame, math, random, pygame.gfxdraw
from random import randint, random
from physics.particle import *
from physics.bouncer import *
from pprint import pprint as pp

# Pygame setup and application stuff
game_name = "DVD Logo"
pygame.init()
display, clock = pygame.display.Info(), pygame.time.Clock()
width, height = display.current_w, display.current_h
center_x, center_y = width // 2, height // 2
win = pygame.display.set_mode((width, height))
pygame.display.set_caption(game_name)


# Functions
def screensaver():
    # Setting up loop variables
    running, paused, time = True, False, 0
    deltas = [.1 for _ in range(10)]

    # Load data
    particles = []
    bouncer = Bouncer((center_x, center_y), Vector2(width - randint(0, 100), height - randint(0, 100)) / 10, "uah_logo.png")

    while running:
        delta = clock.tick(60) / 1000

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
                    for i in range(4):
                        speed = 150 + 50 * (random() - .5)
                        angle = random() * math.pi / 2 + math.pi / 4
                        particles.append(Firework(
                            (width * random(), height - 1),
                            (speed * math.cos(angle), -speed * math.sin(angle)),
                            25, 2 + random() * 2, int(50 + 100 * random()), 200, particles
                        ))

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

                if not 0 < particle.x < width:
                    particle.alive = False
                if not 0 < particle.y < height:
                    particle.alive = False

            i = 0
            while i < len(particles):
                if not particles[i].alive:
                    particles.pop(i)
                else:
                    i += 1
            bouncer.tick(delta)

        # Drawing
        win.fill((0, 0, 50))

        win.blit(bouncer.surf, bouncer.position)
        for particle in particles:
            win.blit(particle.surf, particle.position)

        win.blit(surf.generate_text(f"Particle count: {len(particles)}\n"
                                    f"fps: {1/max(deltas):.2f} < {1/avg_delta:.2f} < {1/min(deltas):.2f}",
                                    spacing=15), (0, 0))

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
