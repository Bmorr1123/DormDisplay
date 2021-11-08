from pygame import Vector2
from main import width, height
import surf


class Bouncer:
    def __init__(self, center, velocity, image):

        self.surf = surf.change_surf_color((255, 255, 255), surf.load_image(image))
        self.size = self.surf.get_size()

        self.velocity = Vector2(velocity)
        self.position = Vector2(center[0] - self.size[0] // 2, center[1] - self.size[1] // 2)
        self.x, self.y = lambda: int(self.position.x), lambda: int(self.position.y)

    def tick(self, delta):
        self.position += self.velocity * delta
        if self.x() < 0 or width < self.x() + self.size[0]:
            self.velocity.x *= -1
        if self.y() < 0 or height < self.y() + self.size[1]:
            self.velocity.y *= -1

    def get_tl_corner(self):
        return self.position

    def get_tr_corner(self):
        return self.position + Vector2(self.size[0], 0)

    def get_bl_corner(self):
        return self.position + Vector2(0, self.size[1])

    def get_br_corner(self):
        return self.position + self.size
