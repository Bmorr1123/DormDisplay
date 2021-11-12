from pygame import Vector2
from main import width, height
from random import random
import surf


class Bouncer:
    def __init__(self, center, velocity, image):

        self.surf = surf.change_surf_color((255, 255, 255), surf.load_image(image))
        self.size = self.surf.get_size()

        self.velocity = Vector2(velocity)
        self.position = Vector2(center[0] - self.size[0] // 2, center[1] - self.size[1] // 2)
        self.x, self.y = lambda: int(self.position.x), lambda: int(self.position.y)

        self._bounces = 0

    def tick(self, delta):
        self.position += self.velocity * delta

        def random_color():
            r, g, b = 0, 0, 0
            while r + g + b < 255 * 1.5:
                r, g, b = random() * 255, random() * 255, random() * 255
            return r, g, b

        if self.x() < 0 or width < self.x() + self.size[0]:
            self.velocity.x *= -1
            # self.velocity += Vector2(random())
            surf.change_surf_color(random_color(), self.surf)

            if self._bounces:
                return True
            self._bounces += 1 / 10

            self.position.x = min(max(0, self.x()), width)

        if self.y() < 0 or height < self.y() + self.size[1]:
            self.velocity.y *= -1
            # self.velocity += Vector2(random(), random())
            surf.change_surf_color(random_color(), self.surf)

            if self._bounces:
                return True
            self._bounces += 1 / 10

            self.position.y = min(max(0, self.y()), height)

        self._bounces = max(0, self._bounces - delta)

        return False

    def get_tl_corner(self):
        return self.position

    def get_tr_corner(self):
        return self.position + Vector2(self.size[0], 0)

    def get_bl_corner(self):
        return self.position + Vector2(0, self.size[1])

    def get_br_corner(self):
        return self.position + self.size
