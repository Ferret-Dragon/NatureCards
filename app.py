from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///flashcards.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cards = db.relationship('Card', backref='deck', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Deck {self.name}>'

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.Text, nullable=True)
    back = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    card_type = db.Column(db.String(20), nullable=False, default='flashcard')
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        if self.card_type == 'note':
            return f'<Note {self.content[:20]}...>'
        return f'<Card {self.front[:20]}...>'

    def extract_keyword(self):
        """Extract the most important keyword from note content"""
        if self.card_type != 'note' or not self.content:
            return None

        text = self.content.lower()

        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

        # Find words that are likely keywords (capitalized, technical terms, longer words)
        words = re.findall(r'\b[a-zA-Z]+\b', text)

        # Score words based on various criteria
        word_scores = {}
        for word in words:
            if word in stop_words or len(word) < 3:
                continue

            score = 0

            # Longer words are more likely to be keywords
            score += len(word) * 0.5

            # Words that appear capitalized in original text
            if word.title() in self.content:
                score += 3

            # Words with numbers or special patterns
            if re.search(r'\d', word) or word.endswith('tion') or word.endswith('ism'):
                score += 2

            # Frequency (but not too frequent)
            freq = words.count(word)
            if freq == 1:
                score += 1
            elif freq > 4:
                score -= 1

            word_scores[word] = word_scores.get(word, 0) + score

        if not word_scores:
            # Fallback: return first significant word
            words = [w for w in words if w not in stop_words and len(w) >= 3]
            return words[0].title() if words else "Note"

        # Return the highest scoring word
        keyword = max(word_scores, key=word_scores.get)
        return keyword.title()

@app.route('/')
def index():
    decks = Deck.query.all()
    return render_template('index.html', decks=decks)

@app.route('/deck/<int:deck_id>')
def view_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    return render_template('deck.html', deck=deck)

@app.route('/create_deck', methods=['GET', 'POST'])
def create_deck():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        deck = Deck(name=name, description=description)
        db.session.add(deck)
        db.session.commit()

        flash('Deck created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('create_deck.html')

@app.route('/deck/<int:deck_id>/add_card', methods=['GET', 'POST'])
def add_card(deck_id):
    deck = Deck.query.get_or_404(deck_id)

    if request.method == 'POST':
        card_type = request.form['card_type']

        if card_type == 'flashcard':
            front = request.form['front']
            back = request.form['back']
            card = Card(front=front, back=back, card_type='flashcard', deck_id=deck_id)
        else:  # note card
            content = request.form['content']
            card = Card(content=content, card_type='note', deck_id=deck_id)

        db.session.add(card)
        db.session.commit()

        flash('Card added successfully!', 'success')
        return redirect(url_for('view_deck', deck_id=deck_id))

    return render_template('add_card.html', deck=deck)

@app.route('/deck/<int:deck_id>/study')
def study_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)

    # Prepare cards for study mode
    study_cards = []
    for card in deck.cards:
        if card.card_type == 'flashcard':
            study_cards.append({
                'front': card.front,
                'back': card.back,
                'type': 'flashcard'
            })
        else:  # note card
            keyword = card.extract_keyword()
            study_cards.append({
                'front': keyword,
                'back': card.content,
                'type': 'note'
            })

    return render_template('study.html', deck=deck, study_cards=study_cards)

@app.route('/delete_deck/<int:deck_id>')
def delete_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    db.session.delete(deck)
    db.session.commit()
    flash('Deck deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_card/<int:card_id>')
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    deck_id = card.deck_id
    db.session.delete(card)
    db.session.commit()
    flash('Card deleted successfully!', 'success')
    return redirect(url_for('view_deck', deck_id=deck_id))

if __name__ == '__main__':
    with app.app_context():
        # Only drop tables in development
        if not os.environ.get('DATABASE_URL'):
            db.drop_all()
        db.create_all()

    # Use environment variable for debug mode
    debug_mode = not os.environ.get('DATABASE_URL')
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))