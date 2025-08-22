import os
import requests
import time

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"  # You can change this to any available Groq model

class AIAssistant:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        print(f"AI Assistant initialized. API Key present: {bool(self.api_key)}")

    def _chat_completion(self, prompt, max_tokens=300, temperature=0.3):
        if not self.api_key:
            print("ERROR: No API key found!")
            return "Error: GROQ_API_KEY not found in environment variables"
        
        print(f"Making API call to Groq with model: {self.model}")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Retry logic for better reliability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Sending request to Groq API (attempt {attempt + 1}/{max_retries})...")
                response = requests.post(
                    GROQ_API_URL, 
                    headers=headers, 
                    json=data, 
                    timeout=(30, 120)  # (connect_timeout, read_timeout) - increased for longer responses
                )
                print(f"Response status: {response.status_code}")
                response.raise_for_status()
                result = response.json()["choices"][0]["message"]["content"].strip()
                print(f"API call successful, got response: {result[:100]}...")
                return result
            except requests.exceptions.Timeout:
                print(f"ERROR: Request timed out (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return "Error: Request timed out after multiple attempts"
                time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.ConnectionError:
                print(f"ERROR: Connection failed (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return "Error: Connection failed after multiple attempts"
                time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.ChunkedEncodingError:
                print(f"ERROR: Chunked encoding error (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return "Error: Response was interrupted after multiple attempts"
                time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.RequestException as e:
                print(f"ERROR: Request failed - {str(e)} (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return f"Error: {str(e)}"
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"ERROR: Unexpected error - {str(e)} (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return f"Error: {str(e)}"
                time.sleep(2 ** attempt)  # Exponential backoff

    def generate_summary(self, text: str, max_words: int = 150) -> str:
        print(f"Generating summary for text of length: {len(text)} with max_words: {max_words}")
        
        # Increase text limit for longer summaries
        max_chars = min(8000, max_words * 10)  # Allow more characters for longer summaries
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            print(f"Text truncated to {max_chars} characters")
        
        # Calculate max_tokens more generously for longer summaries
        if max_words <= 200:
            max_tokens = int(max_words * 2) + 200
        elif max_words <= 400:
            max_tokens = int(max_words * 2.5) + 300
        else:
            max_tokens = int(max_words * 3) + 500  # Much more generous for long summaries
        
        print(f"Using max_tokens: {max_tokens}")
        
        # Create stronger prompts based on detail level
        if max_words <= 200:
            prompt = f"""Create a concise summary of this document in EXACTLY {max_words} words. Do not exceed this word count.

Document:
{text}

Instructions:
- Write exactly {max_words} words
- Focus on main points and key findings
- Be concise but comprehensive

Summary:"""
        elif max_words <= 400:
            prompt = f"""Create a detailed summary of this document in EXACTLY {max_words} words. Do not exceed this word count.

Document:
{text}

Instructions:
- Write exactly {max_words} words
- Include main points, methodology, key findings, and conclusions
- Structure the summary clearly

Summary:"""
        else:
            prompt = f"""Create a comprehensive summary of this document in EXACTLY {max_words} words. Do not exceed this word count.

Document:
{text}

Instructions:
- Write exactly {max_words} words
- Include main points, methodology, key findings, conclusions, and important details
- Structure the summary with clear sections
- Be thorough and detailed

Summary:"""
        
        return self._chat_completion(prompt, max_tokens=max_tokens, temperature=0.3)

    def answer_question(self, question: str, document_text: str) -> str:
        print(f"Answering question: {question}")
        # Increase text limit for better context
        if len(document_text) > 6000:
            document_text = document_text[:6000] + "..."
        prompt = f"Read the following document and answer the question.\n\nDocument:\n{document_text}\n\nQuestion: {question}\nAnswer:"
        return self._chat_completion(prompt, max_tokens=400, temperature=0.3)

    def generate_challenges(self, document_text: str):
        print("Generating challenge questions")
        # Increase text limit for better questions
        if len(document_text) > 6000:
            document_text = document_text[:6000] + "..."
        prompt = f"Read the following document and write 3 simple questions that test understanding.\n\nDocument:\n{document_text}\n\nQuestions:"
        result = self._chat_completion(prompt, max_tokens=400, temperature=0.5)
        return result.split('\n')

    def evaluate_challenge_response(self, user_answer: str, question: str, document_text: str):
        print(f"Evaluating answer for question: {question}")
        # Increase text limit for better evaluation
        if len(document_text) > 6000:
            document_text = document_text[:6000] + "..."
        prompt = f"Read the document and the question. Evaluate if the answer is correct.\n\nDocument:\n{document_text}\n\nQuestion: {question}\nUser's Answer: {user_answer}\n\nIs this correct? Give a short feedback."
        return self._chat_completion(prompt, max_tokens=200, temperature=0.3) 