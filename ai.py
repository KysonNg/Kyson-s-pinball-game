import pygame


class P2_AI:

    def __init__(self, left_paddle, right_paddle):
        self.left_paddle = left_paddle
        self.right_paddle = right_paddle
        self.state = "PATROL"

        self.detection_range = 350.0
        self.strike_range = 140.0
        self.fov_threshold = 0.3

        self.left_swing_timer = 0
        self.right_swing_timer = 0
        self.swing_duration = 6
        self.swing_cooldown = 12

    def update(self, ball, height):
        ai_center = pygame.Vector2(200, 80)
        to_ball = ball.ball_position - ai_center
        distance = to_ball.length()

        if distance > 0:
            dir_to_ball = to_ball.normalize()
        else:
            dir_to_ball = pygame.Vector2(0, 1)

        ai_facing = pygame.Vector2(0, 1)
        dot_prod = ai_facing.dot(dir_to_ball)

        if distance < self.strike_range and dot_prod > self.fov_threshold:
            self.state = "STRIKE"
        elif (
            distance < self.detection_range
            and ball.ball_position.y < (height // 2) + 50
        ):
            self.state = "TRACK"
        else:
            self.state = "PATROL"

        if self.left_swing_timer > 0:
            self.left_swing_timer -= 1
        if self.right_swing_timer > 0:
            self.right_swing_timer -= 1

        if self.state == "STRIKE":
            if ball.ball_position.x < 200 and self.left_swing_timer == 0:
                self.left_swing_timer = (
                    self.swing_duration + self.swing_cooldown
                )
            elif ball.ball_position.x >= 200 and self.right_swing_timer == 0:
                self.right_swing_timer = (
                    self.swing_duration + self.swing_cooldown
                )

        elif self.state == "TRACK":
            if (
                ball.ball_position.x < 200
                and ball.ball_position.distance_to(
                    self.left_paddle.pivot_position
                )
                < 110
                and self.left_swing_timer == 0
            ):
                self.left_swing_timer = (
                    self.swing_duration + self.swing_cooldown
                )
            elif (
                ball.ball_position.x >= 200
                and ball.ball_position.distance_to(
                    self.right_paddle.pivot_position
                )
                < 110
                and self.right_swing_timer == 0
            ):
                self.right_swing_timer = (
                    self.swing_duration + self.swing_cooldown
                )

        ai_keys = {
            self.left_paddle.active_key: self.left_swing_timer
            > self.swing_cooldown,
            self.right_paddle.active_key: self.right_swing_timer
            > self.swing_cooldown,
        }

        self.left_paddle.update_Rotation(ai_keys)
        self.right_paddle.update_Rotation(ai_keys)