import pygame, os, math, constants
from gameobject import GameObjectView

class PlayerView(GameObjectView):
  def __init__(self, model):
    GameObjectView.__init__(self, model)

    #self.original = pygame.Surface([self.tsc(self.model.height), self.tsc(self.model.width)], pygame.SRCALPHA)
    #self.original.fill(self.model.color)
    self.originals = {}
    for image in ["standing3", "jumping", "running2", "running3"]:
      self.originals[image + "_right"] = pygame.transform.rotate(pygame.image.load(os.path.join(image + ".png")).convert_alpha(), 90)
      self.originals[image + "_left"] = pygame.transform.flip(pygame.transform.rotate(pygame.image.load(os.path.join(image + ".png")).convert_alpha(), 90), False, True)

    self.bounding_rect = pygame.Rect(0, 0, 2 * max(constants.PLAYER_HEIGHT, constants.PLAYER_WIDTH), 2 * max(constants.PLAYER_HEIGHT, constants.PLAYER_WIDTH))

    self.init()

  def update_graphics(self):
    #self.image = pygame.transform.rotate(self.original, self.model.rotation * (180.0 / math.pi))
    postfix = "_" + self.model.last_direction

    if self.model.is_jumping():
      self.image = self.originals["jumping" + postfix]
      self.rotation_cache_key = "jumping" + postfix
    elif self.model.moved:
      number = 2 if self.model.time % constants.PLAYER_RUNNING_PERIOD > constants.PLAYER_RUNNING_PERIOD / 2 else 3

      self.image = self.originals["running" + str(number) + postfix]
      self.rotation_cache_key = "running" + str(number) + postfix
    else:
      self.image = self.originals["standing3" + postfix]
      self.rotation_cache_key = "standing3" + postfix
