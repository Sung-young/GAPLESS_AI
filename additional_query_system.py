from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json

class AdditionalQuerySystem:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Few-shot examples for additional queries
        self.few_shot_examples = [
            {
                "input": {
                    "previous_answer": {
                        "term": "Closure",
                        "definition": "A closure is a function that has access to variables from its outer scope, even after the outer function has returned.",
                        "example": "function outer() {\n  let count = 0;\n  return function inner() {\n    count++;\n    return count;\n  };\n}\nlet counter = outer();\nconsole.log(counter()); // 1\nconsole.log(counter()); // 2"
                    },
                    "additional_request": "information"
                },
                "output": {
                    "term": "Closure Memory Management",
                    "definition": "Closures maintain references to variables from their outer scope, which keeps these variables in memory even after the outer function has completed execution. This is because the inner function (closure) still has access to these variables.",
                    "example": "function createClosure() {\n  let largeData = new Array(1000000).fill('data');\n  return function() {\n    return largeData.length;\n  };\n}\n// The largeData array remains in memory as long as the closure exists\nlet closure = createClosure();"
                }
            },
            {
                "input": {
                    "previous_answer": {
                        "term": "REST API",
                        "definition": "REST (Representational State Transfer) is an architectural style for designing networked applications.",
                        "example": "GET /api/users - Retrieve all users\nPOST /api/users - Create a new user"
                    },
                    "additional_request": "code"
                },
                "output": {
                    "code": "from flask import Flask, request, jsonify\n\napp = Flask(__name__)\n\n# In-memory storage\nusers = []\n\n@app.route('/api/users', methods=['GET'])\ndef get_users():\n    return jsonify(users)\n\n@app.route('/api/users', methods=['POST'])\ndef create_user():\n    user = request.json\n    users.append(user)\n    return jsonify(user), 201\n\nif __name__ == '__main__':\n    app.run(debug=True)"
                }
            }
        ]
        
        # Prompt template for additional queries
        self.prompt_template = PromptTemplate(
            input_variables=["previous_answer", "additional_request", "category", "few_shot_examples"],
            template="""You are an expert in {category} development. A user has asked for additional information about a previous answer.
Previous answer: {previous_answer}
Additional request: {additional_request}

Here are some examples of how to handle additional requests:
{few_shot_examples}

Please provide a more detailed answer that addresses the user's additional request. The response should be in JSON format with the following structure:
{{
    "term": "term name",
    "definition": "detailed definition",
    "example": "practical example or code snippet"
}}

Response:"""
        )

    def process_additional_query(self, previous_answer: dict, additional_request: str, category: str) -> dict:
        # Format few-shot examples
        formatted_examples = "\n".join([
            f"Input: {json.dumps(ex['input'], indent=2)}\nOutput: {json.dumps(ex['output'], indent=2)}\n"
            for ex in self.few_shot_examples
        ])
        
        # Create prompt
        prompt = self.prompt_template.format(
            previous_answer=json.dumps(previous_answer, indent=2),
            additional_request=additional_request,
            category=category,
            few_shot_examples=formatted_examples
        )
        
        # Get response from model
        response = self.model.predict(prompt)
        
        try:
            # Parse JSON response
            return json.loads(response)
        except json.JSONDecodeError:
            # If JSON parsing fails, return a structured error response
            return {
                "term": "Error",
                "definition": "Failed to generate a proper response. Please try rephrasing your request.",
                "example": ""
            } 