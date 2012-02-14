from gameobject import GameObjectModel

class SheepModel(GameObjectModel):
  def __init__(self, meteor_model, position):
    GameObjectModel.__init__(self, position)
