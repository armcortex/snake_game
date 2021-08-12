import sys
import time
import random
import copy
import pygame as pg

# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 20


# Colors (R, G, B)
BLACK = pg.Color(0, 0, 0)
WHITE = pg.Color(255, 255, 255)
RED   = pg.Color(255, 0, 0)
GREEN = pg.Color(0, 255, 0)
BLUE  = pg.Color(0, 0, 255)

FRAME_WIDTH  = 640
FRAME_HEIGHT = 480
SNAKE_BLOCK  = 10
SNAKE_LEN    = 5

EAT_SUCCESS =  True
EAT_FAILURE =  False

MOVE_UP    = 0
MOVE_RIGHT = 1
MOVE_LEFT  = 2
MOVE_DOWN  = 3


class POINT:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class SNAKE:
    def __init__(self, init_pos):
        self.body = [init_pos]
        
        # Generate init body
        for x in range(SNAKE_BLOCK, SNAKE_BLOCK*(SNAKE_LEN+1), SNAKE_BLOCK):
            self.__grow(POINT(init_pos.x+x, init_pos.y))

    def __grow(self, p):
        self.body.append(p)

    def __shrink(self):
        self.body.pop()

    def position(self):
        return copy.deepcopy(self.body[0])

    def moving_and_eating(self, head, food):
        self.body.insert(0, head)
        return self.__eating(food)

    def moving(self, head):
        self.body.insert(0, head)
        self.__shrink()

    def __eating(self, food):
        curr_pos = self.position()
        if food.x == curr_pos.x and food.y == curr_pos.y:
            return EAT_SUCCESS
        else:
            self.__shrink()
            return EAT_FAILURE

class GAME:
    def __init__(self, width, height):
        pg.init()
        self.width = width
        self.height = height
        self.score = 0
        self.direction = MOVE_LEFT
        self.food_eaten = EAT_SUCCESS
        self.food = POINT(0, 0)
        self.generate_food()
        
        pg.display.set_caption('Snake Eater')
        self.window = pg.display.set_mode((self.width, self.height))
        self.window.fill(BLACK)

    def show_snake(self, snake):
        self.window.fill(BLACK)
        for p in snake.body:
            pg.draw.rect(self.window, GREEN, pg.Rect(p.x, p.y, SNAKE_BLOCK, SNAKE_BLOCK))

    def __screen_text(self, text, font, size, color, pos):
        font = pg.font.SysFont(font, size)
        text = font.render(text, True, color)
        text_rect = text.get_rect()
        text_rect.midtop = (pos[0], pos[1])
        self.window.blit(text, text_rect)

    def welcome(self):
        self.__screen_text("Let's play a game", 'times new roman', \
                            90, RED, (self.width//2, self.height//4))

        self.__screen_text("Press Enter", 'times new roman', \
                            40, RED, (self.width//2, self.height//1.25))
        pg.display.update()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        return

    def over(self):
        self.__screen_text('YOU DIED!', 'times new roman', \
                            90, RED, (self.width//2, self.height//4))

        self.show_score(0, RED, 'times', 20)
        pg.display.flip()
        time.sleep(3)
        pg.quit()
        sys.exit()

    def show_score(self, choice, color, font, size):
        if choice == 1:
            pos = (self.width/10, 15)
        else:
            pos = (self.width/2, self.height/1.25)
        
        text = f'Score : {self.score}'
        self.__screen_text(text, 'times', size, RED, pos)

    def check_keys(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                self.direction = self.key_direction(event)
            else:
                pass

    def key_direction(self, event):
        # W -> Up; S -> Down; A -> Left; D -> Right
        if event.key == pg.K_UP or event.key == ord('w'):
            if self.direction == MOVE_DOWN:
                return MOVE_DOWN
            else:
                return MOVE_UP
        elif event.key == pg.K_DOWN or event.key == ord('s'):
            if self.direction == MOVE_UP:
                return MOVE_UP
            else:
                return MOVE_DOWN
        elif event.key == pg.K_LEFT or event.key == ord('a'):
            if self.direction == MOVE_RIGHT:
                return MOVE_RIGHT
            else:
                return MOVE_LEFT
        elif event.key == pg.K_RIGHT or event.key == ord('d'):
            if self.direction == MOVE_LEFT:
                return MOVE_LEFT
            else:
                return MOVE_RIGHT
        # Esc -> Create event to quit the game
        elif event.key == pg.K_ESCAPE:
            pg.event.post(pg.event.Event(pg.QUIT))
        else:
            pass

    def moving_and_eating(self, snake):
        curr_pos = snake.position()
        
        if self.direction == MOVE_UP:
            curr_pos.y -= SNAKE_BLOCK
        elif self.direction == MOVE_DOWN:
            curr_pos.y += SNAKE_BLOCK
        elif self.direction == MOVE_LEFT:
            curr_pos.x -= SNAKE_BLOCK
        elif self.direction == MOVE_RIGHT:
            curr_pos.x += SNAKE_BLOCK
        else:
            pass
            # raise ValueError('Wrong command: {}'.format(self.direction))

        self.food_eaten = snake.moving_and_eating(curr_pos, self.food)

        if self.food_eaten == EAT_SUCCESS:
            self.score += 1

    def generate_food(self):
        if self.food_eaten == EAT_SUCCESS:
            self.food.x = random.randrange(0, self.width, SNAKE_BLOCK)
            self.food.y = random.randrange(0, self.height, SNAKE_BLOCK)
            self.food_eaten = EAT_FAILURE

    def show_food(self):
        pg.draw.rect(self.window, WHITE, pg.Rect(self.food.x, self.food.y, SNAKE_BLOCK, SNAKE_BLOCK))

    def check_bound(self, snake):
        curr_pos = snake.position()

        if curr_pos.x < 0 or curr_pos.x > self.width:
            self.over()
        elif curr_pos.y < 0 or curr_pos.y > self.height:
            self.over()
        else:
            pass

    def check_suicide(self, snake):
        curr_pos = snake.position()

        for p in snake.body[1:]:
            if curr_pos.x == p.x and curr_pos.y == p.y:
                self.over()


def main():
    snake = SNAKE(POINT(FRAME_WIDTH//2, FRAME_HEIGHT//2))
    game = GAME(FRAME_WIDTH, FRAME_HEIGHT)
    game.show_snake(snake)
    game.welcome()

    fps = pg.time.Clock()
    while True:
        game.generate_food()
        game.check_keys()
        game.moving_and_eating(snake)
        game.show_snake(snake)
        game.show_food()
        
        game.check_suicide(snake)
        game.check_bound(snake)

        game.show_score(1, WHITE, 'consolas', 20)
        pg.display.update()
        fps.tick(DIFFICULTY)


if __name__ == '__main__':
    main()
