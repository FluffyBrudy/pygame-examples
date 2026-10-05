import sys

import pygame

from src.scene import LevelScene
from src.scene.base import SceneManager
from src.settings import PROJECT_PATH


class Game:
    WIDTH = 1280
    HEIGHT = 720
    FPS = 60
    BG_COLOR = (30, 30, 30)
    TITLE = "Strange Forest"

    def __init__(self) -> None:
        self.running = True
        self._init()

    def _init(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(self.TITLE)
        self.clock = pygame.time.Clock()
        self.time_scale = 1.0

        self.map_path = PROJECT_PATH / "data/maps"
        self.levels = [mapfile for mapfile in self.map_path.iterdir() if mapfile.suffix == ".json"]
        self.pointer = int(sys.argv[1]) % len(self.levels) if (len(sys.argv) > 1 and sys.argv[1].isnumeric()) else 0

        self.scene_manager = SceneManager()
        self.scene_manager.change_scene(
            LevelScene(),
            level_path=self.levels[self.pointer],
        )

    def handle_event(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt: float) -> None:
        self.scene_manager.update(dt)
        scene = self.scene_manager.current_scene
        if isinstance(scene, LevelScene) and scene.can_transition():
            level_pointer = self.pointer + 1
            if level_pointer >= len(self.levels):
                level_pointer = 0
            self.pointer = level_pointer
            self.scene_manager.change_scene(
                LevelScene(),
                level_path=self.levels[self.pointer],
            )

    def render(self) -> None:
        self.screen.fill(self.BG_COLOR)
        self.scene_manager.render(self.screen)
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0

            self.handle_event()

            self.update(dt * self.time_scale)
            self.render()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
