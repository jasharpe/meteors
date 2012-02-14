import pygame, math, constants
from geometry import Point, ORIGIN
from collections import defaultdict

class GameObjectView(pygame.sprite.Sprite):
  def __init__(self, model):
    self.model = model
    self.model.register_listener(self)
    self.rotation_cache = defaultdict(dict)
    self.rotation_cache_key = "default"
    self.rotatable = True

  def init(self):
    self.update_graphics()

  # to screen coordinates
  def tsc(self, x):
    if isinstance(x, Point):
      return Point(int(round(self.tsc(x.x))), int(round(self.tsc(x.y))))
    elif isinstance(x, pygame.Rect):
      rect = pygame.Rect(x)
      rect.w *= constants.PIXELS_PER_UNIT
      rect.h *= constants.PIXELS_PER_UNIT
      return rect
    else:
      return int(round(x * constants.PIXELS_PER_UNIT))

  def notify(self):
    pass
    #self.update_graphics()

  def update_graphics(self):
    raise Exception("Implement update_graphics()")

  def draw(self, screen, offset, center, rotation):
    view_rotation = 0
    try:
      view_rotation = self.model.rotation
    except:
      pass
    
    position = self.model.position.translate(offset).rotate_about(rotation, Point(0, 0)).translate(center - ORIGIN)

    screen_rect = self.tsc(self.bounding_rect)
    screen_rect.center = self.tsc(position)

    ret = False
    if screen_rect.colliderect(screen.get_rect()):
      self.update_graphics()
      if self.rotatable:
        total_rotation = -(rotation - view_rotation) * 180.0 / math.pi
        cache_rotation = int(round(total_rotation * constants.ROTATION_CACHE_RESOLUTION / (360.0))) % constants.ROTATION_CACHE_RESOLUTION
        if cache_rotation in self.rotation_cache[self.rotation_cache_key]:
          to_blit = self.rotation_cache[self.rotation_cache_key][cache_rotation]
        else:
          to_blit = pygame.transform.rotate(self.image, total_rotation)
          self.rotation_cache[self.rotation_cache_key][cache_rotation] = to_blit
      else:
        to_blit = self.image
      screen.blit(to_blit, to_blit.get_rect(center=self.tsc(position)))
      ret = True
    return ret
