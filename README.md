# Your Personal Health Companion

Hey there! 👋 Welcome to my health monitoring project. I built this because I wanted a smarter way to track health metrics and get personalized insights. Think of it as having a knowledgeable friend who's always there to help you understand your health better.

## What's Special About This?

This isn't just another health tracker. It's like having a really smart health advisor that:
- Watches your vitals in real-time
- Learns from medical knowledge to give you relevant advice
- Explains things in a way that actually makes sense

## The Cool Stuff It Does

🫀 **Keeps an Eye on Your Health**
- Tracks your heart rate (because that's kind of important!)
- Monitors your blood oxygen (SpO2)
- Counts your steps (every step counts!)

🧠 **Smart Insights**
- Takes what it knows about health and makes it personal to you
- Gives you advice that actually makes sense for your situation
- Keeps learning from trusted health guidelines

📊 **Easy to Understand**
- Shows your health data in a way that's actually helpful
- Lets you know when something needs attention
- Keeps track of how you're doing over time

## Behind the Scenes

I built this using some pretty cool tech:
- Pathway for handling all the real-time stuff
- OpenAI's smarts for understanding health data
- A nice web interface so you can actually use it

## Getting Started

1. **Grab the Code**
   ```bash
   git clone https://github.com/yourusername/healthguard_ai.git
   cd healthguard_ai
   ```

2. **Set Things Up**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```

3. **Fire It Up**
   ```bash
   # Start the backend
   python -m uvicorn src.api.metrics_service:app --reload --port 7000
   
   # Start the dashboard
   python -m streamlit run src/ui/app.py
   ```

## Using It

1. Open up the dashboard at http://localhost:8501
2. Pop in your health numbers
3. Get personalized insights and recommendations

## Want to Make It Better?

Got ideas? Great! Here's how you can help:
1. Fork it
2. Make it better
3. Send me a pull request

## A Note on Privacy

Your health data is important and private. This runs locally on your machine, so your data stays with you.

## What's Next?

I'm thinking about adding:
- Support for more health metrics
- Mobile app integration
- Better trend analysis
- Integration with health devices

## Questions?

Feel free to open an issue or reach out if you have questions or ideas!
