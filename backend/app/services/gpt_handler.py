import openai
from flask import current_app
import json
from typing import List, Dict, Any

class GPTHandler:
    def __init__(self):
        self.client = openai.OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
    
    def explain_topic(self, topic: str, persona_level: str = 'student', max_words: int = 500) -> str:
        """Generate explanation for a topic based on persona level"""
        try:
            persona_prompts = {
                'student': 'Explain this in simple terms suitable for a high school student:',
                'college': 'Provide a detailed explanation suitable for a college student:',
                'professional': 'Give a comprehensive explanation suitable for a professional:'
            }
            
            prompt = f"{persona_prompts.get(persona_level, persona_prompts['student'])} {topic}\n\nKeep the explanation under {max_words} words and make it engaging and easy to understand."
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful educational tutor. Provide clear, accurate, and engaging explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Sorry, I couldn't generate an explanation right now. Error: {str(e)}"
    
    def generate_quiz(self, topic: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate multiple choice quiz questions for a topic"""
        try:
            prompt = f"""Generate {num_questions} multiple choice questions about {topic}.
            
            Return the response as a JSON array with this exact format:
            [
                {{
                    "question": "Question text here?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Brief explanation of why this is correct"
                }}
            ]
            
            Make sure the questions are educational and the explanations are helpful."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational quiz generator. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                questions = json.loads(content)
                if isinstance(questions, list):
                    return questions
                else:
                    raise ValueError("Response is not a list")
            except json.JSONDecodeError:
                # Fallback: return a simple quiz structure
                return self._generate_fallback_quiz(topic, num_questions)
                
        except Exception as e:
            return self._generate_fallback_quiz(topic, num_questions)
    
    def _generate_fallback_quiz(self, topic: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate a simple fallback quiz if GPT fails"""
        return [
            {
                "question": f"What is the main concept of {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "A",
                "explanation": "This is a fallback question. Please try again later."
            }
        ] * num_questions
    
    def chat_response(self, message: str, session_history: List[Dict[str, str]] = None, user_context: str = "") -> str:
        """Generate chat response with session memory"""
        try:
            # Build conversation history
            messages = [
                {"role": "system", "content": f"You are Athena, a helpful AI tutor for the Personalized Learning Assistant. {user_context} Be encouraging, clear, and educational in your responses."}
            ]
            
            # Add session history (last 10 messages to stay within limits)
            if session_history:
                for msg in session_history[-10:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I'm having trouble responding right now. Please try again in a moment. Error: {str(e)}"
    
    def create_study_plan(self, topics: List[str], target_date: str, persona: str = 'student') -> Dict[str, Any]:
        """Generate a personalized study plan"""
        try:
            topics_str = ", ".join(topics)
            
            prompt = f"""Create a 7-day study plan for these topics: {topics_str}
            Target completion date: {target_date}
            Student level: {persona}
            
            Return the response as a JSON object with this exact format:
            {{
                "title": "Study Plan Title",
                "daily_tasks": [
                    {{
                        "day": 1,
                        "date": "YYYY-MM-DD",
                        "tasks": [
                            {{
                                "title": "Task title",
                                "description": "Task description",
                                "estimated_time": "30 minutes",
                                "type": "reading|practice|review|quiz"
                            }}
                        ]
                    }}
                ]
            }}
            
            Make the plan realistic and engaging for a {persona}."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational planner. Create realistic and engaging study plans. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                plan = json.loads(content)
                return plan
            except json.JSONDecodeError:
                return self._generate_fallback_plan(topics, target_date)
                
        except Exception as e:
            return self._generate_fallback_plan(topics, target_date)
    
    def _generate_fallback_plan(self, topics: List[str], target_date: str) -> Dict[str, Any]:
        """Generate a simple fallback plan if GPT fails"""
        from datetime import datetime, timedelta
        
        start_date = datetime.now().date()
        daily_tasks = []
        
        for day in range(1, 8):
            task_date = start_date + timedelta(days=day-1)
            daily_tasks.append({
                "day": day,
                "date": task_date.strftime("%Y-%m-%d"),
                "tasks": [
                    {
                        "title": f"Study {topics[0] if topics else 'your topic'}",
                        "description": f"Review and practice {topics[0] if topics else 'your topic'} concepts",
                        "estimated_time": "45 minutes",
                        "type": "practice"
                    }
                ]
            })
        
        return {
            "title": f"Study Plan for {', '.join(topics) if topics else 'Your Topics'}",
            "daily_tasks": daily_tasks
        } 