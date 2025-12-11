# Hippocratic AI Coding Assignment - Submission
**AI Bedtime Story Generator with Iterative Quality Control**
---
## 📖 Project Overview

This project implements an intelligent bedtime story generator for children ages 5-10 using a multi-agent LLM system with iterative quality improvement. The system uses OpenAI's GPT-3.5-turbo with sophisticated prompting strategies to create, evaluate, and refine engaging bedtime stories.

### ✨ Key Features

- **Two-Agent System**: Separate Storyteller and Judge agents with distinct roles and temperature settings
- **Iterative Quality Control**: Stories are evaluated and improved through multiple iterations (up to 3)
- **Comparative Judging**: Judge acknowledges previous feedback and recognizes improvements
- **Smart Selection**: Automatically returns the best-scoring version if target quality isn't reached
- **Plateau Detection**: Monitors score progression and alerts when improvements stagnate
- **Age-Appropriate Content**: Ensures vocabulary, themes, and tone suitable for 5-10 year olds
- **Bedtime Suitability**: Focuses on calming, peaceful narratives with happy endings

---

## 🏗️ System Architecture

### Block Diagram

```
                    ┌──────────────┐
                    │  User Input  │
                    └──────┬───────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  Storyteller Agent   │
                │  (temp=0.7)          │
                │  "Generate Story"    │
                └──────────┬───────────┘
                           │ Draft Story
                           ▼
        ╔════════════════════════════════════╗
        ║   Iterative Improvement Loop       ║
        ║   (Max 3 iterations)               ║
        ║                                    ║
        ║  ┌────────────────────────────┐   ║
        ║  │    Judge Agent             │   ║
        ║  │    (temp=0.1)              │   ║
        ║  │    "Evaluate & Score"      │   ║
        ║  │    + Comparative Feedback  │   ║
        ║  └─────────┬──────────────────┘   ║
        ║            │ Score + Feedback      ║
        ║            ▼                       ║
        ║  ┌────────────────────────────┐   ║
        ║  │  Quality Control Logic     │   ║
        ║  │  • Score >= 8? → DONE      │   ║
        ║  │  • Iterations >= 3? → BEST │   ║
        ║  │  • Plateau detected?       │   ║
        ║  └──┬──────────────────────┬──┘   ║
        ║     │ NO                   │ YES  ║
        ║     ▼                      │      ║
        ║  ┌────────────────────┐    │      ║
        ║  │ Storyteller Agent  │    │      ║
        ║  │ "Improve Story"    │    │      ║
        ║  │ (with feedback)    │    │      ║
        ║  └──────┬─────────────┘    │      ║
        ║         │ Improved Story   │      ║
        ║         └──────────────────┘      ║
        ║         (loop back to Judge)      ║
        ╚════════════════╤═══════════════════╝
                         │
                         ▼
                ┌─────────────────────┐
                │  Best Story         │
                │  + Score Summary    │
                │  + Evaluations      │
                └─────────────────────┘
```

---

## 📂 Project Files

- **`main_iterative.py`** - Iterative story generation system with quality control loop
- **`.env`** - Environment variables (contains OpenAI API key - **NOT included in submission**)
- **`README.md`** - This file

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10
- OpenAI API key

### Installation Steps

```bash
# 1. Install dependencies
pip install openai==0.28.0 python-dotenv

# 2. Create .env file and add your API key
echo "OPENAI_API_KEY=your-key-here" > .env

# 3. Run the story generator
python main_iterative.py
```

## 📊 System Parameters

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| **Target Score** | 8/10 | Ambitious but achievable quality threshold |
| **Max Iterations** | 3 | Balance between quality improvement and API cost |
| **Story Temperature** | 0.7 | Creative but not too random |
| **Judge Temperature** | 0.1 | Consistent, objective evaluation |
| **Max Tokens** | 800 | ~600 words - appropriate bedtime story length |

---

## 💡 What I Would Build Next (2+ Hours)

With 2 more hours, I would add:

1. **Automated Testing Suite** - Unit tests for score extraction, prompt validation, and edge cases (empty inputs, API failures). This ensures reliability and makes the system production-ready.

2. **Performance Metrics Dashboard** - Track average iteration count, score improvements, API costs per story, and success rates. This data would help optimize the prompting strategy and identify areas for improvement.

3. **Multi-Story Session Management** - Allow users to generate multiple stories in one session with conversation history, save favorite stories to disk, and compare different versions side-by-side before selecting the final one.

---

## 🔍 Design Decisions & Learnings

### Challenge: Score Plateaus
Initial implementation had judges repeating the same feedback, causing scores to plateau. **Solution**: Comparative judging where the judge explicitly acknowledges previous feedback.

### Challenge: Knowing When to Stop
System could waste API calls on marginal improvements. **Solution**: Track all versions and return the best one if target not reached.

### Why Store All Versions?
Enables "best of N" selection and prevents regressions where improvements make one aspect better but another worse.

---

## 📈 Example Output

```
Score Progression: 7.0/10 → 7.5/10 → 8.5/10
Best Score Achieved: 8.5/10
✓ Final version selected (iteration 3)
Total Improvement: +1.5 points
```
## 🛠️ Technical Notes

- Uses OpenAI's legacy API (v0.28.0) for compatibility with provided code
- Environment variables managed via `python-dotenv`
- Score extraction via regex parsing of judge responses
- Modular design allows easy swapping of storyteller/judge prompts

## Sample Prompt
- A peaceful story about a cloud floating gently through the sky
- A child discovers they can speak to fairies in the garden
- A story about a child lost in a dark forest with monsters chasing them
