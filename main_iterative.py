import os
import re
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def call_model(prompt: str, max_tokens=800, temperature=0.1) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message["content"]  # type: ignore


def extract_score_from_evaluation(evaluation: str) -> float:
    """Parse score from judge's response like 'Score: 7/10' or 'Score: 8.5/10'"""
    # Updated regex to support decimal scores like 9.5/10 and two-digit scores like 10/10
    match = re.search(r'Score:\s*(\d+(?:\.\d+)?)/10', evaluation)
    if match:
        return float(match.group(1))
    return 5.0  # Default if parsing fails


def detect_story_category(user_input: str) -> str:
    """Detect the category of story requested (adventure, educational, calming, fantasy)."""
    detection_prompt = f"""Analyze this story request and categorize it into ONE of these types:
- adventure: Action-filled, exciting journeys or quests
- educational: Learning-focused, teaching concepts or lessons
- calming: Gentle, soothing, peaceful stories
- fantasy: Magical, imaginative, fantastical elements
- friendship: Focus on relationships and social bonds

Story request: {user_input}

Respond with ONLY the category name (one word).
Category:"""
    
    category = call_model(detection_prompt, max_tokens=10, temperature=0.1).strip().lower()
    
    # Validate category
    valid_categories = ['adventure', 'educational', 'calming', 'fantasy', 'friendship']
    if category not in valid_categories:
        category = 'adventure'  # Default
    
    return category


def get_category_specific_requirements(category: str) -> str:
    """Return tailored requirements based on story category."""
    requirements = {
        'adventure': """- Build excitement gradually but end calmly
- Include a brave protagonist overcoming challenges
- Use active, engaging language but avoid overstimulation
- Ensure the adventure concludes peacefully for bedtime""",
        
        'educational': """- Weave learning naturally into the narrative
- Teach one clear concept or lesson
- Use simple explanations appropriate for ages 5-10
- Make learning fun and memorable through story""",
        
        'calming': """- Use slow, gentle pacing throughout
- Include soothing imagery (soft clouds, gentle breezes, quiet nights)
- Minimize conflict or make it very mild
- Focus on peaceful, tranquil settings""",
        
        'fantasy': """- Create magical elements that spark wonder, not fear
- Keep magic whimsical and gentle
- Ground fantasy in relatable emotions
- Ensure magical elements lead to peaceful resolution""",
        
        'friendship': """- Emphasize positive relationships and cooperation
- Show characters supporting each other
- Include themes of kindness, sharing, and understanding
- Demonstrate healthy conflict resolution"""
    }
    
    return requirements.get(category, requirements['adventure'])


def generate_initial_story(user_input: str, category: str = None) -> str:
    """Generate the initial story draft using the storyteller agent with category-specific tailoring."""
    
    # Detect category if not provided
    if category is None:
        category = detect_story_category(user_input)
    
    print("\n" + "="*70)
    print(f"STEP 1: GENERATING INITIAL STORY DRAFT (Category: {category.upper()})")
    print("="*70)
    
    # Get category-specific requirements
    category_requirements = get_category_specific_requirements(category)
    
    storyteller_prompt = f"""You are an expert children's storyteller specializing in bedtime stories for ages 5-10.

Write an engaging bedtime story based on this request: {user_input}

General Requirements:
- Length: 200-300 words
- Include a clear story arc: beginning (introduce characters), middle (adventure/conflict), end (resolution)
- Use age-appropriate vocabulary and themes for children aged 5-10
- Include descriptive, imaginative language suitable for bedtime
- End with a peaceful, happy conclusion that's appropriate for bedtime
- Use proper paragraphs for readability

Category-Specific Requirements ({category.upper()}):
{category_requirements}

Story:"""
    
    story = call_model(storyteller_prompt, max_tokens=500, temperature=0.7)
    return story, category


