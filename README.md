# 🎮 Wikipedia Game Bot

A bot for playing the Wikipedia game that uses Google Gemini AI to intelligently choose the path between articles.

## 📝 Description

The game involves reaching a target Wikipedia article by clicking links in successive articles. The bot starts from a random article and uses AI to choose the best path leading to the goal.

## ✨ Features

- 🤖 Intelligent link selection using Google Gemini AI
- 🔄 Automatic loop prevention
- 📊 Step limit and path tracking
- 🎯 Direct link detection to target
- 🌐 Support for Polish Wikipedia

## 🚀 Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/wikipedia-game-bot.git
cd wikipedia-game-bot
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Configure API key:
   - Create a `.env` file in the project root folder
   - Add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key
   ```
   - You can obtain an API key at [Google AI Studio](https://makersuite.google.com/app/apikey)

## 💻 Usage

Run the script:

```bash
python game.py
```

Then enter the target article you want to reach.

## 📋 Requirements

- Python 3.7+
- Google Gemini API key

## ⚙️ How It Works

1. Bot starts from a random Wikipedia article
2. Fetches page HTML using `requests`
3. Parses content with `BeautifulSoup` and extracts links
4. Sends list of links to Google Gemini AI
5. AI selects the most promising link
6. Bot navigates to the selected article and repeats the process
7. Game ends after finding the target or reaching the step limit (15)

## 🛡️ Security

- API key is stored in `.env` file (ignored by git)
- Do not share your API key publicly

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss proposed changes.

## ⚠️ Note

- The bot uses Google Gemini API, which may be paid after exceeding the free limit
- Use responsibly and in accordance with Wikipedia's policies

## 📝 License

This project was created by PS. All rights reserved.
