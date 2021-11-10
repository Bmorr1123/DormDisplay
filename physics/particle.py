from random import randint, random
from math import pi, cos, sin
from pygame import Vector2
import pygame


class ColorAnimation:
    def __init__(self, *colors):
        self.life_total = sum([life for color, life in colors])
        self.colors = []

        if len(colors) > 1:
            for i in range(len(colors) - 1):
                c1, life1 = colors[i]
                c2, life2 = colors[i + 1]

                if len(c1) < 4:
                    c1 = (*c1, 255)
                if len(c2) < 4:
                    c2 = (*c2, 255)

                frames = life1 * 10
                for j in range(frames):
                    perc = j / frames
                    color = (
                        c1[0] * (1 - perc) + c2[0] * perc,
                        c1[1] * (1 - perc) + c2[1] * perc,
                        c1[2] * (1 - perc) + c2[2] * perc,
                        c1[3] * (1 - perc) + c2[3] * perc
                    )
                    self.colors.append(color)

            self.colors.append(colors[-1][0])
        else:
            self.colors.append(colors[0][0])

    def get_color(self, life_percentage):
        return self.colors[int(life_percentage * len(self.colors))]


class Particle:
    def __init__(self, position, velocity, size, max_life, color_gen, gravity=True):
        self.alive = True
        # Basic data
        self.position = Vector2(position)
        self.velocity = Vector2(velocity)
        self.size = Vector2(size, size)

        self.life = 0
        self.max_life = max_life

        self.color_generator = color_gen

        # r, g = randint(200, 255), randint(0, 255)
        # g = min(r, g)
        # self.color = (r, g, 0)
        self.gravity = Vector2(0, 150 * gravity)

        # Surface generation
        self._surf = pygame.surface.Surface((size, size), pygame.SRCALPHA)
        self.last_color = None

    def tick(self, delta):
        self.velocity += self.gravity * delta
        self.position += self.velocity * delta

        self.life += delta
        if self.life > self.max_life:
            self.alive = False

    def get_x(self):
        return int(self.position.x)

    def get_y(self):
        return int(self.position.y)

    def get_surf(self):
        color = self.color
        if color != self.last_color:
            self._surf.fill(color)
            self.last_color = color
        return self._surf

    def get_color(self):
        return self.color_generator.get_color(self.life / self.max_life)

    x = property(get_x)
    y = property(get_y)
    color = property(get_color)

    surf = property(get_surf)

class Firework(Particle):
    def __init__(self, position, velocity, size, explosion_time, explosion_size, acceleration, particles, color_generator=None, tier=0):
        if not color_generator:
            color_generator = ColorAnimation(((255, 255, 255), 0))
        super().__init__(position, velocity, size, explosion_time, color_generator, True)
        self.particles = particles

        self.explosion_size = explosion_size

        if acceleration == -1:
            self.gravity = Vector2(0, 0)
            acceleration = 0
        self.acceleration = Vector2(0, -acceleration)

        self.tier = tier

    def tick(self, delta):
        self.velocity += self.acceleration * delta
        super().tick(delta)

        if not self.alive:
            self.splode()

    def splode(self):

        def random_color():
            r, g, b = 0, 0, 0
            while r + g + b < 255 * 1.5:
                r, g, b = random() * 255, random() * 255, random() * 255
            return r, g, b
        # color_gen = ColorAnimation(((255, 0, 0), 4), ((255, 255, 0), 2), ((255, 255, 255, 0), 0))
        if self.tier == 0:
            color_gen = ColorAnimation((random_color(), 4), (random_color(), 6), (random_color(), 1), (random_color(), 2), ((255, 255, 255, 0), 0))

            for i in range(self.explosion_size):
                angle, velocity = random() * 2 * pi, random() * 100
                self.particles.append(Particle(
                    self.position,
                    Vector2(cos(angle) * velocity, sin(angle) * velocity),
                    int(random() * 5), 3 + random(), color_gen
                ))
        elif self.tier > 0:
            color_gen = ColorAnimation((random_color(), 5), ((*random_color(), 255), 0))

            for i in range(self.explosion_size):
                angle, velocity = random() * 2 * pi, random() * 100
                self.particles.append(Firework(
                    self.position,
                    Vector2(cos(angle) * velocity, sin(angle) * velocity),
                    int(random() * 5), 2, int(15 + random() * 10), -1, self.particles, color_gen, self.tier - 1
                ))

    # TODO: Come up with a better idea how to randomly generate colors to switch between
    possible_colors = {
        (255, 255, 255): [
            (255, 0, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 255, 255),
            (0, 0, 255),
            (255, 0, 255)
        ],
        (255, 0, 0): [
            (255, 255 // 2, 0),
            (255, 255, 0),
            (255, 0, 255)
        ]
    }

