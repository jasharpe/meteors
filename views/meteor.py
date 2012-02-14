import pygame
from gameobject import GameObjectView

class MeteorView(GameObjectView):
  def __init__(self, model):
    GameObjectView.__init__(self, model)
    self.image = None
    self.init()

    self.bounding_rect = pygame.Rect(0, 0, 2 * self.model.radius, 2 * self.model.radius)
    self.rotatable = False

  def update_graphics(self):
    if self.image is None:
      size = self.tsc(2 * self.model.radius)
      self.image = pygame.Surface([size, size], pygame.SRCALPHA)
      pygame.draw.circle(self.image, self.model.color, (size / 2, size / 2), size / 2)
