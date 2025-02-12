import numpy as np
import pickle
import multiprocessing as mp
from itertools import product
import random
from tqdm import tqdm

class RPSEnvironment:
    def __init__(self):
        self.actions = ['rock', 'paper', 'scissors']
        self.state = None
        self.reset()
        
    def reset(self):
        self.state = random.choice(self.actions)
        return self.state
        
    def step(self, action):
        # Define winning combinations
        wins = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
        
        # Get opponent's move (random for training)
        opponent_action = random.choice(self.actions)
        
        # Calculate reward
        if action == opponent_action:
            reward = 0
        elif wins[action] == opponent_action:
            reward = 1
        else:
            reward = -1
            
        # Update state
        self.state = opponent_action
        
        return opponent_action, reward, False

class QLearningAgent:
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.1):
        self.actions = ['rock', 'paper', 'scissors']
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.q_table = {
            'rock': {a: 0.0 for a in self.actions},
            'paper': {a: 0.0 for a in self.actions},
            'scissors': {a: 0.0 for a in self.actions}
        }
        
    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            return max(self.q_table[state].items(), key=lambda x: x[1])[0]
            
    def update(self, state, action, reward, next_state):
        best_next_value = max(self.q_table[next_state].values())
        current_value = self.q_table[state][action]
        self.q_table[state][action] = current_value + self.lr * (
            reward + self.gamma * best_next_value - current_value
        )

def train_episode(args):
    episode_count, lr, gamma, epsilon = args
    
    env = RPSEnvironment()
    agent = QLearningAgent(learning_rate=lr, discount_factor=gamma, epsilon=epsilon)
    
    total_reward = 0
    games_won = 0
    
    for _ in range(episode_count):
        state = env.reset()
        done = False
        
        while not done:
            action = agent.get_action(state)
            next_state, reward, done = env.step(action)
            
            agent.update(state, action, reward, next_state)
            
            total_reward += reward
            if reward == 1:
                games_won += 1
                
            state = next_state
            done = True
    
    return agent.q_table, total_reward, games_won

def merge_q_tables(q_tables):
    merged = {
        'rock': {a: 0.0 for a in ['rock', 'paper', 'scissors']},
        'paper': {a: 0.0 for a in ['rock', 'paper', 'scissors']},
        'scissors': {a: 0.0 for a in ['rock', 'paper', 'scissors']}
    }
    
    for state in merged:
        for action in merged[state]:
            values = [table[state][action] for table in q_tables]
            merged[state][action] = np.mean(values)
    
    return merged

def train_parallel(total_episodes=1000000, num_processes=None):
    if num_processes is None:
        num_processes = mp.cpu_count()
    
    # Hyperparameters grid
    learning_rates = [0.1, 0.01]
    discount_factors = [0.95, 0.99]
    epsilons = [0.1, 0.05]
    
    # Create combinations of hyperparameters
    hyperparams = list(product(learning_rates, discount_factors, epsilons))
    episodes_per_combination = total_episodes // len(hyperparams)
    
    # Prepare arguments for multiprocessing
    args_list = [(episodes_per_combination, lr, gamma, epsilon) 
                 for lr, gamma, epsilon in hyperparams]
    
    print(f"Training with {num_processes} processes...")
    print(f"Episodes per hyperparameter combination: {episodes_per_combination}")
    
    # Create process pool and train in parallel
    with mp.Pool(num_processes) as pool:
        results = list(tqdm(pool.imap(train_episode, args_list), 
                          total=len(args_list),
                          desc="Training Progress"))
    
    # Unpack results
    q_tables, rewards, wins = zip(*results)
    
    # Merge Q-tables from different processes
    final_q_table = merge_q_tables(q_tables)
    
    # Calculate statistics
    total_reward = sum(rewards)
    total_wins = sum(wins)
    win_rate = total_wins / (total_episodes)
    
    print(f"\nTraining Complete!")
    print(f"Total Reward: {total_reward}")
    print(f"Win Rate: {win_rate:.2%}")
    
    return final_q_table

def save_q_table(q_table, filename='q_table.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(q_table, f)

def evaluate_agent(q_table, num_games=10000):
    wins = 0
    draws = 0
    losses = 0
    
    actions = ['rock', 'paper', 'scissors']
    winning_moves = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    
    for _ in tqdm(range(num_games), desc="Evaluating"):
        state = random.choice(actions)
        action = max(q_table[state].items(), key=lambda x: x[1])[0]
        opponent_action = random.choice(actions)
        
        if action == opponent_action:
            draws += 1
        elif winning_moves[action] == opponent_action:
            wins += 1
        else:
            losses += 1
    
    print("\nEvaluation Results:")
    print(f"Wins: {wins/num_games:.2%}")
    print(f"Draws: {draws/num_games:.2%}")
    print(f"Losses: {losses/num_games:.2%}")

if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Training parameters
    TOTAL_EPISODES = 10000
    NUM_PROCESSES = mp.cpu_count()  # Use all available CPU cores
    
    print("Starting Training Process...")
    print(f"Total Episodes: {TOTAL_EPISODES:,}")
    print(f"Number of Processes: {NUM_PROCESSES}")
    
    # Train the agent
    final_q_table = train_parallel(TOTAL_EPISODES, NUM_PROCESSES)
    
    # Save the trained model
    save_q_table(final_q_table)
    print("\nQ-table saved to 'q_table.pkl'")
    
    # Evaluate the trained agent
    print("\nEvaluating trained agent...")
    evaluate_agent(final_q_table)