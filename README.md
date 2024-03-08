# QADatasetBuilder

The project provides two main functionalities wrapped in a Python library:
1. **ChunkFile**: A class designed for processing text files or URLs to extract, clean, and save chunks of text based on specified criteria. It supports operations such as removing references, extracting text from PDFs, and handling Wikipedia pages.
2. **CreateDataset**: A class aimed at generating a dataset from text files by creating questions and answers using Gemini Pro, allowing for a customizable dataset creation process to fine-tune a model for machine learning applications.

## Features

- Extract text from PDF files or Wikipedia pages
- Option to remove references and introduction sections from the text
- Clean and split the text into meaningful chunks
- Generate questions and answers from text to create datasets
- Customizable text processing and dataset generation settings

## Installation

Before you can use, ensure you have the required dependencies installed:

```python
pip install wikipedia pdfminer.six langchain-google-genai
```

This code also requires access to Gemini Pro free API and must be provided by the user.

## Usage
### ChunkFile
To use the ChunkFile class, initialize it with the path to your file or URL, the name of the output file, and options to remove references and introductions if needed. 

```python
from QADatasetBuilder import ChunkFile

chunker = ChunkFile(
      file_path="path/to/your/document.pdf",
      file_name="processed_text",
      remove_references=True,
      remove_introduction=False
      )
chunker.initiate_processing()
```

### CreateDataset
To create a dataset, initialize the CreateDataset class with the path to your text file, the output file name, your Google API key, and other optional parameters:

```python
from QADatasetBuilder import CreateDataset

dataset_creator = CreateDataset(
      file_path="path/to/your/processed_text.txt",
      file_name="dataset",
      google_api_key="YOUR_GOOGLE_API_KEY"
      )
dataset_creator.create_dataset()
```

## Contribution
Contributions are welcome! If you have suggestions for improvements or bug fixes, please feel free to fork the repository and submit a pull request.

## License
This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/)- see the LICENSE file for details.


Make sure to replace `"YOUR_GOOGLE_API_KEY"` with the actual Google API key or instructions on how user.



