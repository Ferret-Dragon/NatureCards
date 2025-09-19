# 🌿 NatureCards - Organic Flashcard Study App

A beautiful, nature-themed flashcard application for organizing and studying your notes. Perfect for students who want to organize class notes in different decks with an earthy, organic design.

## ✨ Features

- 📚 **Deck Organization**: Create separate decks for different subjects/classes
- 🃏 **Flashcard System**: Add front/back flashcards to each deck
- 📖 **Interactive Study Mode**: Flip cards, navigate with keyboard shortcuts
- 🔀 **Study Tools**: Shuffle cards, track progress, reset sessions
- 🌱 **Organic Theme**: Beautiful earth-toned design with natural colors
- 📱 **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Installation

### Option 1: Automatic Setup (Recommended)

**For macOS/Linux:**
```bash
./install.sh
```

**For Windows:**
```batch
install.bat
```

**Cross-platform Python:**
```bash
python setup.py
```

### Option 2: Manual Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate virtual environment:**
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open in browser:**
   Navigate to `http://127.0.0.1:5000`

## 🎮 How to Use

1. **Create a Deck**: Click "Create New Deck" and add a name/description
2. **Add Cards**: In your deck, click "Add Card" to create flashcards
3. **Study**: Click "Study" to enter interactive flashcard mode
4. **Navigate**: Use mouse clicks or keyboard shortcuts:
   - `Space/Enter`: Flip card
   - `←/→ arrows`: Previous/Next card
   - Shuffle and Reset buttons available

## 🎨 Theme

The app features an organic, earthy design with:
- 🍃 Moss and sage greens
- 🏔️ Earth and bark browns
- 🧡 Clay orange accents
- 🏖️ Cream and sand backgrounds
- 🌿 Nature-inspired typography and emojis

## 📁 Project Structure

```
NatureCards/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── setup.py           # Cross-platform installer
├── install.sh         # Unix/macOS installer
├── install.bat        # Windows installer
├── static/
│   └── css/
│       └── style.css  # Organic theme styling
└── templates/
    ├── base.html      # Base template
    ├── index.html     # Home page
    ├── create_deck.html
    ├── deck.html      # Deck view
    ├── add_card.html
    └── study.html     # Study mode
```

## 🛠️ Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Custom organic/earthy theme

## 🌱 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.