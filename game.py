import pygame, constants, itertools, math, os
from pygame.sprite import Group
from geometry import Point, ORIGIN, Vector
from models import GameObjectModel, MeteorModel, SheepModel, PlayerModel
from views import GameObjectView, MeteorView, SheepView, PlayerView

def create_pair(model_type, view_type, *args):
  model = model_type(*args)
  return (model, view_type(model))

class Game(object):
  def __init__(self, screen_size):
    self.screen_position = Point(0, 0)
    self.zoom = 1
    self.screen_size = screen_size

    self.meteor_models = []
    self.meteor_views = []
    for (position, radius, color) in [(Point(0, 0), 5, pygame.color.Color(100, 100, 100)), (Point(10, 5), 3, pygame.color.Color(100, 100, 150)), (Point(15, 16), 6, pygame.color.Color(150, 100, 100))]:
      (meteor_model, meteor_view) = create_pair(MeteorModel, MeteorView, position, radius, color)
      self.meteor_models.append(meteor_model)
      self.meteor_views.append(meteor_view)

    self.player_models = []
    self.player_views = []
    (player_model, player_view) = create_pair(PlayerModel, PlayerView, self.meteor_models[0], Point(1, -6))
    self.player = player_model
    self.player_models.append(player_model)
    self.player_views.append(player_view)

    self.should_quit = False

  def quit(self):
    self.should_quit = True

  def update(self, delta, pygame_events, pressed, mouse):
    if self.should_quit:
      return True
    
    for event in pygame_events:
      if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        self.player.jump()

    if pressed[pygame.K_LEFT]:
      self.player.move_radially_left(constants.PLAYER_SPEED * (delta / 1000.0))
    elif pressed[pygame.K_RIGHT]:
      self.player.move_radially_right(constants.PLAYER_SPEED * (delta / 1000.0))

    for model in itertools.chain(self.meteor_models, self.player_models):
      model.update(delta, self)

    self.screen_position = self.player.position
    self.screen_rotation = 0
    #self.screen_rotation = self.player.rotation + math.pi / 2

  def draw(self, screen):
    screen.fill(pygame.color.Color(15, 15, 15))

    center = Point(float(self.screen_size[0]) / constants.PIXELS_PER_UNIT / 2, float(self.screen_size[1]) / constants.PIXELS_PER_UNIT / 2)
    drawn = 0
    for view in itertools.chain(self.meteor_views, self.player_views):
      if view.draw(screen, ORIGIN - self.screen_position, center, self.screen_rotation):
        drawn += 1
