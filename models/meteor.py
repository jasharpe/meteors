from gameobject import GameObjectModel
from geometry import Vector

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
