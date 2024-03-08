            
from wikipedia.exceptions import DisambiguationError, PageError
from langchain_google_genai import ChatGoogleGenerativeAI
from pdfminer.high_level import extract_text
from urllib.parse import urlparse
import wikipedia
import json
import re
import os


class ChunkFile:
    def __init__(self, file_path, file_name, remove_references=False, remove_introduction=False):
        """
        Initialize the ChunkFile class with file paths, options to remove references and introductions, 
        and checks if the file already exists.
        """
        if file_name is None:
            raise ValueError("name_file must be specified.")
        
        self.file_path = file_path
        self.file_name = self.ensure_txt_extension(file_name)
        self.remove_references = remove_references
        self.remove_introduction = remove_introduction
        self.file_exists = os.path.isfile(self.file_name)
        
    def ensure_txt_extension(self, file_name):
        if not file_name.endswith('.txt'):
            file_name += '.txt'
        return file_name
    
    def initiate_processing(self):
        """Determine the file type or URL and initiate the appropriate text extraction and processing method."""
        if self.file_path.split(".")[-1].lower() == 'pdf':
            text = self.extract_text_from_pdf()
            text = self.process_text_based_on_options(text)
            self.save_sentences_to_file(text)
        elif bool(re.compile(r'https?://[a-z]{2,3}\.wikipedia\.org/wiki/.*').match(self.file_path)):
            extract_titles = self.extract_titles()
            text = ""
            for title in extract_titles:
                page_text = self.extract_wikipedia_text(title)
                text += page_text + "\n\n" 
            self.save_sentences_to_file(text)
            
        else:
            raise ValueError(f"Unsupported file format or URL")

    def extract_text_from_pdf(self):
        """Extract raw text from a PDF file."""
        return extract_text(self.file_path)

    def process_text_based_on_options(self, text):
        """Process the extracted text based on user options to remove introductions and/or references, and clean up."""
        text = self.remove_unwanted_sections(text)
        text = self.cleanup_text(text)
        return text

    def remove_unwanted_sections(self, text):
        """Remove introduction and/or references from the text if specified by the user."""
        text = self.remove_introduction_if_specified(text)
        text = self.remove_references_if_specified(text)
        return text

    def remove_introduction_if_specified(self, text):
        """Remove the introduction section from the text if the user has specified to do so."""
        if not self.remove_introduction:
            return text
        
        start_pattern = re.compile(r"\n\s*\n\s*2\.?\s{1,3}[A-Z][a-z]*")
        start_match = start_pattern.search(text)
        return text[start_match.start():] if start_match else text

    def remove_references_if_specified(self, text):
        """Remove the references section from the text if the user has specified to do so."""
        if not self.remove_references:
            return text
        
        references_pattern = re.compile(r"\n\s*\n\s*References")
        references_match = references_pattern.search(text)
        return text[:references_match.start()] if references_match else text

    def cleanup_text(self, text):
        """Clean up the text by removing headers, figures, and tables, and splitting into sentences."""
        combined_removal_pattern = re.compile(
            r"^\s*\d+(\.\d+)*\.\s*.+?$\n?"
            r"|[^.]*?\bFig\..*?\n{2,}"
            r"|Table \d+.*?\n\n",
            flags=re.DOTALL | re.MULTILINE
        )
        text = combined_removal_pattern.sub('\n', text)
        sentences = re.split(r'\n\s*\n', text)
        sentences = [s for s in sentences if len(s.split()) >= 35]
        return '\n\n'.join(sentences)

    def save_sentences_to_file(self, text):
        """Save processed text to a file, appending if the file already exists."""
        with open(self.file_name, 'a', encoding='utf-8') as file:
            if self.file_exists:
                file.write('\n\n')
            file.write(text)
            
    def extract_titles(self):
        """Extract Wikipedia page titles from the URL."""
        titles = []
        path = urlparse(self.file_path).path
        title = path.split("/")[-1]
        title_with_underscore = title.replace(" ", "_")
        titles.append(title_with_underscore)
        return titles
    
    def remove_topic_headings(self, content):
        """Remove topic headings from Wikipedia content to simplify the text."""
        lines = content.splitlines()
        filtered_lines = []
        for line in lines:
            if not (line.startswith("==") and line.endswith("==")):
                filtered_lines.append(line)
        adjusted_text = "\n\n".join([line for line in filtered_lines if len(line.strip().split()) >= 30])  
        return adjusted_text

    def extract_wikipedia_text(self, title):
        """Extract and clean text from a Wikipedia page based on the title."""
        try:
            wiki = wikipedia.page(title, auto_suggest=False)
            text_without_headings = self.remove_topic_headings(wiki.content)
            return text_without_headings
        except DisambiguationError as e:
            return f"DisambiguationError for '{title}': {', '.join(e.options)}"
        except PageError as e:
            return f"PageError for '{title}': {e}"
        except Exception as e:
            return f"Error for {title}: {e}"
    

