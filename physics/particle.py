from random import randint, random
from math import pi, cos, sin
from pygame import Vector2
import pygame


_bloom_surf = pygame.Surface((50, 50), pygame.SRCALPHA | pygame.HWSURFACE)
for x in range(_bloom_surf.get_width()):
    for y in range(_bloom_surf.get_height()):
        dist = (Vector2(_bloom_surf.get_size()) / 2 - Vector2(x, y)).magnitude_squared()
        _bloom_surf.set_at((x, y), [255, 255, 255, min(255.0, 255 // 8 * (100 / max(dist, 1)))])


def change_surf_color(rgb, surf):
    _surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA | pygame.HWSURFACE)
    _surf.blit(surf, (0, 0))

    for x in range(_surf.get_width()):
        for y in range(_surf.get_height()):
            rgba = _surf.get_at((x, y))
            if rgba[3] > 0:
                alpha = rgba[3]
                if len(rgb) > 3:
                    alpha = min(alpha, rgb[3])
                _surf.set_at((x, y), (*rgb[:3], alpha))

    return _surf


class ColorAnimation:
    def __init__(self, *colors, generate_bloom=False):
        self.life_total = sum([life for color, life in colors])
        self.colors = []
        self._bloom = []

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

        if generate_bloom:
            self._bloom.append(change_surf_color(self.colors[0], _bloom_surf))

    def get_color(self, life_percentage):
        return self.colors[int(life_percentage * len(self.colors))]

    def get_bloom(self, life_percentage):
        index = int(life_percentage * len(self.colors))
        while not index < len(self._bloom):
            self._bloom.append(change_surf_color(self.colors[len(self._bloom)], _bloom_surf))
        return self._bloom[index]


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

    def get_bloom(self):
        return self.color_generator.get_bloom(self.life / self.max_life)

    def get_color(self):
        return self.color_generator.get_color(self.life / self.max_life)

    x = property(get_x)
    y = property(get_y)
    color = property(get_color)

    surf = property(get_surf)

class Firework(Particle):
    def __init__(self, position, velocity, explosion_time, explosion_height, explosion_size, acceleration, particles, color_generator=None, tier=0):
        if not color_generator:
            color_generator = ColorAnimation(((255, 255, 255), 0))
        super().__init__(position, velocity, 5, explosion_time, color_generator, True)
        self.particles = particles

        self.explosion_size = explosion_size
        self.explosion_height = explosion_height

        if acceleration == -1:
            self.gravity = Vector2(0, 0)
            acceleration = 0
        self.acceleration = Vector2(0, -acceleration)

        self.tier = tier

    def tick(self, delta):
        self.velocity += self.acceleration * delta
        super().tick(delta)

        if self.y < self.explosion_height:
            self.alive = False

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
            colors = 1 + int(5 * random() ** 5)
            print(colors)
            for _ in range(colors):
                color_gen = ColorAnimation((random_color(), 4), (random_color(), 6), (random_color(), 1), (random_color(), 2), ((255, 255, 255, 0), 0), generate_bloom=True)

                for i in range(self.explosion_size // colors):
                    angle, velocity = random() * 2 * pi, random() * 100
                    self.particles.append(Particle(
                        self.position,
                        Vector2(cos(angle) * velocity, sin(angle) * velocity),
                        int(random() * 5), 3 + random(), color_gen
                    ))
        elif self.tier > 0:
            color_gen = ColorAnimation((random_color(), 5), ((*random_color(), 255), 0), generate_bloom=True)

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

