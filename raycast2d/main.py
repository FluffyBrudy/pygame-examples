import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class Raycast:
    _game_loop = True

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._game_loop = False

    def update(self):
        pass

    def render(self):
        self.screen.fill((0, 0, 0))
        pygame.display.update((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def run(self):
        while self._game_loop:
            self.handle_event()
            self.update()
            self.render()
        pygame.quit()

if __name__ == "__main__":
    raycast = Raycast()
    raycast.run()
