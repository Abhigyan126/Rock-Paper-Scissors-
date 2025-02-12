import pygame
import sys
import os
import pickle
from pygame import mixer
import numpy as np

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60
IMAGE_SIZE = 110

# Colors
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Rock Paper Scissors")

class QLearnAI:
    def __init__(self):
        try:
            with open('q_table.pkl', 'rb') as f:
                self.q_table = pickle.load(f)
        except FileNotFoundError:
            # Improved default strategy that follows basic RPS logic
            self.q_table = {
                'rock': {'rock': 0.2, 'paper': 0.5, 'scissors': 0.3},     # Favor paper against rock
                'paper': {'rock': 0.3, 'scissors': 0.5, 'paper': 0.2},    # Favor scissors against paper
                'scissors': {'paper': 0.3, 'rock': 0.5, 'scissors': 0.2}  # Favor rock against scissors
            }
        self.last_state = 'rock'
    
    def get_move(self, state=None):
        if state is None:
            state = self.last_state
            
        # Get action values for current state
        action_values = self.q_table[state]
        
        # Choose the action with highest Q-value most of the time
        if np.random.random() < 0.5:  # 80% exploitation
            move = max(action_values.items(), key=lambda x: x[1])[0]
        else:  # 20% exploration
            move = np.random.choice(['rock', 'paper', 'scissors'])
        
        self.last_state = move
        return move


