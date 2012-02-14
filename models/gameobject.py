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
