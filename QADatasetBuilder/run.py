from CreateDataset import ChunkFile, CreateDataset

    # Insert pdfs or wikipedia pages here
files = ["https://en.wikipedia.org/wiki/Thermoplastic",
                           "path/to/your/document.pdf",               
        ]

scraped_files = "all_data.txt"

for i in files:
    file_reader = ChunkFile(
        remove_introduction=True, 
        remove_references=True,
        file_path=i, 
        file_name=scraped_files)
    file_reader.initiate_processing()

dataset = CreateDataset(
    file_path= scraped_files,
    file_name = "QAFile.json",
    google_api_key=google_api_key,
    start_sentence=0,
    temperature=0.6
    )

dataset.create_dataset()
