import math
import pygame


class Paddle:

    def __init__(
        self,
        x,
        y,
        length,
        thickness,
        rest_angle,
        active_angle,
        flip_speed,
        return_speed,
        color,
        active_key=pygame.K_SPACE,
    ):
        self.pivot_position = pygame.Vector2(x, y)
        self.length = length
        self.thickness = thickness
        self.rest_angle = rest_angle
        self.active_angle = active_angle
        self.flip_speed = flip_speed
        self.return_speed = return_speed
        self.color = color
        self.active_key = active_key
        self.angle = rest_angle
        self.angular_velocity = 0.0
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.update_geometry()

    def direction(self):
        radians = math.radians(self.angle)
        return pygame.Vector2(math.cos(radians), math.sin(radians))

    def update_geometry(self):
        direction = self.direction()
        half_width = self.thickness / 2
        perpendicular = (
            pygame.Vector2(-direction.y, direction.x) * half_width
        )
        end = self.pivot_position + direction * self.length
        self.points = (
            self.pivot_position + perpendicular,
            end + perpendicular,
            end - perpendicular,
            self.pivot_position - perpendicular,
        )

        min_x = min(point.x for point in self.points)
        max_x = max(point.x for point in self.points)
        min_y = min(point.y for point in self.points)
        max_y = max(point.y for point in self.points)
        self.rect = pygame.Rect(
            math.floor(min_x),
            math.floor(min_y),
            math.ceil(max_x) - math.floor(min_x),
            math.ceil(max_y) - math.floor(min_y),
        )

    def update_Rotation(self, keys):
        if keys[self.active_key]:
            target = self.active_angle
        else:
            target = self.rest_angle
        old_angle = self.angle
        if target == self.active_angle:
            speed = self.flip_speed
        else:
            speed = self.return_speed

        if self.angle < target:
            self.angle = min(self.angle + speed, target)
        elif self.angle > target:
            self.angle = max(self.angle - speed, target)

        self.angular_velocity = math.radians(self.angle - old_angle)
        self.update_geometry()

    def collide(self, ball):
        start = self.pivot_position
        segment = self.direction() * self.length
        relative_position = ball.ball_position - start
        segment_length_squared = segment.length_squared()
        if segment_length_squared == 0:
            return False

        fraction = max(
            0.0, min(1.0, relative_position.dot(segment) / segment_length_squared)
        )
        closest_point = start + segment * fraction
        offset = ball.ball_position - closest_point
        minimum_distance = ball.radius + self.thickness / 2
        distance_squared = offset.length_squared()

        if distance_squared >= minimum_distance * minimum_distance:
            return False

        if distance_squared > 0:
            normal = offset / math.sqrt(distance_squared)
        else:
            normal = pygame.Vector2(-segment.y, segment.x).normalize()
            if ball.velocity.dot(normal) > 0:
                normal = -normal

        ball.ball_position = closest_point + normal * minimum_distance

        contact_offset = closest_point - self.pivot_position
        paddle_velocity = (
            pygame.Vector2(-contact_offset.y, contact_offset.x)
            * self.angular_velocity
        )
        relative_velocity = ball.velocity - paddle_velocity
        normal_speed = relative_velocity.dot(normal)
        if normal_speed < 0:
            relative_velocity -= 2 * normal_speed * normal
            ball.velocity = relative_velocity + paddle_velocity

        return True

    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.points)
        pygame.draw.circle(
            screen,
            self.color,
            (round(self.pivot_position.x), round(self.pivot_position.y)),
            max(2, round(self.thickness / 2)),
        )