# Vocabulary Learning System (Quizlet Clone)

This is a comprehensive web-based learning system similar to Quizlet.com with multiple study modes and spaced repetition functionality.

## Features

### 1. Web-based Interface
- Card-based UI similar to Quizlet
- Flip cards to reveal translations
- Responsive design for all devices

### 2. Manual Vocabulary Input
- Add new words directly through the web interface
- Input word, symbol (optional), and translation
- Words are saved and persist between sessions

### 3. Intelligent Spaced Repetition
- Difficult words are shown more frequently
- Easy words are shown less frequently
- Algorithm adjusts based on your performance
- Tracks difficulty levels for each word

### 4. Multiple Study Modes
- **Study Mode**: Flip cards and mark your performance
- **Quiz Mode**: Multiple choice questions focusing on difficult words
- **Statistics**: Track your progress and see difficult words

## How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app.py`
3. Open your browser to `http://localhost:5000`

## How It Works

The system uses a spaced repetition algorithm that prioritizes difficult words. When you mark a word as "difficult" or get it wrong, it will appear more frequently in your study sessions. Words you know well will appear less often, optimizing your study time.

The algorithm considers:
- Your success rate with each word
- How recently you've reviewed the word
- The inherent difficulty of the word based on your performance
