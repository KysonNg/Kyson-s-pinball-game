import asyncio
import math
import pygame

from ai import P2_AI
from ball import Ball
from bumper import Bumper
from paddle import Paddle

pygame.init()

width, height = 400, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("CyberPin: Dual Arena Pinball")
clock = pygame.time.Clock()

BACKGROUND = (11, 11, 26)
PADDLE_COLOR = (238, 255, 0)
BALL_COLOR = (255, 0, 110)
BLOCK_COLOR = (80, 125, 190)
SCORE_COLOR = (255, 255, 255)

border = height // 2

score_p1 = 0
score_p2 = 0
WINNING_SCORE = 3
winner = None

font = pygame.font.SysFont("Consolas", 24, bold=True)
large_font = pygame.font.SysFont("Consolas", 36, bold=True)
controls_font = pygame.font.SysFont("Consolas", 16, bold=True)


def reset_ball(ball, winner_y_direction):
    ball.ball_position = pygame.Vector2(width // 2, border)
    ball.velocity = pygame.Vector2(0, 5 * winner_y_direction)


ball = Ball(200, 400, 0.25, BALL_COLOR)
reset_ball(ball, 1)

paddles = [
    Paddle(
        118,
        720,
        70,
        12,
        rest_angle=30,
        active_angle=-25,
        flip_speed=7,
        return_speed=5,
        color=PADDLE_COLOR,
        active_key=pygame.K_z,
    ),
    Paddle(
        282,
        720,
        70,
        12,
        rest_angle=150,
        active_angle=205,
        flip_speed=7,
        return_speed=5,
        color=PADDLE_COLOR,
        active_key=pygame.K_x,
    ),
    Paddle(
        118,
        80,
        70,
        12,
        rest_angle=-30,
        active_angle=25,
        flip_speed=7,
        return_speed=5,
        color=PADDLE_COLOR,
        active_key=pygame.K_n,
    ),
    Paddle(
        282,
        80,
        70,
        12,
        rest_angle=210,
        active_angle=155,
        flip_speed=7,
        return_speed=5,
        color=PADDLE_COLOR,
        active_key=pygame.K_m,
    ),
]

ai_p2 = P2_AI(paddles[2], paddles[3])

blocks = [
    pygame.Rect(0, 0, 118, 80),
    pygame.Rect(282, 0, 118, 80),
    pygame.Rect(0, 720, 118, 80),
    pygame.Rect(282, 720, 118, 80),
]

wedges = [
    [(0, 80), (118, 80), (0, 160)],
    [(282, 80), (400, 80), (400, 160)],
    [(0, 720), (118, 720), (0, 640)],
    [(282, 720), (400, 720), (400, 640)],
]

# Angled bumper positions to keep the center lane open
bumpers = [
    Bumper(200, 240, 16),
    Bumper(100, 180, 16),
    Bumper(300, 180, 16),
    Bumper(200, 500, 16),
    Bumper(90, 590, 16),
    Bumper(310, 590, 16),
]


def collide_block(ball, block):
    closest = pygame.Vector2(
        max(block.left, min(ball.ball_position.x, block.right)),
        max(block.top, min(ball.ball_position.y, block.bottom)),
    )
    offset = ball.ball_position - closest
    distance_squared = offset.length_squared()

    if distance_squared >= ball.radius * ball.radius:
        return

    if distance_squared > 0:
        distance = distance_squared**0.5
        normal = offset / distance
        ball.ball_position = closest + normal * ball.radius
    else:
        distances = (
            (ball.ball_position.x - block.left, pygame.Vector2(-1, 0)),
            (block.right - ball.ball_position.x, pygame.Vector2(1, 0)),
            (ball.ball_position.y - block.top, pygame.Vector2(0, -1)),
            (block.bottom - ball.ball_position.y, pygame.Vector2(0, 1)),
        )
        distance, normal = min(distances, key=lambda item: item[0])
        ball.ball_position += normal * (distance + ball.radius)

    normal_speed = ball.velocity.dot(normal)
    if normal_speed < 0:
        ball.velocity -= 2 * normal_speed * normal


def collide_wedge(ball, triangle):
    points = []
    for point in triangle:
        points.append(pygame.Vector2(point))

    position = ball.ball_position
    area = 0
    for i in range(3):
        area += (
            points[i].x * points[(i + 1) % 3].y
            - points[(i + 1) % 3].x * points[i].y
        )

    if area == 0:
        return

    inside = True
    closest_point = None
    closest_distance_squared = float("inf")
    nearest_outward = None

    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % 3]
        edge = end - start
        length_squared = edge.length_squared()
        if length_squared == 0:
            continue

        outward = pygame.Vector2(edge.y, -edge.x)
        if area < 0:
            outward = -outward
        outward = outward.normalize()

        if (position - start).dot(outward) > 0:
            inside = False

        fraction = max(
            0.0, min(1.0, (position - start).dot(edge) / length_squared)
        )
        point = start + fraction * edge
        distance_squared = (position - point).length_squared()

        if distance_squared < closest_distance_squared:
            closest_distance_squared = distance_squared
            closest_point = point
            nearest_outward = outward

    if closest_point is None:
        return

    if not inside and closest_distance_squared >= ball.radius * ball.radius:
        return

    offset = position - closest_point
    if inside or closest_distance_squared == 0:
        normal = nearest_outward
    else:
        normal = offset.normalize()

    ball.ball_position = closest_point + normal * ball.radius
    normal_speed = ball.velocity.dot(normal)
    if normal_speed < 0:
        ball.velocity -= 2 * normal_speed * normal


