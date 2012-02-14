import pygame
from gameobject import GameObjectView

class SheepView(GameObjectView):
  def __init__(self, model):
    GameObjectView.__init__(self, model)

    self.original = pygame.transform.rotate(pygame.image.load(os.path.join("sheep.png")).convert_alpha(), 90)

    self.init()

  def update_graphics(self):
    self.image = self.original