# Load images
def load_images():
    return {
        'rock': pygame.transform.scale(pygame.image.load('rock.png'), (IMAGE_SIZE, IMAGE_SIZE)),
        'paper': pygame.transform.scale(pygame.image.load('paper.png'), (IMAGE_SIZE, IMAGE_SIZE)),
        'scissors': pygame.transform.scale(pygame.image.load('scissors.png'), (IMAGE_SIZE, IMAGE_SIZE)),
        'background': pygame.transform.scale(pygame.image.load('background.png'), (WINDOW_WIDTH, WINDOW_HEIGHT))
    }

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.images = load_images()
        self.reset_game()
        self.font = pygame.font.Font(None, 36)
        
        # Mode selection buttons
        self.single_player_button = Button(
            WINDOW_WIDTH//2 - BUTTON_WIDTH//2 - 200,
            WINDOW_HEIGHT//2 + 200,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Single Player",
            WHITE
        )
        self.multiplayer_button = Button(
            WINDOW_WIDTH//2 - BUTTON_WIDTH//2 + 200,
            WINDOW_HEIGHT//2 + 200,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Multiplayer",
            WHITE
        )
        
        self.reset_button = Button(
            WINDOW_WIDTH//2 - BUTTON_WIDTH//2,
            WINDOW_HEIGHT - 80,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Reset Game",
            WHITE
        )
        
        self.state = "menu"
        self.game_mode = None
        self.animation_alpha = 0
        self.animation_direction = 1
        self.ai = QLearnAI()
        self.round_count = 0
        self.game_over = False
        self.winner = None

    def reset_game(self):
        self.scores = {'player1': 0, 'player2': 0}
        self.choices = {'player1': None, 'player2': None}
        self.round_count = 0
        self.game_over = False
        self.winner = None
        
    def draw_menu(self):
        screen.blit(self.images['background'], (0, 0))
        self.single_player_button.draw(screen)
        self.multiplayer_button.draw(screen)
        
        # Title text
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Rock Paper Scissors", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 100))
        
    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw winner text or draw message
        if self.winner == 'draw':
            winner_text = "It's a Draw!"
        else:
            winner_text = f"{'Player 1' if self.winner == 'player1' else 'Player 2'} Wins!"
        text_surface = self.font.render(winner_text, True, WHITE)
        screen.blit(text_surface, (WINDOW_WIDTH//2 - text_surface.get_width()//2, WINDOW_HEIGHT//2))
        self.reset_button.draw(screen)
            
    def draw_game(self):
        screen.fill(YELLOW)
        
        # Draw dividing line
        pygame.draw.line(screen, BLACK, (WINDOW_WIDTH//2, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT), 2)
        
        # Draw scores and round count
        score_text1 = self.font.render(f"Player 1: {self.scores['player1']}", True, BLACK)
        score_text2 = self.font.render(f"{'AI' if self.game_mode == 'single' else 'Player 2'}: {self.scores['player2']}", True, BLACK)
        round_text = self.font.render(f"Round: {self.round_count}/3", True, BLACK)
        screen.blit(score_text1, (50, 50))
        screen.blit(score_text2, (WINDOW_WIDTH - 200, 50))
        screen.blit(round_text, (WINDOW_WIDTH//2 - round_text.get_width()//2, 20))
        
        # Calculate positions for better alignment
        choices = ['rock', 'paper', 'scissors']
        y_pos = WINDOW_HEIGHT//2 - IMAGE_SIZE//2
        
        # Draw player labels
        p1_label = self.font.render("Player 1", True, BLACK)
        p2_label = self.font.render("AI" if self.game_mode == 'single' else "Player 2", True, BLACK)
        screen.blit(p1_label, (WINDOW_WIDTH//4 - p1_label.get_width()//2, y_pos - 50))
        screen.blit(p2_label, (3*WINDOW_WIDTH//4 - p2_label.get_width()//2, y_pos - 50))
        
        # Draw choices
        p1_start_x = (WINDOW_WIDTH//4) - ((IMAGE_SIZE * 3 + 40) // 2)
        p2_start_x = (3*WINDOW_WIDTH//4) - ((IMAGE_SIZE * 3 + 40) // 2)
        
        # Draw Player 1 choices
        for i, choice in enumerate(choices):
            x_pos = p1_start_x + i * (IMAGE_SIZE + 20)
            screen.blit(self.images[choice], (x_pos, y_pos))
            if self.choices['player1'] == choice:
                pygame.draw.rect(screen, RED, (x_pos, y_pos, IMAGE_SIZE, IMAGE_SIZE), 3)
        
        # Draw Player 2/AI choices
        for i, choice in enumerate(choices):
            x_pos = p2_start_x + i * (IMAGE_SIZE + 20)
            screen.blit(self.images[choice], (x_pos, y_pos))
            if self.choices['player2'] == choice:
                pygame.draw.rect(screen, RED, (x_pos, y_pos, IMAGE_SIZE, IMAGE_SIZE), 3)
        
        # Draw reset button
        self.reset_button.draw(screen)
        
        if self.game_over:
            self.draw_game_over()
                
    def check_winner(self):
        if None in self.choices.values():
            return
            
        p1, p2 = self.choices['player1'], self.choices['player2']
        if p1 == p2:
            self.round_count += 1
            if self.round_count >= 3: # Check for draw if it's the final round.
                self.game_over = True
                self.winner = 'draw' # Set winner to 'draw'
        else:
            winning_combinations = {
                'rock': 'scissors',
                'paper': 'rock',
                'scissors': 'paper'
            }
            
            if winning_combinations[p1] == p2:
                self.scores['player1'] += 1
            else:
                self.scores['player2'] += 1
            
            self.round_count += 1
            
        self.choices = {'player1': None, 'player2': None}
        
        # Check if game is over (best of 3)
        if self.round_count >= 3:
            self.game_over = True
            if self.winner != 'draw': # Only declare a winner if it's not a draw
                if self.scores['player1'] > self.scores['player2']:
                    self.winner = 'player1'
                else:
                    self.winner = 'player2'
            
    def handle_click(self, pos):
        if self.state == "menu":
            if self.single_player_button.is_clicked(pos):
                self.state = "game"
                self.game_mode = "single"
                return
            if self.multiplayer_button.is_clicked(pos):
                self.state = "game"
                self.game_mode = "multi"
                return
                
        if self.state == "game":
            if self.reset_button.is_clicked(pos):
                self.reset_game()
                self.state = "menu"
                return
            
            if self.reset_button.is_clicked(pos):
                self.reset_game()
                return
                
            if self.game_over:
                return
                
            choices = ['rock', 'paper', 'scissors']
            y_pos = WINDOW_HEIGHT//2 - IMAGE_SIZE//2
            
            # Player 1 choice detection
            p1_start_x = (WINDOW_WIDTH//4) - ((IMAGE_SIZE * 3 + 40) // 2)
            for i, choice in enumerate(choices):
                x_pos = p1_start_x + i * (IMAGE_SIZE + 20)
                if pygame.Rect(x_pos, y_pos, IMAGE_SIZE, IMAGE_SIZE).collidepoint(pos):
                    self.choices['player1'] = choice
                    if self.game_mode == "single":
                        # AI makes its move
                        self.choices['player2'] = self.ai.get_move()
                        self.check_winner()
            
            # Player 2 choice detection (only in multiplayer mode)
            if self.game_mode == "multi":
                p2_start_x = (3*WINDOW_WIDTH//4) - ((IMAGE_SIZE * 3 + 40) // 2)
                for i, choice in enumerate(choices):
                    x_pos = p2_start_x + i * (IMAGE_SIZE + 20)
                    if pygame.Rect(x_pos, y_pos, IMAGE_SIZE, IMAGE_SIZE).collidepoint(pos):
                        self.choices['player2'] = choice
                        self.check_winner()

def main():
    game = Game()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)
                
        if game.state == "menu":
            game.draw_menu()
        else:
            game.draw_game()
            
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()