def judge_story(story: str, iteration: int, previous_evaluation: str = None) -> str:
    """Evaluate the story using the judge agent with comparative feedback."""
    
    if previous_evaluation and iteration > 1:
        # Comparative evaluation for iterations after the first
        judge_prompt = f"""You are a children's literature expert and editor specializing in bedtime stories for ages 5-10.

You previously evaluated an earlier version of this story. Now evaluate this IMPROVED version:

Previous Feedback Given:
{previous_evaluation}

Improved Story to Evaluate:
{story}

Evaluate based on these criteria:
1. Age-appropriateness (vocabulary, themes, content suitable for 5-10 year olds)
2. Story structure (clear beginning, middle, end with proper story arc)
3. Engagement (interesting, holds attention, imaginative)
4. Bedtime suitability (calming tone, not scary or overstimulating)
5. Length and pacing (appropriate for bedtime reading)
6. Content safety (NO scary/violent/sad themes inappropriate for bedtime)

⚠️ CRITICAL SCORING RULES - DEDUCT POINTS HEAVILY:
Any story containing the following should receive a LOW score:
- Scary, frightening, or nightmare-inducing content (monsters, ghosts, darkness, being lost/alone, shadows, creepy atmosphere)
- Violence, fighting, weapons, or aggressive behavior (battles, attacks, hitting, kicking)
- Sad or depressing themes (death, loss, abandonment, loneliness, crying without resolution)
- Overly stimulating action (explosions, chases, danger, intense conflict, emergencies)
- Negative emotions as primary theme (fear, anger, jealousy, meanness)
- Inappropriate moral lessons (lying, stealing, disobedience rewarded)

A bedtime story MUST be calming, positive, and leave the child feeling safe and happy. Deduct at least 5 points for any violation of content safety.

IMPORTANT: Acknowledge if previous issues were addressed. Only raise NEW concerns or remaining issues. If improvements were made, increase the score accordingly.

Provide your evaluation in this format:
Score: X/10
Improvements Made: [what was fixed from previous feedback]
Strengths: [list 2-3 specific strengths]
Weaknesses: [list remaining or new areas for improvement]
Suggestions: [provide concrete, actionable suggestions]

Evaluation:"""
    else:
        # Initial evaluation
        judge_prompt = f"""You are a children's literature expert and editor specializing in bedtime stories for ages 5-10.

Evaluate the following story on these criteria:
1. Age-appropriateness (vocabulary, themes, content suitable for 5-10 year olds)
2. Story structure (clear beginning, middle, end with proper story arc)
3. Engagement (interesting, holds attention, imaginative)
4. Bedtime suitability (calming tone, not scary or overstimulating)
5. Length and pacing (appropriate for bedtime reading)
6. Content safety (NO scary/violent/sad themes inappropriate for bedtime)

Story to evaluate:
{story}

⚠️ CRITICAL SCORING RULES - DEDUCT POINTS HEAVILY:
Any story containing the following should receive a LOW score:
- Scary, frightening, or nightmare-inducing content (monsters, ghosts, darkness, being lost/alone, shadows, creepy atmosphere)
- Violence, fighting, weapons, or aggressive behavior (battles, attacks, hitting, kicking)
- Sad or depressing themes (death, loss, abandonment, loneliness, crying without resolution)
- Overly stimulating action (explosions, chases, danger, intense conflict, emergencies)
- Negative emotions as primary theme (fear, anger, jealousy, meanness)
- Inappropriate moral lessons (lying, stealing, disobedience rewarded)

A bedtime story MUST be calming, positive, and leave the child feeling safe and happy. Deduct at least 5 points for any violation of content safety.

Provide your evaluation in this format:
Score: X/10
Strengths: [list 2-3 specific strengths]
Weaknesses: [list 2-3 specific areas for improvement]
Suggestions: [provide concrete, actionable suggestions to improve the story]

Evaluation:"""
    
    print("\n" + "="*70)
    print(f"STEP {iteration * 2}: JUDGING STORY (Iteration {iteration})")
    print("="*70)
    
    evaluation = call_model(judge_prompt, max_tokens=500, temperature=0.1)
    return evaluation


def improve_story(original_story: str, evaluation: str, iteration: int) -> str:
    """Improve the story based on judge's feedback."""
    improvement_prompt = f"""You are an expert children's storyteller. You previously wrote this bedtime story for ages 5-10:

{original_story}

A children's literature expert provided this feedback:

{evaluation}

Please rewrite the story, addressing ALL the feedback and suggestions provided. Maintain what worked well and fix the identified weaknesses. Ensure the improved story is engaging, age-appropriate, and perfect for bedtime.

Improved Story:"""
    
    print("\n" + "="*70)
    print(f"STEP {iteration * 2 + 1}: IMPROVING STORY BASED ON FEEDBACK (Iteration {iteration})")
    print("="*70)
    
    improved_story = call_model(improvement_prompt, max_tokens=500, temperature=0.7)
    return improved_story


def generate_story_with_quality_control(user_input: str, target_score=8, max_iterations=3):
    """
    Generate a story and iteratively improve it based on judge feedback.
    
    Args:
        user_input: The story request from the user
        target_score: Minimum acceptable quality score (1-10)
        max_iterations: Maximum number of improvement iterations
    
    Returns:
        tuple: (final_story, all_evaluations, score_progression, all_story_versions)
    """
    
    # Initial story generation with category detection
    story, category = generate_initial_story(user_input)
    print(f"\n[Initial Draft]:\n{story}")
    
    evaluations = []
    scores = []
    story_versions = [story]  # Track all story versions
    previous_evaluation = None
    
    # Iterative improvement loop
    for iteration in range(1, max_iterations + 1):
        # Judge the current story (with comparative feedback after first iteration)
        evaluation = judge_story(story, iteration, previous_evaluation)
        score = extract_score_from_evaluation(evaluation)
        
        evaluations.append(evaluation)
        scores.append(score)
        
        print(f"\n[Evaluation {iteration}]:\n{evaluation}")
        print(f"\n>>> Current Score: {score}/10")
        
        # Check if we've reached the target score
        if score >= target_score:
            print(f"\n✓ Story meets quality threshold of {target_score}/10!")
            if iteration < max_iterations:
                print(f"Skipping remaining {max_iterations - iteration} iteration(s).")
            break
        
        # Check for plateau (score not improving)
        if len(scores) >= 2 and scores[-1] <= scores[-2]:
            print(f"\n⚠ Score plateaued at {score}/10 (no improvement from previous iteration).")
            if iteration < max_iterations:
                print(f"Continuing to try {max_iterations - iteration} more iteration(s)...")
        
        # Check if this is the last iteration
        if iteration == max_iterations:
            print(f"\n⚠ Max iterations ({max_iterations}) reached.")
            print(f"Final score: {score}/10 (target was {target_score}/10)")
            
            # Find and return the best version
            best_score_idx = scores.index(max(scores))
            if best_score_idx < len(story_versions) - 1:
                print(f"\n📌 Returning best version from iteration {best_score_idx + 1} with score {scores[best_score_idx]}/10")
                story = story_versions[best_score_idx]
            break
        
        # Improve the story based on feedback
        previous_evaluation = evaluation
        story = improve_story(story, evaluation, iteration)
        story_versions.append(story)
        print(f"\n[Improved Story (Version {iteration + 1})]:\n{story}")
    
    return story, evaluations, scores, story_versions, category