class CreateDataset:
    def __init__(self, file_path, file_name, google_api_key, start_sentence=0, temperature=0.6):
        """Initialize the dataset creation class with file path, file name, Google API key, and temperature settings for AI model generation."""
        if file_name is None:
            raise ValueError("name_file must be specified.")
                
        self.file_path = file_path
        self.file_name = self.ensure_json_extension(file_name)
        self.start_sentence = start_sentence
        self.google_api_key = google_api_key
        self.temperature = temperature
        
    def model(self):
        """Return a ChatGoogleGenerativeAI model instance configured with specified model parameters and Google API key."""
        return ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=self.google_api_key,
            temperature=self.temperature
        )
        
    def ensure_json_extension(self, file_name):
        if not file_name.endswith('.json'):
            file_name += '.json'
        return file_name
    
    def create_dataset(self):
        """Main method to create a dataset by processing each sentence from the input file."""
        try:
            llm = self.model()
            sentences = self.extract_sentences()
            total_sentences = len(sentences)
            print(f"Starting the processing of {total_sentences} sentences.")
            while self.start_sentence < total_sentences:
                self.process_sentence(sentences[self.start_sentence], llm)
                self.start_sentence += 1
                print(f"Sentence {self.start_sentence}/{total_sentences} processed.")
            print("Processing completed. The data has been saved.")
        except Exception as e:
            print(f"Error creating the dataset: {e}")
            

    def extract_sentences(self):
        """Extract sentences from the specified file path, splitting content by paragraphs."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                paragraphs = content.split('\n\n')
                paragraphs = [paragraph for paragraph in paragraphs if paragraph]
                return paragraphs
        except Exception as e:
            print(f"Error reading the file {self.file_path}: {e}")
            return []

    def process_sentence(self, sentence, llm):
        """Process a single sentence to generate a question and its summary, then evaluate and possibly add it to the dataset."""
        try:
            question = self.generate_question(sentence, llm)
            if question:
                summary = self.generate_summary(sentence, question, llm)
                is_valid = self.evaluate_question(question, summary, llm)
                if is_valid == "True":
                    self.save_to_file({"instruction": question, "output": summary})
                else:
                    self.save_to_alternate_file({"instruction": question, "output": summary})
                    print(f"""According to LLM, the question is not a correct solution to the answer generated.
Question: {question}
Answer: {summary}""")
        except Exception as e:
            print(f"Error processing the sentence '{sentence}': {e}")

    def generate_question(self, sentence, llm):
        """Generate a question based on the provided sentence."""
        
        prompt = f"Generate a clear and precise question, applicable in a broad context, for which the given answer is '{sentence}'. The question should be concise, framed in one sentence, and not refer to specific studies, documents, or details."
        return llm.predict(prompt)

    def generate_summary(self, sentence, question, llm):
        """Generate a summary for how the sentence answers the generated question."""
        
        prompt = f"Write a succinct summary of key concepts of how '{sentence}' answers '{question}'. The summary must stand on its own. Never include math, equations, variables and weird symbols like u00 in the response."
        return llm.predict(prompt)

    def evaluate_question(self, question, summary, llm):
        """Evaluate whether the generated question is a correct solution for the generated summary."""
        
        prompt = f"Is the instruction '{question}' a correct solution for '{summary}'? Answer with 'True' or 'False'."
        return llm.predict(prompt)
  

    def save_to_file(self, qa_data):
        """Save the collected QA data to the specified file in JSON format."""
        all_qa_data = []
        if os.path.exists(self.file_name):
            try:
                with open(self.file_name, 'r', encoding="utf-8") as file:
                    all_qa_data = json.load(file)
            except json.JSONDecodeError:
                all_qa_data = []
                
        all_qa_data.append(qa_data)

        try:
            with open(self.file_name, 'w', encoding="utf-8") as file:
                json.dump(all_qa_data, file, indent=4)
        except IOError as e:
            print(f"Error writing data to the file {self.file_name}: {e}")
    
    def save_to_alternate_file(self, qa_data):
        """Saves QA data in an alternative file, without changing the method save_to_file."""
        original_file_name = self.file_name
        concatenate = "Not_validated_by_LLM.json"
        self.file_name = self.file_name.split(".")
        self.file_name = self.file_name[0] + concatenate
        self.save_to_file(qa_data)
        self.file_name = original_file_name
            
