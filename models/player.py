import math

from geometry import Vector
from gameobject import GameObjectModel
import constants

class PlayerModel(GameObjectModel):
  def __init__(self, meteor_model, position):
    GameObjectModel.__init__(self, position)

    self.meteor_model = meteor_model

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
    return (self.position - self.meteor_model.position).length() - constants.PLAYER_HEIGHT / 2 - self.meteor_model.radius

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
      self.position = self.meteor_model.position.translate(self.up_direction() * (self.meteor_model.radius + constants.PLAYER_HEIGHT / 2))
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
