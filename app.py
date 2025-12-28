#!/usr/bin/env python3
"""
Web-based Vocabulary Learning System similar to Quizlet.com
Features:
- Web interface with card-based UI
- Manual vocabulary input functionality
- Spaced repetition system that prioritizes difficult words
- Multiple study modes
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os


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
        self.times_reviewed = 0
    
    def to_dict(self):
        return {
            'word': self.word,
            'symbol': self.symbol,
            'translation': self.translation,
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None,
            'next_review': self.next_review.isoformat(),
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count,
            'difficulty': self.difficulty,
            'times_reviewed': self.times_reviewed
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
        item.times_reviewed = data.get('times_reviewed', 0)
        return item


class SpacedRepetitionSystem:
    def __init__(self):
        # Standard intervals based on forgetting curve (in minutes for testing)
        # In a real application, these would be in days
        self.intervals = [1, 3, 7, 14, 30, 60, 120]  # minutes for testing, would be days in production
    
    def update_item_difficulty(self, item: VocabularyItem, is_correct: bool):
        """Update item difficulty based on performance"""
        item.times_reviewed += 1
        
        if is_correct:
            # Decrease difficulty if user is getting it right consistently
            if item.correct_count > item.incorrect_count:
                item.difficulty = max(1, item.difficulty - 0.2)
            item.correct_count += 1
        else:
            # Increase difficulty if user is struggling
            item.difficulty = min(5, item.difficulty + 0.5)
            item.incorrect_count += 1
        
        # Update next review time based on difficulty
        # Harder items get reviewed more frequently
        difficulty_factor = 6 - item.difficulty  # Lower difficulty number = longer intervals
        interval_idx = min(int(difficulty_factor), len(self.intervals)) - 1
        minutes_to_add = self.intervals[interval_idx]
        item.next_review = datetime.now() + timedelta(minutes=minutes_to_add)
    
    def get_items_for_review(self, vocabulary: List[VocabularyItem]) -> List[VocabularyItem]:
        """Get items that are due for review, prioritizing difficult items"""
        now = datetime.now()
        due_items = [item for item in vocabulary if item.next_review <= now]
        
        # Sort by difficulty (hardest first) and then by how long overdue they are
        due_items.sort(key=lambda x: (x.difficulty, (now - x.next_review).total_seconds()), reverse=True)
        return due_items


class LearningSystem:
    def __init__(self):
        self.vocabulary = []
        self.spaced_repetition = SpacedRepetitionSystem()
        self.current_session_items = []
        self.current_session_index = 0
        self.session_results = {}  # Track results for current session
    
    def save_to_file(self, file_path: str = "vocabulary_data.json"):
        """Save vocabulary to file"""
        data = [item.to_dict() for item in self.vocabulary]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, file_path: str = "vocabulary_data.json"):
        """Load vocabulary from file"""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.vocabulary = [VocabularyItem.from_dict(item_data) for item_data in data]
        else:
            # Load sample vocabulary if no data file exists
            self.load_sample_vocabulary()
    
    def load_sample_vocabulary(self):
        """Load sample vocabulary for initial use"""
        sample_data = [
            {"word": "hello", "symbol": "h", "translation": "привет"},
            {"word": "world", "symbol": "w", "translation": "мир"},
            {"word": "python", "symbol": "p", "translation": "питон, язык программирования"},
            {"word": "computer", "symbol": "c", "translation": "компьютер"},
            {"word": "keyboard", "symbol": "k", "translation": "клавиатура"},
            {"word": "mouse", "symbol": "m", "translation": "мышь"},
            {"word": "screen", "symbol": "s", "translation": "экран"},
            {"word": "algorithm", "symbol": "a", "translation": "алгоритм"},
            {"word": "function", "symbol": "f", "translation": "функция"},
            {"word": "variable", "symbol": "v", "translation": "переменная"}
        ]
        for item_data in sample_data:
            item = VocabularyItem(
                item_data['word'],
                item_data['symbol'],
                item_data['translation']
            )
            self.vocabulary.append(item)
        self.save_to_file()
    
    def add_vocabulary_item(self, word: str, symbol: str, translation: str):
        """Add a single vocabulary item"""
        item = VocabularyItem(word, symbol, translation)
        self.vocabulary.append(item)
        self.save_to_file()
    
    def get_items_for_study(self, count: int = 10) -> List[VocabularyItem]:
        """Get items for study, prioritizing difficult and overdue items"""
        # Get items due for review
        due_items = self.spaced_repetition.get_items_for_review(self.vocabulary)
        
        # If we don't have enough due items, add some random items that haven't been reviewed recently
        if len(due_items) < count:
            not_due = [item for item in self.vocabulary if item.next_review > datetime.now()]
            # Sort by last reviewed (oldest first) and difficulty (hardest first)
            not_due.sort(key=lambda x: (x.last_reviewed or datetime.min, x.difficulty), reverse=True)
            additional_items = not_due[:count - len(due_items)]
            due_items.extend(additional_items)
        
        # Return up to count items, shuffled to avoid predictable order
        selected_items = due_items[:count]
        random.shuffle(selected_items)
        return selected_items
    
    def update_item_performance(self, word: str, is_correct: bool):
        """Update performance for a specific item"""
        item = next((v for v in self.vocabulary if v.word == word), None)
        if item:
            self.spaced_repetition.update_item_difficulty(item, is_correct)
            self.save_to_file()


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize learning system
learning_system = LearningSystem()
learning_system.load_from_file()


@app.route('/')
def index():
    """Main page showing vocabulary cards"""
    return render_template('index.html', vocabulary=learning_system.vocabulary)


@app.route('/study')
def study():
    """Study mode page"""
    items = learning_system.get_items_for_study(10)
    return render_template('study.html', items=items)


@app.route('/add_word', methods=['POST'])
def add_word():
    """Add a new vocabulary word via AJAX"""
    word = request.form.get('word', '').strip()
    symbol = request.form.get('symbol', '').strip()
    translation = request.form.get('translation', '').strip()
    
    if word and translation:
        learning_system.add_vocabulary_item(word, symbol, translation)
        return jsonify({'success': True, 'message': 'Word added successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Please fill in both word and translation'})


@app.route('/quiz')
def quiz():
    """Quiz mode page"""
    items = learning_system.get_items_for_study(10)
    # Prepare quiz questions (multiple choice)
    quiz_items = []
    for item in items:
        # Create 4 options: 1 correct, 3 incorrect
        options = [item.translation]
        
        # Add 3 random incorrect translations
        incorrect_options = [v.translation for v in learning_system.vocabulary 
                           if v != item and v.translation not in options]
        options.extend(random.sample(incorrect_options, min(3, len(incorrect_options))))
        
        # Shuffle options
        random.shuffle(options)
        
        quiz_items.append({
            'word': item.word,
            'options': options,
            'correct_answer': item.translation
        })
    
    return render_template('quiz.html', quiz_items=quiz_items)


@app.route('/update_performance', methods=['POST'])
def update_performance():
    """Update item performance after user interaction"""
    word = request.form.get('word')
    is_correct = request.form.get('is_correct') == 'true'
    
    if word:
        learning_system.update_item_performance(word, is_correct)
        return jsonify({'success': True})
    
    return jsonify({'success': False})


@app.route('/stats')
def stats():
    """Show learning statistics"""
    total_items = len(learning_system.vocabulary)
    due_for_review = len(learning_system.spaced_repetition.get_items_for_review(learning_system.vocabulary))
    
    # Calculate stats
    mastered_items = sum(1 for item in learning_system.vocabulary if item.difficulty <= 2 and item.correct_count > 2)
    difficult_items = [item for item in learning_system.vocabulary if item.difficulty > 3]
    
    return render_template('stats.html', 
                         total_items=total_items,
                         due_for_review=due_for_review,
                         mastered_items=mastered_items,
                         difficult_items=difficult_items[:10])  # Show top 10 difficult items


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)