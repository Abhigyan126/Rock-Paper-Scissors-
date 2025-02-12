# Rock Paper Scissors with Q-Learning AI

This repository contains a Rock Paper Scissors game implemented using Pygame, featuring a Q-Learning AI opponent.  You can play against the AI in single-player mode or against another human player in multiplayer mode.

<div align="center">
  <img width="912" alt="Screenshot 2025-02-12 at 2 11 13 PM" src="https://github.com/user-attachments/assets/97f5d0a6-7d53-44b2-812d-08d85dc24272" />
  <img width="912" alt="Screenshot 2025-02-12 at 2 11 19 PM" src="https://github.com/user-attachments/assets/0eab9bbc-2ad9-49fc-82b5-0030c2583332" />
</div>

## Introduction

This project provides a fun and interactive Rock Paper Scissors game.  The single-player mode utilizes a Q-Learning AI that learns to play better over time. The AI adapts its strategy based on previous games, making it a challenging opponent. The multiplayer mode allows two human players to compete against each other.

## Features

- **Single-player mode:** Play against a Q-Learning AI.
- **Multiplayer mode:** Play against another human player.
- **Graphical user interface:**  Uses Pygame for a visually appealing experience.
- **Q-Learning AI:** The AI learns and improves its strategy over time.
- **Score tracking:** Keeps track of the score for each player.
- **Game reset:** Easily reset the game to start a new match.
- **Draw detection:** Detects and announces draws.
- **Menu System:** Allows selection between singleplayer and multiplayer modes.

## How to Run

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Abhigyan126/Rock-Paper-Scissors-.git
    cd Rock-Paper-Scissors-
    ```

2.  **Install dependencies:**

    ```bash
    pip install pygame numpy
    ```
3.  **Run the game:**

    ```bash
    python main.py
    ```

## Training the AI

The AI's knowledge is stored in `q_table.pkl`.  Each game played will update the Q-table, improving the AI's strategy. The AI's learning is continuous; every time you play against it, the AI learns. No separate training script is needed. Just play the game in single-player mode, and the AI will gradually become more proficient.

## Game Logic

-   The game is played in rounds (best of 3).
-   The player chooses Rock, Paper, or Scissors by clicking on the corresponding image.
-   In single-player mode, the AI chooses its move after the player's choice.
-   The winner of each round is determined based on the classic Rock Paper Scissors rules.
-   The score is updated after each round.
-   The game ends after three rounds.
-   The player with the highest score wins the game.
-   A draw is declared if both players choose the same option in the final round.

## Dependencies

-   Pygame
-   NumPy
-   pickle (built-in Python library)

