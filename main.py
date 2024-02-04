import pygame
import sys
import random
import math
import threading
import asyncio
from pydub import AudioSegment
from pydub.playback import play

# Attempt to import the required modules
try:
    print("Verifying dependencies...")
    from pydub import AudioSegment
    from pydub.playback import play
except ImportError:
    print("Installing dependencies...")
    import os
    import subprocess
    subprocess.run(["pip", "install", "pydub"])
    os.system("sudo apt-get install ffmpeg")  # Install ffmpeg package

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BALL_RADIUS = 5
MIN_SIZE_FACTOR = 0.25  # Minimum size factor relative to normal size
MAX_SIZE_FACTOR = 2.5   # Maximum size factor relative to normal size
GRAVITY = 0.1
BOUNCINESS = 0.8  # Controls how much the velocity reverses when the balls collide with the boundaries (1 = perfectly elastic)

# Colors
WHITE = (255, 255, 255)
RAINBOW_COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0),
                  (0, 128, 0), (0, 0, 255), (75, 0, 130),
                  (238, 130, 238)]  # Rainbow colors in order: Red, Orange, Yellow, Green, Blue, Indigo, Violet

# Load sound effect
LAND_SOUND = AudioSegment.from_mp3("land_sound.mp3")

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice(RAINBOW_COLORS)  # Randomly select a color from the rainbow colors
        self.vx = random.uniform(-2, 2)  # Random initial velocity
        self.vy = random.uniform(-2, 2)  # Random initial velocity
        self.size_factor = 1.0
        self.is_picked = False
        self.prev_y = None  # Store previous y position

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(BALL_RADIUS * self.size_factor))

async def play_land_sound(speed):
    volume = min(speed / 10, 1.0)  # Adjust volume based on speed (max volume capped at 1.0)
    play(LAND_SOUND - volume)  # Play sound effect with adjusted volume

def update_balls(balls):
    for ball in balls:
        if ball.is_picked:
            ball.x, ball.y = pygame.mouse.get_pos()
        else:
            ball.vy += GRAVITY
            ball.prev_y = ball.y
            ball.x += ball.vx
            ball.y += ball.vy

            # Check for collisions with walls and ceiling
            if ball.x <= BALL_RADIUS or ball.x >= SCREEN_WIDTH - BALL_RADIUS:
                ball.vx *= -BOUNCINESS  # Reverse velocity with bounciness factor
                ball.y += random.uniform(-1, 1)  # Add slight variation on bounce
                ball.color = random.choice(RAINBOW_COLORS)  # Change color on bounce
            if ball.y <= BALL_RADIUS:
                ball.vy *= -BOUNCINESS  # Reverse velocity with bounciness factor
                ball.x += random.uniform(-1, 1)  # Add slight variation on bounce
                ball.color = random.choice(RAINBOW_COLORS)  # Change color on bounce
                if ball.prev_y is not None and ball.vy > 0:
                    asyncio.create_task(play_land_sound(abs(ball.vy)))  # Play sound effect when ball hits the floor

            # Check for collision with floor
            if ball.y >= SCREEN_HEIGHT - BALL_RADIUS:
                ball.vy *= -BOUNCINESS  # Reverse velocity with bounciness factor
                ball.x += random.uniform(-1, 1)  # Add slight variation on bounce
                ball.color = random.choice(RAINBOW_COLORS)  # Change color on bounce
                if ball.prev_y is not None and ball.vy < 0:
                    asyncio.create_task(play_land_sound(abs(ball.vy)))  # Play sound effect when ball hits the floor

            # Update ball size factor
            ball.size_factor = min(MAX_SIZE_FACTOR, ball.size_factor + 0.02)

async def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Physics Simulation")

    balls = []

    clock = pygame.time.Clock()

    is_holding_right = False
    spawn_timer = 0

    while True:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click to pick up a ball
                    for ball in balls:
                        if math.sqrt((event.pos[0] - ball.x) ** 2 + (event.pos[1] - ball.y) ** 2) < BALL_RADIUS:
                            ball.is_picked = True
                elif event.button == 3:  # Right click to spawn a ball
                    is_holding_right = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Release left click to stop dragging balls
                    for ball in balls:
                        ball.is_picked = False
                elif event.button == 3:  # Release right click to stop spawning balls
                    is_holding_right = False
                    spawn_timer = 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Press space to throw all balls upwards with more force
                    for ball in balls:
                        ball.vx = random.uniform(-5, 5)
                        ball.vy = random.uniform(-20, -15)  # Throw upwards with more force
                elif event.key == pygame.K_e:  # Press 'e' to clear all balls
                    balls.clear()

        if is_holding_right:
            balls.append(Ball(*pygame.mouse.get_pos()))
        
        update_balls(balls)

        for ball in balls:
            ball.draw(screen)

        pygame.display.flip()
        clock.tick(120)

if __name__ == "__main__":
    asyncio.run(main())
