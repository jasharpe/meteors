import pygame, constants, itertools, math, os
from collections import defaultdict
from pygame.sprite import Group
from geometry import Point, ORIGIN, Vector

class GameObjectModel(object):
  def __init__(self, position):
    self.position = position
    self.listeners = []

  def register_listener(self, listener):
    self.listeners.append(listener)

  def notify(self):
    for listener in self.listeners:
      listener.notify()

  def update(self, delta, game):
    pass

class MeteorModel(GameObjectModel):
  def __init__(self, position, radius, color):
    GameObjectModel.__init__(self, position)

    self.radius = radius
    self.color = color

  def get_position(self, radial_position, height):
    return self.position.translate(Vector(radial_position).normalize() * (self.radius + height))

  def get_height(self, position):
    return (position - self.position).length() - self.radius

  def get_radial_position(self, position):
    return (position - self.position).angle()

class PlayerModel(GameObjectModel):
  def __init__(self, meteor_model, position, width, height, color):
    GameObjectModel.__init__(self, position)

    self.meteor_model = meteor_model
    self.width = width
    self.height = height
    self.color = color

    self.rotation = self.target_angle()
    self.velocity = Vector(0, 0)
    self.can_switch = True

    self.last_position = self.position
    self.moved = False
    self.last_direction = "right"
    self.time = 0

  def target_angle(self):
    angle = math.pi - (self.position - self.meteor_model.position).angle()
    if angle < 0:
      angle += 2 * math.pi
    return angle

  def move_radially_left(self, arc_distance):
    self.move_radially_right(-arc_distance)
    self.last_direction = "left"
    self.moved = True

  def move_radially_right(self, arc_distance):
    # arc = radius * angle
    angle = arc_distance / self.meteor_model.radius
    self.position = self.position.rotate_about(angle, self.meteor_model.position)
    self.last_direction = "right"
    self.moved = True

  def up_direction(self):
    return (self.position - self.meteor_model.position).normalize()

  def height_off_ground(self):
    return (self.position - self.meteor_model.position).length() - self.height / 2 - self.meteor_model.radius

  def is_jumping(self):
    return self.height_off_ground() > 0.01

  def on_ground(self):
    return self.height_off_ground() < 0.001

  def jump(self):
    if self.on_ground():
      self.velocity = self.up_direction() * constants.PLAYER_JUMP_VELOCITY

  # Returns the time (assuming no movement) until the player lands
  def time_until_landing(self):
    x = -self.height_off_ground()
    v_0 = -self.velocity.length()
    a = constants.PLAYER_JUMP_ACCELERATION
    # want t
    # 0 = a/2 * t^2 + v_0 * t - x
    # t = (-v_0 +- sqrt(v_0^2 + 2 * a * x)) / a
    desc = v_0 ** 2 + 2 * a * x
    # this is to guard against stupid things like -3e-19
    if desc < 0 and desc > -0.0001:
      desc = 0
    return (-v_0 - math.sqrt(desc)) / a

  def adjust_rotation(self, delta):
    point = self.meteor_model.position

    t_a = self.target_angle()
    c_a = self.rotation
    difference = t_a - c_a
    while difference < -math.pi:
      difference += 2 * math.pi
    while difference > math.pi:
      difference -= 2 * math.pi

    if abs(difference) < constants.PLAYER_ROTATION_SPEED * (delta / 1000.0):
      self.rotation = self.target_angle()
    else:
      t = self.time_until_landing()
      if t < 0.0001:
        self.rotation += difference
      else:
        self.rotation += difference * (delta / 1000.0) / t

  def rotate(self, rotation):
    self.rotation += rotation
    while self.rotation > 2 * math.pi:
      self.rotation -= 2 * math.pi
    while self.rotation < 0:
      self.rotation += 2 * math.pi

  def update(self, delta, game):
    self.time += delta
    self.position = self.position.translate(self.velocity * (delta / 1000.0))
    self.velocity = self.velocity + self.up_direction() * constants.PLAYER_JUMP_ACCELERATION * (delta / 1000.0)
    if self.on_ground():
      self.position = self.meteor_model.position.translate(self.up_direction() * (self.meteor_model.radius + self.height / 2))
      self.velocity = Vector(0, 0)
      self.can_switch = True

    self.adjust_rotation(delta)

    if self.can_switch:
      def meteor_model_key(meteor_model):
        return meteor_model.get_height(self.position)

      new_meteor_model = min(game.meteor_models, key=meteor_model_key)

      if new_meteor_model != self.meteor_model:
        self.meteor_model = new_meteor_model
        self.can_switch = False

    self.moved = ((self.last_position - self.position).length() > 0.01)
    self.last_position = self.position

    self.notify()

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

class PlayerView(GameObjectView):
  def __init__(self, model):
    GameObjectView.__init__(self, model)

    #self.original = pygame.Surface([self.tsc(self.model.height), self.tsc(self.model.width)], pygame.SRCALPHA)
    #self.original.fill(self.model.color)
    self.originals = {}
    for image in ["standing3", "jumping", "running2", "running3"]:
      self.originals[image + "_right"] = pygame.transform.rotate(pygame.image.load(os.path.join(image + ".png")).convert_alpha(), 90)
      self.originals[image + "_left"] = pygame.transform.flip(pygame.transform.rotate(pygame.image.load(os.path.join(image + ".png")).convert_alpha(), 90), False, True)

    self.bounding_rect = pygame.Rect(0, 0, 2 * max(self.model.height, self.model.width), 2 * max(self.model.width, self.model.height))

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
    (player_model, player_view) = create_pair(PlayerModel, PlayerView, self.meteor_models[0], Point(1, -6), 0.5, 1.0, pygame.color.Color(50, 200, 50))
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
    screen.fill(pygame.color.Color(0, 0, 0))

    center = Point(float(self.screen_size[0]) / constants.PIXELS_PER_UNIT / 2, float(self.screen_size[1]) / constants.PIXELS_PER_UNIT / 2)
    drawn = 0
    for view in itertools.chain(self.meteor_views, self.player_views):
      if view.draw(screen, ORIGIN - self.screen_position, center, self.screen_rotation):
        drawn += 1
