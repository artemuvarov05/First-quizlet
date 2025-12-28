#!/usr/bin/env python3
"""
Comprehensive Learning System similar to Quizlet.com
Features:
- Multiple study modes (multiple choice, matching, true/false, typing)
- Import functionality for vocabulary
- Spaced repetition system based on forgetting curve
- Progress tracking and review tests
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re


class VocabularyItem:
    def __init__(self, word: str, symbol: str, translation: str):
        self.word = word
        self.symbol = symbol
        self.translation = translation
        self.last_reviewed = None
        self.next_review = datetime.now()
        self.correct_count = 0
        self.incorrect_count = 0
        self.difficulty = 1  # 1-5 scale, 1 being easiest
    
    def to_dict(self):
        return {
            'word': self.word,
            'symbol': self.symbol,
            'translation': self.translation,
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None,
            'next_review': self.next_review.isoformat(),
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count,
            'difficulty': self.difficulty
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(data['word'], data['symbol'], data['translation'])
        if data['last_reviewed']:
            item.last_reviewed = datetime.fromisoformat(data['last_reviewed'])
        item.next_review = datetime.fromisoformat(data['next_review'])
        item.correct_count = data['correct_count']
        item.incorrect_count = data['incorrect_count']
        item.difficulty = data['difficulty']
        return item


class StudySession:
    def __init__(self, vocabulary: List[VocabularyItem]):
        self.vocabulary = vocabulary
        self.current_index = 0
        self.session_vocab = []
        self.completed = False
    
    def get_current_batch(self, batch_size: int = 7) -> List[VocabularyItem]:
        """Get the next batch of vocabulary items to study"""
        start_idx = self.current_index
        end_idx = min(start_idx + batch_size, len(self.vocabulary))
        return self.vocabulary[start_idx:end_idx]
    
    def move_to_next_batch(self, batch_size: int = 7):
        """Move to the next batch of vocabulary items"""
        self.current_index += batch_size
        return self.current_index < len(self.vocabulary)
    
    def is_session_complete(self):
        """Check if all vocabulary has been studied"""
        return self.current_index >= len(self.vocabulary)


class LearningSystem:
    def __init__(self):
        self.vocabulary = []
        self.study_session = None
        self.spaced_repetition = SpacedRepetitionSystem()
    
    def import_vocabulary(self, file_path: str):
        """Import vocabulary from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item_data in data:
                item = VocabularyItem(
                    item_data['word'],
                    item_data['symbol'],
                    item_data['translation']
                )
                self.vocabulary.append(item)
            
            print(f"Successfully imported {len(data)} vocabulary items")
        except FileNotFoundError:
            print(f"File {file_path} not found")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in {file_path}")
    
    def add_vocabulary_item(self, word: str, symbol: str, translation: str):
        """Add a single vocabulary item"""
        item = VocabularyItem(word, symbol, translation)
        self.vocabulary.append(item)
    
    def start_study_session(self):
        """Start a new study session"""
        if not self.vocabulary:
            print("No vocabulary loaded. Please import vocabulary first.")
            return
        
        self.study_session = StudySession(self.vocabulary)
        print("Starting study session...")
        self.run_study_cycle()
    
    def run_study_cycle(self):
        """Run the complete study cycle for all vocabulary"""
        while not self.study_session.is_session_complete():
            current_batch = self.study_session.get_current_batch()
            print(f"\n--- Studying batch {self.study_session.current_index//7 + 1} ---")
            
            # Multiple Choice Mode
            self.multiple_choice_mode(current_batch)
            
            # Matching Mode
            self.matching_mode(current_batch)
            
            # True/False Mode
            self.true_false_mode(current_batch)
            
            # Typing Mode
            self.typing_mode(current_batch)
            
            # Move to next batch
            if not self.study_session.move_to_next_batch():
                break
        
        # Final comprehensive review
        self.comprehensive_review()
    
    def multiple_choice_mode(self, batch: List[VocabularyItem]):
        """Multiple choice mode - present translation and 4 options"""
        print("\n--- Multiple Choice Mode ---")
        
        for item in batch:
            # Create 4 options: 1 correct, 3 incorrect
            options = [item.translation]
            
            # Add 3 random incorrect translations
            incorrect_options = [v.translation for v in self.vocabulary 
                               if v != item and v.translation not in options]
            options.extend(random.sample(incorrect_options, min(3, len(incorrect_options))))
            
            # Shuffle options
            random.shuffle(options)
            
            print(f"\nWhat does '{item.word}' mean?")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            
            # Get user answer
            while True:
                try:
                    choice = int(input("Select your answer (1-4): ")) - 1
                    if 0 <= choice < len(options):
                        break
                    else:
                        print("Please select a number between 1 and 4")
                except ValueError:
                    print("Please enter a valid number")
            
            # Check if correct
            if options[choice] == item.translation:
                print("Correct!")
                item.correct_count += 1
                self.spaced_repetition.update_item_difficulty(item, True)
            else:
                print(f"Incorrect. The correct answer is: {item.translation}")
                item.incorrect_count += 1
                self.spaced_repetition.update_item_difficulty(item, False)
            
            # Update last reviewed time
            item.last_reviewed = datetime.now()
    
    def matching_mode(self, batch: List[VocabularyItem]):
        """Matching mode - pair words with translations"""
        print("\n--- Matching Mode ---")
        
        # Create word-translation pairs
        words = [item.word for item in batch]
        translations = [item.translation for item in batch]
        
        # Shuffle translations to create matching challenge
        shuffled_translations = translations.copy()
        random.shuffle(shuffled_translations)
        
        # Display words and translations to match
        print("Match the words with their translations:")
        print("\nWords:")
        for i, word in enumerate(words, 1):
            print(f"{i}. {word}")
        
        print("\nTranslations:")
        for i, translation in enumerate(shuffled_translations, 1):
            print(f"{i}. {translation}")
        
        # Get user matches
        correct_matches = 0
        for i, word in enumerate(words):
            target_translation = next(item.translation for item in batch if item.word == word)
            
            while True:
                try:
                    match_num = int(input(f"\nWhich number matches with '{word}'? ")) - 1
                    if 0 <= match_num < len(shuffled_translations):
                        break
                    else:
                        print("Please select a valid number")
                except ValueError:
                    print("Please enter a valid number")
            
            if shuffled_translations[match_num] == target_translation:
                print("Correct!")
                correct_matches += 1
                # Find the matching item and update it
                matching_item = next(item for item in batch if item.translation == target_translation)
                matching_item.correct_count += 1
                self.spaced_repetition.update_item_difficulty(matching_item, True)
            else:
                print(f"Incorrect. '{word}' matches with '{target_translation}'")
                matching_item = next(item for item in batch if item.translation == target_translation)
                matching_item.incorrect_count += 1
                self.spaced_repetition.update_item_difficulty(matching_item, False)
        
        print(f"\nYou matched {correct_matches}/{len(words)} correctly")
    
    def true_false_mode(self, batch: List[VocabularyItem]):
        """True/False mode - evaluate if word-translation pairs are correct"""
        print("\n--- True/False Mode ---")
        
        correct_answers = 0
        
        for item in batch:
            # 50% chance of showing correct pair, 50% of incorrect pair
            is_correct = random.choice([True, False])
            
            if is_correct:
                translation = item.translation
                print(f"\nTrue or False: '{item.word}' means '{translation}'")
                user_answer = input("Enter 'T' for True or 'F' for False: ").upper()
                correct_answer = 'T'
            else:
                # Get a random incorrect translation
                incorrect_translations = [v.translation for v in self.vocabulary if v != item]
                incorrect_translation = random.choice(incorrect_translations)
                print(f"\nTrue or False: '{item.word}' means '{incorrect_translation}'")
                user_answer = input("Enter 'T' for True or 'F' for False: ").upper()
                correct_answer = 'F'
            
            if user_answer == correct_answer:
                print("Correct!")
                correct_answers += 1
                item.correct_count += 1
                self.spaced_repetition.update_item_difficulty(item, True)
            else:
                print(f"Incorrect. The correct answer was {correct_answer}")
                item.incorrect_count += 1
                self.spaced_repetition.update_item_difficulty(item, False)
        
        print(f"\nYou got {correct_answers}/{len(batch)} correct")
    
    def typing_mode(self, batch: List[VocabularyItem]):
        """Typing mode with soft grading for minor errors"""
        print("\n--- Typing Mode ---")
        
        for item in batch:
            print(f"\nType the translation for: '{item.word}'")
            user_translation = input("Your answer: ")
            
            # Soft grading - check for minor errors
            is_correct, feedback = self.soft_grading(item.translation, user_translation)
            
            if is_correct:
                print("Correct!")
                print(f"Feedback: {feedback}")
                item.correct_count += 1
                self.spaced_repetition.update_item_difficulty(item, True)
            else:
                print(f"Incorrect. The correct answer is: '{item.translation}'")
                print(f"Your answer: '{user_translation}'")
                print(f"Feedback: {feedback}")
                
                # Allow user to override if they think it's a minor mistake
                override = input("Do you think this is a minor error that should be counted as correct? (y/n): ").lower()
                if override == 'y':
                    print("Answer marked as correct due to user override.")
                    item.correct_count += 1
                    self.spaced_repetition.update_item_difficulty(item, True)
                else:
                    item.incorrect_count += 1
                    self.spaced_repetition.update_item_difficulty(item, False)
            
            item.last_reviewed = datetime.now()
    
    def soft_grading(self, correct_answer: str, user_answer: str) -> tuple[bool, str]:
        """Soft grading that allows for minor errors"""
        # Normalize both strings
        correct_norm = re.sub(r'[^\w\s]', '', correct_answer.lower())
        user_norm = re.sub(r'[^\w\s]', '', user_answer.lower())
        
        # Exact match
        if correct_norm == user_norm:
            return True, "Perfect match!"
        
        # Check for common minor errors
        if self.calculate_similarity(correct_norm, user_norm) >= 0.8:
            return True, f"Close match! Minor differences detected. Expected: '{correct_answer}'"
        
        # Check for missing spaces or extra spaces
        if correct_norm.replace(' ', '') == user_norm.replace(' ', ''):
            return True, f"Minor spacing issue. Expected: '{correct_answer}'"
        
        # Check for case differences
        if correct_answer.lower() == user_answer.lower():
            return True, f"Case difference only. Expected: '{correct_answer}'"
        
        # Check for common character swaps (typos)
        if self.is_typo_variant(correct_norm, user_norm):
            return True, f"Possible typo detected. Expected: '{correct_answer}'"
        
        return False, f"Not a close match. Expected: '{correct_answer}'"
    
    def calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings using Levenshtein distance"""
        if len(s1) == 0 or len(s2) == 0:
            return 0.0
        
        # Calculate Levenshtein distance
        distances = [[0 for _ in range(len(s2) + 1)] for _ in range(len(s1) + 1)]
        
        for i in range(len(s1) + 1):
            distances[i][0] = i
        for j in range(len(s2) + 1):
            distances[0][j] = j
        
        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                if s1[i-1] == s2[j-1]:
                    cost = 0
                else:
                    cost = 1
                
                distances[i][j] = min(
                    distances[i-1][j] + 1,      # deletion
                    distances[i][j-1] + 1,      # insertion
                    distances[i-1][j-1] + cost  # substitution
                )
        
        max_len = max(len(s1), len(s2))
        return 1.0 - (distances[len(s1)][len(s2)] / max_len)
    
    def is_typo_variant(self, s1: str, s2: str) -> bool:
        """Check if the difference between strings is likely a typo"""
        if abs(len(s1) - len(s2)) > 1:
            return False
        
        diff_count = 0
        i = j = 0
        
        while i < len(s1) and j < len(s2):
            if s1[i] != s2[j]:
                diff_count += 1
                if diff_count > 1:
                    return False
                
                # Check if it's a character swap
                if i + 1 < len(s1) and j + 1 < len(s2) and s1[i+1] == s2[j] and s1[i] == s2[j+1]:
                    i += 2
                    j += 2
                    continue
                # Check if it's an insertion/deletion
                elif len(s1) > len(s2):
                    i += 1
                elif len(s2) > len(s1):
                    j += 1
                else:
                    i += 1
                    j += 1
            else:
                i += 1
                j += 1
        
        return diff_count <= 1
    
    def comprehensive_review(self):
        """Final comprehensive review test"""
        print("\n--- Comprehensive Review Test ---")
        print("This test will assess your overall knowledge of all vocabulary studied.")
        
        # Get all vocabulary items sorted by difficulty (hardest first)
        review_vocab = sorted(self.vocabulary, key=lambda x: x.difficulty, reverse=True)
        
        correct_answers = 0
        total_questions = len(review_vocab)
        
        for item in review_vocab:
            # Randomly select question type
            mode = random.choice(['mc', 'tf', 'typing'])
            
            if mode == 'mc':
                # Multiple choice question
                options = [item.translation]
                incorrect_options = [v.translation for v in self.vocabulary 
                                   if v != item and v.translation not in options]
                options.extend(random.sample(incorrect_options, min(3, len(incorrect_options))))
                random.shuffle(options)
                
                print(f"\nWhat does '{item.word}' mean?")
                for i, option in enumerate(options, 1):
                    print(f"{i}. {option}")
                
                while True:
                    try:
                        choice = int(input("Select your answer (1-4): ")) - 1
                        if 0 <= choice < len(options):
                            break
                        else:
                            print("Please select a number between 1 and 4")
                    except ValueError:
                        print("Please enter a valid number")
                
                if options[choice] == item.translation:
                    print("Correct!")
                    correct_answers += 1
                    item.correct_count += 1
                else:
                    print(f"Incorrect. The correct answer is: {item.translation}")
                
            elif mode == 'tf':
                # True/False question
                is_correct = random.choice([True, False])
                
                if is_correct:
                    translation = item.translation
                    print(f"\nTrue or False: '{item.word}' means '{translation}'")
                    user_answer = input("Enter 'T' for True or 'F' for False: ").upper()
                    correct_answer = 'T'
                else:
                    incorrect_translations = [v.translation for v in self.vocabulary if v != item]
                    incorrect_translation = random.choice(incorrect_translations)
                    print(f"\nTrue or False: '{item.word}' means '{incorrect_translation}'")
                    user_answer = input("Enter 'T' for True or 'F' for False: ").upper()
                    correct_answer = 'F'
                
                if user_answer == correct_answer:
                    print("Correct!")
                    correct_answers += 1
                else:
                    print(f"Incorrect. The correct answer was {correct_answer}")
            
            elif mode == 'typing':
                # Typing question
                print(f"\nType the translation for: '{item.word}'")
                user_answer = input("Your answer: ")
                
                is_correct, feedback = self.soft_grading(item.translation, user_answer)
                
                if is_correct:
                    print("Correct!")
                    correct_answers += 1
                else:
                    print(f"Incorrect. The correct answer is: '{item.translation}'")
        
        score = (correct_answers / total_questions) * 100
        print(f"\n--- Final Results ---")
        print(f"You answered {correct_answers} out of {total_questions} correctly")
        print(f"Your score: {score:.1f}%")
        
        if score >= 90:
            print("Excellent! You've mastered this vocabulary set.")
        elif score >= 70:
            print("Good job! You have a solid understanding of the vocabulary.")
        elif score >= 50:
            print("Fair understanding. Consider reviewing the material again.")
        else:
            print("Needs improvement. We recommend studying this vocabulary set again.")


class SpacedRepetitionSystem:
    def __init__(self):
        # Standard intervals based on forgetting curve (in days)
        self.intervals = [1, 3, 7, 14, 30, 60, 120]  # days
    
    def update_item_difficulty(self, item: VocabularyItem, is_correct: bool):
        """Update item difficulty based on performance"""
        if is_correct:
            # Increase difficulty if user is getting it right too easily
            if item.correct_count > item.incorrect_count * 2:
                item.difficulty = max(1, item.difficulty - 0.5)
        else:
            # Increase difficulty if user is struggling
            item.difficulty = min(5, item.difficulty + 0.5)
        
        # Update next review time based on difficulty
        interval_idx = min(int(item.difficulty), len(self.intervals)) - 1
        days_to_add = self.intervals[interval_idx]
        item.next_review = datetime.now() + timedelta(days=days_to_add)
    
    def get_items_for_review(self) -> List[VocabularyItem]:
        """Get items that are due for review"""
        now = datetime.now()
        return [item for item in self.vocabulary if item.next_review <= now]


def main():
    system = LearningSystem()
    
    print("Welcome to the Comprehensive Learning System!")
    print("1. Import vocabulary from file")
    print("2. Add vocabulary manually")
    print("3. Start study session")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            file_path = input("Enter the path to your vocabulary file: ")
            system.import_vocabulary(file_path)
        
        elif choice == '2':
            print("Enter vocabulary items (type 'done' for word to finish):")
            while True:
                word = input("Word: ")
                if word.lower() == 'done':
                    break
                symbol = input("Symbol: ")
                translation = input("Translation: ")
                system.add_vocabulary_item(word, symbol, translation)
                print("Added successfully!")
        
        elif choice == '3':
            if system.vocabulary:
                system.start_study_session()
            else:
                print("Please add or import vocabulary first.")
        
        elif choice == '4':
            print("Thank you for using the Learning System!")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()