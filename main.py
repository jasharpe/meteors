import pygame, sys, constants
from game import Game

FRAME_MS = 11

class Main(object):
  def set_caption(self, caption):
    pygame.display.set_caption(caption)

  def main(self, argv):
    try:
      self.handle_args(argv)
    except:
      return 2

    pygame.mixer.pre_init(frequency=22050, size=-16, channels=16, buffer=512)
    pygame.init()
    screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
    
    self.set_caption(self.get_caption())

    game = self.get_game()

    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    frames = 0
    bad_frames = 0
    exit_program = False
    while True:
      clock.tick(91)

      frame_start_time = pygame.time.get_ticks()
      delta = FRAME_MS

      # event handling
      events = pygame.event.get()
      for event in events:
        if event.type == pygame.QUIT:
          exit_program = True
        elif event.type == pygame.VIDEORESIZE:
          self.screen_size = event.size
          screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
          game.screen_size = self.screen_size

      if exit_program:
        break
    
      pressed = pygame.key.get_pressed()
      mouse = pygame.mouse.get_pos()

      if game.update(delta, events, pressed, mouse):
        break

      # draw
      screen.fill((0, 0, 0))
      game.draw(screen) 
      pygame.display.flip()

      frame_end_time = pygame.time.get_ticks()
      frame_time = (frame_end_time - frame_start_time)
      if frame_time > FRAME_MS:
        bad_frames += 1
        print "Last frame took %d" % (frame_time)
      
      frames += 1

    total_time = (pygame.time.get_ticks() - start_time)
    pygame.quit()
    return 0

class GameMain(Main):
  def __init__(self):
    Main.__init__(self)

    self.screen_size = (constants.DEFAULT_RESOLUTION_X, constants.DEFAULT_RESOLUTION_Y)

  def get_caption(self):
    return "Meteors"

  def get_game(self):
    return Game(self.screen_size)

  def usage(self):
    print ''''''

  def handle_args(self, argv):
    pass

def main(argv):
  return GameMain().main(argv)

if __name__ == "__main__":
  sys.exit(main(sys.argv))
