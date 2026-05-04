# Platformer Game – CSCI 1260 Final Project

## Overview

The player controls a character that navigates through levels and interacts with imported visual assets to create a fully playable platforming experience.

---

## Features

* Fully playable 2D platformer built with Pygame
* Player movement, jumping, and collision detection
* Multiple levels with imported visual assets
* Score/progression tracking
* Persistent data handling using file I/O
* Robust exception handling to prevent crashes

---

## Tech Stack

* Language: Python
* Framework/Library: Pygame
* Data Storage: File-based persistence (level/progress data)
* Testing: Pytest
---

## Installation

Clone the repository:

```bash
git clone git@github.com:etsucs-scott/project-4-YOURUSERNAME.git
cd project-4
```

Install dependencies:

```bash
pip install pygame
```

---

## Running the Game

Run the game using:

```bash
python main.py
```

or

```bash
python src/main.py
```

---

## Running Tests

Run unit tests with:

```bash
python -m unittest discover
```

This project includes 10+ unit tests covering core game logic such as movement, collisions, and level loading.

---

## How It Works

The game is structured using object-oriented programming principles. Core systems are separated into classes such as Player, Enemy, LevelManager, and GameEngine.

* The GameEngine controls the main game loop
* The Player class handles movement, physics, and collisions
* The LevelManager loads level data from files and initializes objects
* Enemies follow simple AI patterns for movement or interaction

Game state and level data are stored using file I/O, allowing progress and levels to persist between runs. Exception handling ensures missing or corrupted files do not crash the game.

---

## Author

* Eli Marlow
* ETSU CSCI 1260 – Spring 2026