def get_user_feedback(story: str, category: str) -> tuple:
    """Get user feedback and determine if changes are needed."""
    print("\n" + "="*70)
    print("USER FEEDBACK")
    print("="*70)
    print("\nWould you like to make any changes to the story?")
    print("1. Make it longer")
    print("2. Make it shorter")
    print("3. Make it more exciting")
    print("4. Make it gentler/calmer")
    print("5. Change something else (describe)")
    print("6. No changes needed (accept story)")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    # Handle option 5 separately to avoid premature input() call
    if choice == '5':
        custom_feedback = input("\nDescribe the changes you'd like: ").strip()
        return custom_feedback, True
    
    feedback_map = {
        '1': ("Make the story longer, adding more details and extending the narrative while maintaining the same tone and style.", True),
        '2': ("Make the story shorter and more concise, keeping only the essential elements of the plot.", True),
        '3': ("Make the story more exciting and adventurous, while still keeping it appropriate for bedtime.", True),
        '4': ("Make the story gentler and calmer, with more soothing language and peaceful imagery.", True),
        '6': ("", False)
    }
    
    feedback, needs_changes = feedback_map.get(choice, ("", False))
    return feedback, needs_changes


def apply_user_feedback(story: str, feedback: str, category: str) -> str:
    """Apply user feedback to regenerate the story."""
    print("\n" + "="*70)
    print("APPLYING USER FEEDBACK")
    print("="*70)
    
    feedback_prompt = f"""You are an expert children's storyteller. Here is a bedtime story you wrote:

{story}

The reader has requested the following change:
{feedback}

Please rewrite the story incorporating this feedback while maintaining:
- Age-appropriateness for 5-10 year olds
- Bedtime suitability (calming, peaceful ending)
- The {category} story style

Revised Story:"""
    
    revised_story = call_model(feedback_prompt, max_tokens=600, temperature=0.7)
    print(f"\n[Revised Story Based on Feedback]:\n{revised_story}")
    return revised_story


def main():
    print("\n" + "🌙" * 35)
    print("  Welcome to the AI Bedtime Story Generator!")
    print("  Iterative Quality Control System (2-Stage Improvement)")
    print("🌙" * 35)
    print("\nI'll create a wonderful bedtime story for children ages 5-10,")
    print("with automatic quality control and iterative improvements!\n")
    
    user_input = input("What kind of story do you want to hear? ")
    
    # Generate story with quality control
    final_story, evaluations, scores, story_versions, category = generate_story_with_quality_control(
        user_input, 
        target_score=8, 
        max_iterations=3
    )
    
    # Display final results
    print("\n" + "="*70)
    print("FINAL STORY")
    print("="*70)
    print(f"\n{final_story}\n")
    
    # User feedback loop
    feedback_text, needs_changes = get_user_feedback(final_story, category)
    if needs_changes:
        final_story = apply_user_feedback(final_story, feedback_text, category)
        print("\n" + "="*70)
        print("FINAL STORY (AFTER USER FEEDBACK)")
        print("="*70)
        print(f"\n{final_story}\n")
    
    print("="*70)
    print("QUALITY IMPROVEMENT SUMMARY")
    print("="*70)
    print(f"\nTotal Iterations: {len(scores)}")
    print(f"Score Progression: {' → '.join([f'{s}/10' for s in scores])}")
    print(f"Best Score Achieved: {max(scores)}/10")
    if len(scores) > 1:
        improvement = scores[-1] - scores[0]
        print(f"Total Improvement: {'+' if improvement >= 0 else ''}{improvement} points")
    
    # Show which version was selected
    best_idx = scores.index(max(scores))
    if best_idx == len(scores) - 1:
        print(f"\n✓ Final version selected (iteration {len(scores)})")
    else:
        print(f"\n📌 Best version selected from iteration {best_idx + 1}")
    
    print("\nFinal Evaluation:")
    print(evaluations[-1])
    
    print("\n" + "="*70)
    print("✨ Story generation complete! Sweet dreams! ✨")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()