async def main():
    global score_p1, score_p2, winner

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if winner is not None and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    score_p1 = 0
                    score_p2 = 0
                    winner = None
                    reset_ball(ball, 1)

        if winner is None:
            keys = pygame.key.get_pressed()

            paddles[0].update_Rotation(keys)
            paddles[1].update_Rotation(keys)
            ai_p2.update(ball, height)

            for paddle in paddles:
                paddle.collide(ball)

            for bumper in bumpers:
                if ball.bumped(bumper):
                    bumper.color_change()

            for block in blocks:
                collide_block(ball, block)

            for wedge in wedges:
                collide_wedge(ball, wedge)

            ball.move(width, height)

            if ball.ball_position.y > height:
                score_p2 += 1
                if score_p2 >= WINNING_SCORE:
                    winner = "AI"
                else:
                    reset_ball(ball, winner_y_direction=1)
            elif ball.ball_position.y < 0:
                score_p1 += 1
                if score_p1 >= WINNING_SCORE:
                    winner = "Player 1"
                else:
                    reset_ball(ball, winner_y_direction=-1)

        # Render field elements
        screen.fill(BACKGROUND)
        pygame.draw.line(
            screen, (255, 255, 255), (0, border), (width, border), 2
        )

        for block in blocks:
            pygame.draw.rect(screen, BLOCK_COLOR, block, border_radius=2)
        for wedge in wedges:
            pygame.draw.polygon(screen, BLOCK_COLOR, wedge)
        for bumper in bumpers:
            bumper.draw(screen)
        for paddle in paddles:
            paddle.draw(screen)

        if winner is None:
            ball.draw(screen)

        # Render HUD elements
        p1_text = font.render(f"P1: {score_p1}", True, SCORE_COLOR)
        p2_text = font.render(f"P2: {score_p2}", True, SCORE_COLOR)
        ai_state_text = font.render(
            f"AI: {ai_p2.state}", True, (150, 150, 200)
        )

        screen.blit(p2_text, (15, 170))
        screen.blit(ai_state_text, (width - 130, 170))
        screen.blit(p1_text, (15, height - 195))

        left_control = controls_font.render("Z = LEFT", True, SCORE_COLOR)
        right_control = controls_font.render("X = RIGHT", True, SCORE_COLOR)
        screen.blit(left_control, left_control.get_rect(center=(118, 770)))
        screen.blit(right_control, right_control.get_rect(center=(282, 770)))

        # Render win screen overlay
        if winner is not None:
            result_message = "YOU LOSE!" if winner == "AI" else "YOU WIN!"
            result_text = large_font.render(
                result_message, True, PADDLE_COLOR
            )
            restart_text = font.render(
                "Press SPACE to Restart", True, SCORE_COLOR
            )
            screen.blit(
                result_text,
                result_text.get_rect(center=(width // 2, border - 20)),
            )
            screen.blit(
                restart_text,
                restart_text.get_rect(center=(width // 2, border + 30)),
            )

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())