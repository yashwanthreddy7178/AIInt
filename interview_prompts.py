"""
Specialized interview prompts for different interview types.
Each prompt is tailored to generate appropriate questions for its specific interview type.
"""

# Coding Interview Prompts
CODING_INTERVIEW_PROMPT = """
Generate {num_questions} realistic coding interview questions for a {position} position.
Each question should be challenging but fair, focusing on:
- Data structures and algorithms
- Problem-solving skills
- Code optimization
- Time and space complexity analysis

For each question, provide:
1. The problem statement
2. Example inputs and expected outputs
3. Constraints and edge cases to consider
4. A question type (e.g., 'array', 'string', 'tree', 'graph', 'dynamic programming')

Format the response as a JSON array of objects with 'question', 'examples', 'constraints', and 'question_type' keys.
"""

# ML System Design Interview Prompts
ML_DESIGN_INTERVIEW_PROMPT = """
Generate {num_questions} realistic ML system design interview questions for a {position} position.
Each question should focus on:
- ML system architecture
- Data pipeline design
- Model selection and training
- Deployment and scaling considerations
- Monitoring and maintenance

For each question, provide:
1. The problem statement
2. Key requirements and constraints
3. Expected system components
4. A question type (e.g., 'recommendation system', 'computer vision', 'NLP system', 'fraud detection')

Format the response as a JSON array of objects with 'question', 'requirements', 'components', and 'question_type' keys.
"""

# System Design Interview Prompts
SYSTEM_DESIGN_INTERVIEW_PROMPT = """
Generate {num_questions} realistic system design interview questions for a {position} position.
Each question should focus on:
- Scalable system architecture
- Database design
- API design
- Caching strategies
- Load balancing
- Fault tolerance

For each question, provide:
1. The problem statement
2. Functional and non-functional requirements
3. Expected system components
4. A question type (e.g., 'distributed system', 'microservices', 'database design', 'API design')

Format the response as a JSON array of objects with 'question', 'requirements', 'components', and 'question_type' keys.
"""

# SQL Interview Prompts
SQL_INTERVIEW_PROMPT = """
Generate {num_questions} realistic SQL interview questions for a {position} position.
Each question should focus on:
- Complex SQL queries
- Database design
- Query optimization
- Data modeling
- Performance tuning

For each question, provide:
1. The problem statement
2. A complete database schema with:
   - Table names and their relationships
   - Column names, data types, and constraints
   - Primary and foreign keys
   - Sample data (2-3 rows per table)
3. Expected output format
4. A question type (e.g., 'joins', 'subqueries', 'window functions', 'indexing')

Format the response as a JSON array of objects with the following structure:
{{
    "question": "The SQL problem statement",
    "schema": {{
        "tables": [
            {{
                "name": "table_name",
                "columns": [
                    {{
                        "name": "column_name",
                        "type": "data_type",
                        "constraints": ["PRIMARY KEY", "NOT NULL", etc.]
                    }}
                ],
                "foreign_keys": [
                    {{
                        "column": "column_name",
                        "references": {{
                            "table": "referenced_table",
                            "column": "referenced_column"
                        }}
                    }}
                ]
            }}
        ],
        "sample_data": {{
            "table_name": [
                {{
                    "column1": "value1",
                    "column2": "value2"
                }}
            ]
        }}
    }},
    "output_format": "Description of expected output format",
    "question_type": "Type of SQL question"
}}
"""

# ML Theory Interview Prompts
ML_THEORY_INTERVIEW_PROMPT = """
Generate {num_questions} realistic ML theory interview questions for a {position} position.
Each question should focus on:
- Machine learning concepts
- Statistical methods
- Model evaluation
- Feature engineering
- Algorithm understanding

For each question, provide:
1. The question
2. Key concepts to cover
3. Expected depth of answer
4. A question type (e.g., 'supervised learning', 'unsupervised learning', 'deep learning', 'statistics')

Format the response as a JSON array of objects with 'question', 'concepts', 'depth', and 'question_type' keys.
"""

# Math/Stats/Logic Interview Prompts
MATH_INTERVIEW_PROMPT = """
Generate {num_questions} realistic math/stats/logic interview questions for a {position} position.
Each question should focus on:
- Probability and statistics
- Mathematical reasoning
- Logical problem-solving
- Algorithmic thinking

For each question, provide:
1. The problem statement
2. Required mathematical concepts
3. Expected solution approach
4. A question type (e.g., 'probability', 'combinatorics', 'logic puzzles', 'mathematical proofs')

Format the response as a JSON array of objects with 'question', 'concepts', 'approach', and 'question_type' keys.
"""

# Custom Interview Prompts
CUSTOM_INTERVIEW_PROMPT = """
Generate {num_questions} interview questions for a {position} position based on the following custom requirements:
{requirements}

For each question, provide:
1. The question
2. Key aspects to evaluate
3. Expected response format
4. A question type

Format the response as a JSON array of objects with 'question', 'evaluation_aspects', 'response_format', and 'question_type' keys.
""" 