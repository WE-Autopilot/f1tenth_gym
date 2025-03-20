
"""
DOES NOT WORK. Needs to be fixed BIG TIME.
Basically just a "dont move" controller.
"""

import pygame 

from weap_util.abstract_controller import AbstractController

SPEED_INCREMENT = 0.5
MAX_TURN = 0.2

class KeyboardController(AbstractController):
    def __init__(self):
        self.speed = 0.0
        self.steering = 0.0
        pygame.init()
        self.screen = pygame.display.set_mode((100, 100))  # Small window for key capture
        pygame.display.set_caption("Keyboard Controller")

    def startup(self) -> None:
        print("Keyboard controller started")

    def compute(self, obs: dict) -> tuple[2 | 3]:
        pygame.event.pump()  # Ensure event queue is updated

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            self.speed = 1 * SPEED_INCREMENT
        elif keys[pygame.K_2]:
            self.speed = 2 * SPEED_INCREMENT
        elif keys[pygame.K_3]:
            self.speed = 3 * SPEED_INCREMENT
        elif keys[pygame.K_4]:
            self.speed = 4 * SPEED_INCREMENT
        elif keys[pygame.K_5]:
            self.speed = 5 * SPEED_INCREMENT
        elif keys[pygame.K_6]:
            self.speed = 6 * SPEED_INCREMENT
        elif keys[pygame.K_7]:
            self.speed = 7 * SPEED_INCREMENT
        elif keys[pygame.K_7]:
            self.speed = 8 * SPEED_INCREMENT
        
        if keys[pygame.K_0]:
            self.speed = 0

        if keys[pygame.K_LEFT]:
            self.steering = MAX_TURN
        elif keys[pygame.K_RIGHT]:
            self.steering = -MAX_TURN
        else:
            self.steering = 0

        if keys[pygame.K_LSHIFT]:
            self.steering = 0

        return self.speed, self.steering, None

    def shutdown(self) -> None:
        pygame.quit()
        print("Keyboard controller shutting down")