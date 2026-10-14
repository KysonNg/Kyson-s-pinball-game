import pygame


class Bumper:
    color_list = ["#EA00D9", "#CC00FF", "#03D8F3"]

    def __init__(self, x, y, r):
        self.bumper_position = pygame.Vector2(x, y)
        self.radius = r
        self.mass = r * r
        self.color = self.color_list[0]
        self.index = 0

    def color_change(self):
        self.index = (self.index + 1) % len(self.color_list)
        self.color = self.color_list[self.index]

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (round(self.bumper_position.x), round(self.bumper_position.y)),
            self.radius,
        )