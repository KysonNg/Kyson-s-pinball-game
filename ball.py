import math
import random
import pygame


class Ball:

    def __init__(self, x, y, gravity, color):
        self.ball_position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, gravity)
        self.radius = 11
        self.color = color
        self.base_gravity = abs(gravity)

    def move(self, width, height):
        self.velocity += self.acceleration
        self.ball_position += self.velocity
        self.velocity *= 0.995
        if self.ball_position.x - self.radius < 0:
            self.ball_position.x = self.radius
            self.velocity.x *= -0.5
        elif self.ball_position.x + self.radius > width:
            self.ball_position.x = width - self.radius
            self.velocity.x *= -0.5

        if self.ball_position.y < height // 2:
            if self.acceleration.y > 0:
                self.velocity.y *= 0.8
            self.change_gravity("UP")
        else:
            if self.acceleration.y < 0:
                self.velocity.y *= 0.8
            self.change_gravity("DOWN")

    def change_gravity(self, side):
        if side == "UP":
            self.acceleration.y = -self.base_gravity
        elif side == "DOWN":
            self.acceleration.y = self.base_gravity

    def bumped(self, bumper):
        offset = self.ball_position - bumper.bumper_position
        minimum_distance = bumper.radius + self.radius
        distance_squared = offset.length_squared()

        if distance_squared > minimum_distance * minimum_distance:
            return False

        if distance_squared > 0:
            normal = offset / (distance_squared**0.5)
        else:
            normal = pygame.Vector2(1, 0)

        self.ball_position = bumper.bumper_position + normal * minimum_distance
        speed = self.velocity.dot(normal)
        if speed < 0:
            self.velocity -= 2 * speed * normal

        self.velocity.x += random.uniform(-0.5, 0.5)
        return True

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (round(self.ball_position.x), round(self.ball_position.y)),
            self.radius,
        )