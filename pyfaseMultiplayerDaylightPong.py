# DaylightPong Developer : Hamdy Abou El Anein
# pyfase Creator and Multiplayer Implementation: Joaci Morais

import random
import pygame
from pygame import *
from pyfase import *
from threading import Event

"""
requirements:

python3 -m pip install pyfase pyzmq pygame 

PLAY OVER NETWORK:
to play over network with player2, edit 'pyfase_sender' and 'pyfase_receiver' variables with the IP or DNS of 
player1. Player1 is the Host

pyfase_sender = 'tcp://<player1 ip>:8000'
pyfase_receiver = 'tcp://<player1 ip>:8001'
"""

pyfase_sender = 'tcp://127.0.0.1:8000'
pyfase_receiver = 'tcp://127.0.0.1:8001'


class MultiplayerDaylightPong(MicroService):
    def __init__(self, host):
        super(MultiplayerDaylightPong, self).__init__(self,
                                                      sender_endpoint=pyfase_sender,
                                                      receiver_endpoint=pyfase_receiver)
        self.host = host
        self.WHITE = (255, 255, 255)
        self.ORANGE = (255, 140, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.WIDTH = 600
        self.HEIGHT = 400
        self.BALL_RADIUS = 10
        self.PAD_WIDTH = 8
        self.PAD_HEIGHT = 80
        self.HALF_PAD_WIDTH = self.PAD_WIDTH // 2
        self.HALF_PAD_HEIGHT = self.PAD_HEIGHT // 2
        self.X = 0
        self.Y = 1
        self.ball_pos = [0, 0]
        self.ball_vel = [0, 0]
        self.ball_acceleration = 1.05
        self.paddle1_vel = 0
        self.paddle2_vel = 0
        self.l_score = 0
        self.r_score = 0
        self.paddle1_pos = [0.0, 0.0]
        self.paddle2_pos = [0.0, 0.0]
        self.paddle1_vel = 0.0
        self.paddle2_vel = 0.0
        self.l_score = 0.0
        self.r_score = 0.0
        self.score1 = 0
        self.score2 = 0
        self.fps = 0.0
        self.window = None
        self.delta_time_actions = 0.0
        self.game_event = Event()
        if self.host:
            self.start_task('pyfase_broker', (self,))
            self.text_status = "WAITING FOR PLAYER 2"
        else:
            self.text_status = "WAITING FOR PLAYER 1"
        self.start_task('game_task', (self,))
        self.game_clock = None
        self.paused = True
        self.first_run = True
        self.winner = ''

    def ball_init(self, right):
        self.ball_pos = [self.WIDTH // 2, self.HEIGHT // 2]
        horz = random.randrange(2, 4)
        vert = random.randrange(1, 3)
        if right is False:
            horz = -horz
        self.ball_vel = [horz, -vert]

    def init(self):
        self.paddle1_pos = [self.HALF_PAD_WIDTH - 1, self.HEIGHT // 2]
        self.paddle2_pos = [self.WIDTH + 1 - self.HALF_PAD_WIDTH, self.HEIGHT // 2]
        self.l_score = 0
        self.r_score = 0
        if random.randrange(0, 2) == 0:
            self.ball_init(True)
        else:
            self.ball_init(False)

    def draw(self, canvas):
        canvas.fill(self.BLACK)
        pygame.draw.line(canvas, self.WHITE, [self.WIDTH // 2, 0], [self.WIDTH // 2, self.HEIGHT], 1)
        pygame.draw.line(canvas, self.WHITE, [self.PAD_WIDTH, 0], [self.PAD_WIDTH, self.HEIGHT], 1)
        pygame.draw.line(
            canvas, self.WHITE, [self.WIDTH - self.PAD_WIDTH, 0], [self.WIDTH - self.PAD_WIDTH, self.HEIGHT], 1
        )
        pygame.draw.circle(canvas, self.WHITE, [self.WIDTH // 2, self.HEIGHT // 2], 70, 1)

        if self.HALF_PAD_HEIGHT < self.paddle1_pos[1] < self.HEIGHT - self.HALF_PAD_HEIGHT:
            self.paddle1_pos[self.Y] += self.paddle1_vel
        elif self.paddle1_pos[self.Y] == self.HALF_PAD_HEIGHT and self.paddle1_vel > 0:
            self.paddle1_pos[self.Y] += self.paddle1_vel
        elif self.paddle1_pos[self.Y] == self.HEIGHT - self.HALF_PAD_HEIGHT and self.paddle1_vel < 0:
            self.paddle1_pos[self.Y] += self.paddle1_vel

        if self.HALF_PAD_HEIGHT < self.paddle2_pos[1] < self.HEIGHT - self.HALF_PAD_HEIGHT:
            self.paddle2_pos[self.Y] += self.paddle2_vel
        elif self.paddle2_pos[self.Y] == self.HALF_PAD_HEIGHT and self.paddle2_vel > 0:
            self.paddle2_pos[self.Y] += self.paddle2_vel
        elif self.paddle2_pos[self.Y] == self.HEIGHT - self.HALF_PAD_HEIGHT and self.paddle2_vel < 0:
            self.paddle2_pos[self.Y] += self.paddle2_vel

        self.ball_pos[self.X] += int(self.ball_vel[self.X])
        self.ball_pos[self.Y] += int(self.ball_vel[self.Y])

        pygame.draw.circle(canvas, self.ORANGE, self.ball_pos, self.BALL_RADIUS, 0)
        pygame.draw.polygon(
            canvas,
            self.GREEN,
            [
                [self.paddle1_pos[self.X] - self.HALF_PAD_WIDTH, self.paddle1_pos[self.Y] - self.HALF_PAD_HEIGHT],
                [self.paddle1_pos[self.X] - self.HALF_PAD_WIDTH, self.paddle1_pos[self.Y] + self.HALF_PAD_HEIGHT],
                [self.paddle1_pos[self.X] + self.HALF_PAD_WIDTH, self.paddle1_pos[self.Y] + self.HALF_PAD_HEIGHT],
                [self.paddle1_pos[self.X] + self.HALF_PAD_WIDTH, self.paddle1_pos[self.Y] - self.HALF_PAD_HEIGHT],
            ],
            0,
        )
        pygame.draw.polygon(
            canvas,
            self.BLUE,
            [
                [self.paddle2_pos[self.X] - self.HALF_PAD_WIDTH, self.paddle2_pos[self.Y] - self.HALF_PAD_HEIGHT],
                [self.paddle2_pos[self.X] - self.HALF_PAD_WIDTH, self.paddle2_pos[self.Y] + self.HALF_PAD_HEIGHT],
                [self.paddle2_pos[self.X] + self.HALF_PAD_WIDTH, self.paddle2_pos[self.Y] + self.HALF_PAD_HEIGHT],
                [self.paddle2_pos[self.X] + self.HALF_PAD_WIDTH, self.paddle2_pos[self.Y] - self.HALF_PAD_HEIGHT],
            ],
            0,
        )

        if int(self.ball_pos[self.Y]) <= self.BALL_RADIUS:
            self.ball_vel[self.Y] = -self.ball_vel[self.Y]
            self.request_game_sync_ball_data()
        if int(self.ball_pos[self.Y]) >= self.HEIGHT + 1 - self.BALL_RADIUS:
            self.ball_vel[self.Y] = -self.ball_vel[self.Y]
            self.request_game_sync_ball_data()

        if int(self.ball_pos[self.X]) <= self.BALL_RADIUS + self.PAD_WIDTH and int(self.ball_pos[self.Y]) in range(
                int(self.paddle1_pos[self.Y]) - self.HALF_PAD_HEIGHT, int(self.paddle1_pos[self.Y]) + self.HALF_PAD_HEIGHT, 1
        ):
            self.ball_vel[self.X] = -self.ball_vel[self.X]
            self.ball_vel[self.X] *= self.ball_acceleration
            self.ball_vel[self.Y] *= self.ball_acceleration
            self.request_game_sync_ball_data()
        elif int(self.ball_pos[self.X]) <= self.BALL_RADIUS + self.PAD_WIDTH:
            self.r_score += 1
            self.ball_init(True)
            self.paused = True
            self.winner = 'PLAYER 2'
            self.request_game_sync_paused_data()
            self.request_game_sync_score_data()
            self.request_game_sync_ball_data()

        if int(self.ball_pos[self.X]) >= self.WIDTH + 1 - self.BALL_RADIUS - self.PAD_WIDTH and int(
                self.ball_pos[self.Y]
        ) in range(int(self.paddle2_pos[self.Y]) - self.HALF_PAD_HEIGHT, int(self.paddle2_pos[self.Y]) + self.HALF_PAD_HEIGHT, 1):
            self.ball_vel[self.X] = -self.ball_vel[self.X]
            self.ball_vel[self.X] *= self.ball_acceleration
            self.ball_vel[self.Y] *= self.ball_acceleration
            self.request_game_sync_ball_data()
        elif int(self.ball_pos[self.X]) >= self.WIDTH + 1 - self.BALL_RADIUS - self.PAD_WIDTH:
            self.l_score += 1
            self.ball_init(False)
            self.paused = True
            self.winner = 'PLAYER 1'
            self.request_game_sync_paused_data()
            self.request_game_sync_score_data()
            self.request_game_sync_ball_data()

        myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
        label2 = myfont1.render(self.text_status, True, (255, 255, 0))
        canvas.blit(label2, (50, 5))

        myfont2 = pygame.font.SysFont("Comic Sans MS", 20)
        label2 = myfont2.render("SCORE: " + str(self.l_score), True, (255, 255, 0))
        canvas.blit(label2, (50, 20))

        myfont3 = pygame.font.SysFont("Comic Sans MS", 20)
        label3 = myfont3.render("SCORE: " + str(self.r_score), True, (255, 255, 0))
        canvas.blit(label3, (470, 20))

    def keydown(self, event):
        if self.host:
            if event.key == K_UP:
                self.paddle1_vel = -8
            elif event.key == K_DOWN:
                self.paddle1_vel = 8
        else:
            if event.key == K_UP:
                self.paddle2_vel = -8
            elif event.key == K_DOWN:
                self.paddle2_vel = 8
        if event.key == K_SPACE:
            self.request_action('start_game', '')

    def keyup(self, event):
        if self.host:
            if event.key in (K_UP, K_DOWN):
                self.paddle1_vel = 0
        else:
            if event.key in (K_UP, K_DOWN):
                self.paddle2_vel = 0
        self.request_game_sync_paddle_data()

    def input_handler(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                self.keydown(event)
            elif event.type == KEYUP:
                self.keyup(event)
            elif event.type == QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
        if self.host:
            if self.paddle1_vel != 0:
                self.request_game_sync_paddle_data()
        else:
            if self.paddle2_vel != 0:
                self.request_game_sync_paddle_data()

    def game(self):

        def update_game(self):
            self.draw(self.window)
            self.input_handler()
            pygame.display.update()

        pygame.init()
        self.fps = pygame.time.Clock()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT), 0, 32)
        if self.host:
            pygame.display.set_caption("pyfase Multiplayer Daylight Pong - PLAYER 1")
        else:
            pygame.display.set_caption("pyfase Multiplayer Daylight Pong - PLAYER 2")
        self.init()
        self.draw(self.window)
        pygame.display.update()
        if self.host:
            self.request_action('player2_ready', "")
        else:
            self.request_action('player_connected', {'player': 'player2'})
        while True:
            if self.paused is False:
                update_game(self)
            else:
                if self.game_event.wait(0):
                    update_game(self)
                    self.game_event.clear()
                self.input_handler()
            self.fps.tick(60)

    def on_response(self, service, data):
        self.text_status = "READY TO START - PRESS SPACE TO START"
        self.game_event.set()

    @MicroService.action
    def player2_ready(self, service, data):
        if self.host is False:
            self.response("yes, i'm ready")

    @MicroService.action
    def player_connected(self, service, data):
        if self.host:
            self.request_action('player2_ready', '')
        else:
            self.text_status = "READY TO START - PRESS SPACE TO START"
            self.game_event.set()

    @MicroService.action
    def start_game(self, service, data):
        print('start_game')
        self.paused = False
        self.request_game_sync_all()
        self.text_status = ""
        self.winner = ""

    @MicroService.action
    def game_sync_all(self, service, data):
        if self.host:
            self.paddle2_pos[1] = data['paddle2_pos'][1]
        else:
            self.paddle1_pos[1] = data['paddle1_pos'][1]
            self.ball_pos = data['ball_pos']
            self.ball_vel = data['ball_vel']
            self.r_score = data['r_score']
            self.l_score = data['l_score']

    def request_game_sync_all(self):
        self.request_action('game_sync_all', {'paddle1_pos': self.paddle1_pos,
                                              'paddle2_pos': self.paddle2_pos,
                                              'ball_pos': self.ball_pos,
                                              'ball_vel': self.ball_vel,
                                              'r_score': self.r_score,
                                              'l_score': self.l_score})

    @MicroService.action
    def game_sync_ball_data(self, service, data):
        self.ball_pos = data['ball_pos']
        self.ball_vel = data['ball_vel']

    def request_game_sync_ball_data(self):
        self.request_action('game_sync_ball_data', {'ball_pos': self.ball_pos, 'ball_vel': self.ball_vel})

    @MicroService.action
    def game_sync_score_data(self, service, data):
        self.r_score = data['r_score']
        self.l_score = data['l_score']

    def request_game_sync_score_data(self):
        self.request_action('game_sync_score_data', {'r_score': self.r_score, 'l_score': self.l_score})

    @MicroService.action
    def game_sync_paddle_data(self, service, data):
        if self.host:
            self.paddle2_pos[1] = data['paddle2_pos'][1]
        else:
            self.paddle1_pos[1] = data['paddle1_pos'][1]

    def request_game_sync_paddle_data(self):
        self.request_action('game_sync_paddle_data', {'paddle1_pos': self.paddle1_pos, 'paddle2_pos': self.paddle2_pos})

    @MicroService.action
    def game_sync_paused_data(self, service, data):
        print('game_sync_paused_data')
        if data['pause']:
            self.paused = True
            self.text_status = "%s WINS - READY TO START - PRESS SPACE TO START" % data['winner']
            self.game_event.set()

    def request_game_sync_paused_data(self):
        self.request_action('game_sync_paused_data', {'pause': self.paused, "winner": self.winner})

    @MicroService.task
    def pyfase_broker(self):
        if self.host:
            Fase(sender_endpoint=pyfase_sender, receiver_endpoint=pyfase_receiver).execute()

    @MicroService.task
    def game_task(self):
        self.game()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'player1':
            MultiplayerDaylightPong(host=True).execute(enable_tasks=False)
        elif sys.argv[1] == 'player2':
            MultiplayerDaylightPong(host=False).execute(enable_tasks=False)
    print('Please, select your player')
    print('$ python3 pyfaseMultiplayerDaylightPong.py player1')
    print('$ python3 pyfaseMultiplayerDaylightPong.py player2')
