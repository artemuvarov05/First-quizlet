# Comprehensive Learning System

This is a comprehensive learning system similar to Quizlet.com that includes multiple study modes, import functionality, and a spaced repetition system based on the forgetting curve.

## Features

### Study Modes
1. **Multiple Choice Mode** - Present a translation and four multiple-choice options
2. **Matching Mode** - Pair words with their definitions or translations
3. **True/False Mode** - Evaluate if word-translation pairs are correct
4. **Typing Mode** - Type the translation with soft grading for minor errors
5. **Comprehensive Review** - Final test to assess overall knowledge

### Import Functionality
- Import vocabulary from JSON files
- Each entry includes: word, user-chosen symbol, and translation/definition
- Supports batch import of vocabulary sets

### Spaced Repetition System
- Based on the forgetting curve to optimize review timing
- Adjusts difficulty based on user performance
- Automatically schedules reviews at optimal intervals

### Soft Grading
- Tolerates minor errors in typing mode
- Handles typos, case differences, and spacing issues
- Allows user override for significant mistakes

## How to Use

1. Run the program: `python3 quizlet_clone.py`
2. Choose option 1 to import vocabulary from a JSON file
3. Or choose option 2 to add vocabulary manually
4. Select option 3 to start a study session
5. The system will cycle through batches of 7 words
6. Complete all study modes for each batch before moving to the next
7. Finish with a comprehensive review test

## File Structure
- `quizlet_clone.py` - Main application code
- `sample_vocabulary.json` - Example vocabulary file format

## Vocabulary File Format

The import file should be in JSON format with the following structure:

```json
[
  {
    "word": "hello",
    "symbol": "h",
    "translation": "a greeting"
  },
  {
    "word": "world",
    "symbol": "w",
    "translation": "the earth or a worldly matter"
  }
]
```

## Study Session Flow

1. **Batch Processing**: Words are grouped in batches of 7
2. **Mode Cycle**: Each batch goes through all study modes:
   - Multiple Choice
   - Matching
   - True/False
   - Typing
3. **Progression**: After completing a batch, move to the next
4. **Review**: Final comprehensive test after all batches

## Spaced Repetition Algorithm

The system uses the following intervals based on the forgetting curve:
- New items: reviewed after 1 day
- After first review: 3 days
- Then: 7, 14, 30, 60, 120 days
- Difficulty adjusts based on performance

## Soft Grading Features

- Allows for minor typos and character swaps
- Tolerates case differences
- Handles spacing issues
- Provides feedback on similarity scores
- User can override if they believe a mistake is minor
