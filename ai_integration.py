import os
import json
import logging
from openai import OpenAI
from interview_prompts import (
    CODING_INTERVIEW_PROMPT,
    ML_DESIGN_INTERVIEW_PROMPT,
    SYSTEM_DESIGN_INTERVIEW_PROMPT,
    SQL_INTERVIEW_PROMPT,
    ML_THEORY_INTERVIEW_PROMPT,
    MATH_INTERVIEW_PROMPT,
    CUSTOM_INTERVIEW_PROMPT
)

# Initialize the OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

def generate_interview_questions(interview_type, position, num_questions=5, custom_requirements=None):
    """
    Generate interview questions based on the interview type and position.
    
    Args:
        interview_type (str): Type of interview ('coding', 'ml_design', 'system_design', 'sql', 'ml_theory', 'math', 'custom')
        position (str): The job position
        num_questions (int): Number of questions to generate
        custom_requirements (str, optional): Custom requirements for custom interview type
        
    Returns:
        list: List of question dictionaries
    """
    try:
        # Select the appropriate prompt based on interview type
        prompt_map = {
            'coding': CODING_INTERVIEW_PROMPT,
            'ml_design': ML_DESIGN_INTERVIEW_PROMPT,
            'system_design': SYSTEM_DESIGN_INTERVIEW_PROMPT,
            'sql': SQL_INTERVIEW_PROMPT,
            'ml_theory': ML_THEORY_INTERVIEW_PROMPT,
            'math': MATH_INTERVIEW_PROMPT,
            'custom': CUSTOM_INTERVIEW_PROMPT
        }
        
        if interview_type not in prompt_map:
            raise ValueError(f"Invalid interview type: {interview_type}")
            
        base_prompt = prompt_map[interview_type]
        
        # Format the prompt with the appropriate parameters
        if interview_type == 'custom':
            prompt = base_prompt.format(
                num_questions=num_questions,
                position=position,
                requirements=custom_requirements or "No specific requirements provided."
            )
        else:
            prompt = base_prompt.format(
                num_questions=num_questions,
                position=position
            )
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert interviewer for tech companies."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure it's the expected format
        if 'questions' in result:
            return result['questions']
        return result
    except Exception as e:
        logging.error(f"Error generating interview questions: {e}")
        # Fallback questions if API fails
        fallback_questions = []
        for i in range(num_questions):
            fallback_questions.append({
                "question": f"Default {interview_type} question #{i+1} for {position}",
                "question_type": interview_type
            })
        return fallback_questions

def analyze_response(question_text, question_type, interview_type, answer, language=None):
    """
    Analyze a user's response to an interview question.
    
    Args:
        question_text (str): The interview question
        question_type (str): Type of question
        interview_type (str): Type of interview
        answer (str): User's answer
        language (str, optional): Programming language for coding questions
        
    Returns:
        dict: Analysis results with 'analysis' and 'score' keys
    """
    try:
        # Add language context for coding questions
        language_context = ""
        if language and interview_type == 'coding':
            language_context = f"\nProgramming Language: {language}\n"
        
        prompt = f"""
        Analyze the following response to a {question_type} question in a {interview_type} interview:
        
        Question: {question_text}
        {language_context}
        Response: {answer}
        
        Provide detailed feedback on the response's strengths and weaknesses.
        Score the response on a scale of 0-100 based on clarity, correctness, and completeness.
        
        Format the response as a JSON object with 'analysis' and 'score' keys.
        The 'analysis' should be detailed but concise feedback.
        The 'score' should be a number between 0 and 100.
        """
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert interviewer providing accurate and helpful feedback."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure it has the expected format
        if 'analysis' not in result or 'score' not in result:
            return {
                'analysis': "Unable to provide detailed analysis at this time.",
                'score': 50
            }
            
        return result
    except Exception as e:
        logging.error(f"Error analyzing response: {e}")
        return {
            'analysis': "Unable to provide detailed analysis at this time.",
            'score': 50
        }

def generate_interview_feedback(interview_type, position, question_responses, overall_score):
    """
    Generate comprehensive feedback for an entire interview.
    
    Args:
        interview_type (str): Type of interview
        position (str): Job position
        question_responses (list): List of question response dictionaries
        overall_score (float): Overall interview score
        
    Returns:
        dict: Comprehensive feedback
    """
    try:
        # Format the question responses as a string
        questions_str = ""
        for i, qr in enumerate(question_responses):
            questions_str += f"Question {i+1}: {qr['question']}\n"
            questions_str += f"Response: {qr['response']}\n"
            questions_str += f"Score: {qr['score']}\n\n"
        
        prompt = f"""
        Generate comprehensive feedback for a {interview_type} interview for a {position} position.
        
        The candidate's overall score was {overall_score}/100.
        
        Here are the questions and responses:
        
        {questions_str}
        
        Provide detailed feedback including:
        1. Key strengths demonstrated in the interview
        2. Areas that need improvement
        3. Specific suggestions for improvement
        4. Detailed analysis of overall performance
        
        Format the response as a JSON object with 'strengths', 'weaknesses', 'improvement_suggestions', and 'detailed_feedback' keys.
        Each should be a string with bullet points or paragraphs.
        """
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert interviewer providing constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure it has the expected keys
        required_keys = ['strengths', 'weaknesses', 'improvement_suggestions', 'detailed_feedback']
        for key in required_keys:
            if key not in result:
                result[key] = "Not available"
                
        return result
    except Exception as e:
        logging.error(f"Error generating interview feedback: {e}")
        return {
            'strengths': "Unable to analyze strengths at this time.",
            'weaknesses': "Unable to analyze weaknesses at this time.",
            'improvement_suggestions': "Unable to provide improvement suggestions at this time.",
            'detailed_feedback': "Unable to provide detailed feedback at this time."
        }
