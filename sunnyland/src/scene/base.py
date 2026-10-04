from abc import ABC, abstractmethod

import pygame


class Scene(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def enter(self) -> None:
        pass

    @abstractmethod
    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.Event):
        pass

    def load(self, **kwargs):
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface):
        pass


class SceneManager:
    def __init__(self) -> None:
        self.current_scene: Scene | None = None

    def change_scene(self, scene: Scene, **kwargs):
        if self.current_scene is not None:
            self.current_scene.exit()

        scene.load(**kwargs)
        self.current_scene = scene
        self.current_scene.enter()

    def update(self, dt: float):
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def render(self, screen: pygame.Surface):
        if self.current_scene is not None:
            self.current_scene.render(screen)
