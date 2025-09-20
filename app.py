from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration with PostgreSQL for production
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Render/Heroku fix for newer SQLAlchemy
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///flashcards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration for longer login duration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # 30 days
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access your flashcards.'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'
login_manager.remember_cookie_duration = timedelta(days=30)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    decks = db.relationship('Deck', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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

class FunFact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clue = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<FunFact {self.answer}>'

def seed_fun_facts():
    """Seed the database with fun facts"""
    fun_facts = [
        ("Largest mammal on Earth", "WHALE", "Nature"),
        ("Capital of France", "PARIS", "Geography"),
        ("Author of Romeo and Juliet", "SHAKESPEARE", "Literature"),
        ("Planet closest to the sun", "MERCURY", "Science"),
        ("Tallest mountain in the world", "EVEREST", "Geography"),
        ("Chemical symbol for gold", "AU", "Science"),
        ("Fastest land animal", "CHEETAH", "Nature"),
        ("Number of continents", "SEVEN", "Geography"),
        ("Study of stars and planets", "ASTRONOMY", "Science"),
        ("Largest ocean on Earth", "PACIFIC", "Geography"),
        ("Red planet in our solar system", "MARS", "Science"),
        ("King of the jungle", "LION", "Nature"),
        ("Hardest natural substance", "DIAMOND", "Science"),
        ("Ancient wonder in Egypt", "PYRAMID", "History"),
        ("Language spoken in Brazil", "PORTUGUESE", "Geography"),
        ("Smallest bird in the world", "HUMMINGBIRD", "Nature"),
        ("Instrument with 88 keys", "PIANO", "Music"),
        ("Largest desert in the world", "SAHARA", "Geography"),
        ("Gas we breathe to live", "OXYGEN", "Science"),
        ("Frozen water", "ICE", "Science"),
        ("Animal that gives us milk", "COW", "Nature"),
        ("Season after winter", "SPRING", "Nature"),
        ("Device used to tell time", "CLOCK", "General"),
        ("Primary colors are red, blue, and", "YELLOW", "Art"),
        ("Number of sides in a triangle", "THREE", "Math"),
        ("Opposite of hot", "COLD", "General"),
        ("Animal known for its trunk", "ELEPHANT", "Nature"),
        ("First meal of the day", "BREAKFAST", "General"),
        ("Planet we live on", "EARTH", "Science"),
        ("Sound a cat makes", "MEOW", "Nature"),
        ("Opposite of black", "WHITE", "General"),
        ("Vehicle that flies in the sky", "AIRPLANE", "Transportation"),
        ("Insect that makes honey", "BEE", "Nature"),
        ("Number of legs on a spider", "EIGHT", "Nature"),
        ("Fruit that keeps the doctor away", "APPLE", "Health")
    ]

    for clue, answer, category in fun_facts:
        if not FunFact.query.filter_by(answer=answer).first():
            fact = FunFact(clue=clue, answer=answer, category=category)
            db.session.add(fact)

    db.session.commit()

@app.route('/')
@login_required
def index():
    decks = Deck.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', decks=decks)

@app.route('/deck/<int:deck_id>')
@login_required
def view_deck(deck_id):
    deck = Deck.query.filter_by(id=deck_id, user_id=current_user.id).first_or_404()
    return render_template('deck.html', deck=deck)

@app.route('/create_deck', methods=['GET', 'POST'])
@login_required
def create_deck():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        deck = Deck(name=name, description=description, user_id=current_user.id)
        db.session.add(deck)
        db.session.commit()

        flash('Deck created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('create_deck.html')

@app.route('/deck/<int:deck_id>/add_card', methods=['GET', 'POST'])
@login_required
def add_card(deck_id):
    deck = Deck.query.filter_by(id=deck_id, user_id=current_user.id).first_or_404()

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
@login_required
def study_deck(deck_id):
    deck = Deck.query.filter_by(id=deck_id, user_id=current_user.id).first_or_404()

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

import random

class CrosswordGenerator:
    def __init__(self, size=15):
        self.size = size
        self.grid = [['' for _ in range(size)] for _ in range(size)]
        self.word_positions = []

    def clean_word(self, word):
        """Clean word for crossword use"""
        return ''.join(char.upper() for char in word if char.isalpha())

    def can_place_word(self, word, row, col, direction):
        """Check if word can be placed at position"""
        word = self.clean_word(word)
        if not word or len(word) < 2:
            return False

        if direction == 'across':
            if col + len(word) > self.size:
                return False
            # Check for conflicts
            for i, letter in enumerate(word):
                current = self.grid[row][col + i]
                if current != '' and current != letter:
                    return False
            return True
        else:  # down
            if row + len(word) > self.size:
                return False
            # Check for conflicts
            for i, letter in enumerate(word):
                current = self.grid[row + i][col]
                if current != '' and current != letter:
                    return False
            return True

    def place_word(self, word, clue, row, col, direction):
        """Place word on grid"""
        word = self.clean_word(word)
        if not word:
            return False

        if direction == 'across':
            for i, letter in enumerate(word):
                self.grid[row][col + i] = letter
        else:  # down
            for i, letter in enumerate(word):
                self.grid[row + i][col] = letter

        self.word_positions.append({
            'word': word,
            'clue': clue,
            'row': row,
            'col': col,
            'direction': direction,
            'number': len(self.word_positions) + 1
        })
        return True

    def find_intersections(self, word):
        """Find possible intersections with existing words"""
        word = self.clean_word(word)
        if not word:
            return []

        intersections = []

        for pos in self.word_positions:
            existing_word = pos['word']
            for i, letter in enumerate(word):
                for j, existing_letter in enumerate(existing_word):
                    if letter == existing_letter:
                        if pos['direction'] == 'across':
                            # Place new word down
                            new_row = pos['row'] - i
                            new_col = pos['col'] + j
                            if (new_row >= 0 and new_row + len(word) <= self.size and
                                self.can_place_word(word, new_row, new_col, 'down')):
                                intersections.append((new_row, new_col, 'down'))
                        else:
                            # Place new word across
                            new_row = pos['row'] + j
                            new_col = pos['col'] - i
                            if (new_col >= 0 and new_col + len(word) <= self.size and
                                self.can_place_word(word, new_row, new_col, 'across')):
                                intersections.append((new_row, new_col, 'across'))

        return intersections

    def generate_crossword(self, word_clue_pairs):
        """Generate crossword from word-clue pairs"""
        if not word_clue_pairs:
            return None

        # Shuffle for variety
        random.shuffle(word_clue_pairs)

        # Place first word in center
        first_word, first_clue = word_clue_pairs[0]
        first_word = self.clean_word(first_word)
        if first_word:
            start_row = self.size // 2
            start_col = (self.size - len(first_word)) // 2
            self.place_word(first_word, first_clue, start_row, start_col, 'across')

        # Try to place remaining words
        for word, clue in word_clue_pairs[1:]:
            word = self.clean_word(word)
            if not word:
                continue

            intersections = self.find_intersections(word)
            if intersections:
                # Try first valid intersection
                row, col, direction = intersections[0]
                self.place_word(word, clue, row, col, direction)
            else:
                # Try to place randomly if no intersections found
                for _ in range(20):  # Max attempts
                    row = random.randint(0, self.size - 1)
                    col = random.randint(0, self.size - 1)
                    direction = random.choice(['across', 'down'])
                    if self.can_place_word(word, row, col, direction):
                        self.place_word(word, clue, row, col, direction)
                        break

        return {
            'grid': self.grid,
            'clues': {
                'across': [pos for pos in self.word_positions if pos['direction'] == 'across'],
                'down': [pos for pos in self.word_positions if pos['direction'] == 'down']
            }
        }

@app.route('/deck/<int:deck_id>/crossword')
@login_required
def generate_crossword(deck_id):
    deck = Deck.query.filter_by(id=deck_id, user_id=current_user.id).first_or_404()

    # Collect words and clues from deck
    word_clue_pairs = []

    # Add flashcards
    for card in deck.cards:
        if card.card_type == 'flashcard':
            # Use front as clue, back as answer
            answer = card.back.strip()
            clue = card.front.strip()
            if answer and clue:
                word_clue_pairs.append((answer, clue))
        else:  # note card
            # Use extracted keyword as answer, truncated note as clue
            keyword = card.extract_keyword()
            clue = card.content[:100].strip()
            if len(card.content) > 100:
                clue += "..."
            if keyword and clue:
                word_clue_pairs.append((keyword, clue))

    # Add fun facts if not enough words
    target_words = 15
    if len(word_clue_pairs) < target_words:
        try:
            # Use a more compatible random ordering
            import random as py_random
            all_facts = FunFact.query.all()
            py_random.shuffle(all_facts)
            needed_facts = all_facts[:target_words - len(word_clue_pairs)]

            for fact in needed_facts:
                word_clue_pairs.append((fact.answer, fact.clue))
        except Exception as e:
            # Fallback: just use first few facts if random fails
            fun_facts = FunFact.query.limit(target_words - len(word_clue_pairs)).all()
            for fact in fun_facts:
                word_clue_pairs.append((fact.answer, fact.clue))

    # Generate crossword
    try:
        generator = CrosswordGenerator()
        crossword_data = generator.generate_crossword(word_clue_pairs)

        if not crossword_data or not crossword_data.get('clues'):
            flash('Unable to generate crossword. Try adding more cards to your deck!', 'error')
            return redirect(url_for('view_deck', deck_id=deck_id))

        return render_template('crossword.html',
                             deck=deck,
                             crossword=crossword_data,
                             size=generator.size)
    except Exception as e:
        print(f"Crossword generation error: {e}")
        flash(f'Error generating crossword: {str(e)}', 'error')
        return redirect(url_for('view_deck', deck_id=deck_id))

@app.route('/test_crossword')
@login_required
def test_crossword():
    """Test route to debug crossword generation"""
    try:
        # Test with simple data
        test_pairs = [
            ("CAT", "Furry pet"),
            ("DOG", "Man's best friend"),
            ("SUN", "Star in our solar system")
        ]

        generator = CrosswordGenerator()
        result = generator.generate_crossword(test_pairs)

        return f"<h1>Crossword Test</h1><p>Result: {result}</p><p>Word positions: {len(generator.word_positions) if generator.word_positions else 0}</p>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validation
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('register.html')

        # Create new user
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Enable remember me for 30 days
            login_user(user, remember=True, duration=timedelta(days=30))
            next_page = request.args.get('next')
            flash('Logged in successfully!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    total_decks = Deck.query.filter_by(user_id=current_user.id).count()
    total_cards = db.session.query(Card).join(Deck).filter(Deck.user_id == current_user.id).count()

    return render_template('profile.html',
                         user=current_user,
                         total_decks=total_decks,
                         total_cards=total_cards)

@app.route('/export_data')
@login_required
def export_data():
    import json

    # Get all user's decks and cards
    decks = Deck.query.filter_by(user_id=current_user.id).all()

    export_data = {
        'user': current_user.username,
        'export_date': datetime.utcnow().isoformat(),
        'decks': []
    }

    for deck in decks:
        deck_data = {
            'name': deck.name,
            'description': deck.description,
            'created_at': deck.created_at.isoformat(),
            'cards': []
        }

        for card in deck.cards:
            card_data = {
                'type': card.card_type,
                'created_at': card.created_at.isoformat()
            }

            if card.card_type == 'flashcard':
                card_data['front'] = card.front
                card_data['back'] = card.back
            else:
                card_data['content'] = card.content

            deck_data['cards'].append(card_data)

        export_data['decks'].append(deck_data)

    # Return JSON file download
    response = jsonify(export_data)
    response.headers['Content-Disposition'] = f'attachment; filename=naturecards_backup_{current_user.username}.json'
    return response

@app.route('/delete_deck/<int:deck_id>')
@login_required
def delete_deck(deck_id):
    deck = Deck.query.filter_by(id=deck_id, user_id=current_user.id).first_or_404()
    db.session.delete(deck)
    db.session.commit()
    flash('Deck deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_card/<int:card_id>')
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    # Verify user owns the deck this card belongs to
    deck = Deck.query.filter_by(id=card.deck_id, user_id=current_user.id).first_or_404()
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

        # Seed fun facts
        seed_fun_facts()

    # Use environment variable for debug mode
    debug_mode = not os.environ.get('DATABASE_URL')
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))