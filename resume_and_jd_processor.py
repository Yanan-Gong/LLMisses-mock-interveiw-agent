import os
from pdf2image import convert_from_path
import pytesseract
import string

# Function to extract text from PDFs, clean it, and save it to .txt files
def ocr_extract_clean_text_from_pdf(pdf_path, output_text_file):
    """
    Extract text from a PDF file using OCR, clean it by removing unnecessary spaces
    and punctuation marks, and save the output to a text file.
    
    :param pdf_path: Path to the PDF file
    :param output_text_file: Path to save the cleaned text output
    """
    # Define paths for Tesseract and Poppler
    pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"  # Update if needed
    poppler_path = "/opt/homebrew/bin"  # Update based on your installation

    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        extracted_text = ""

        # Perform OCR on each page/image
        for page_number, image in enumerate(images, start=1):
            print(f"Processing page {page_number} of {os.path.basename(pdf_path)}...")
            text = pytesseract.image_to_string(image, lang="eng")
            extracted_text += text

        # Clean the extracted text: remove extra spaces and punctuation
        cleaned_text = ' '.join(extracted_text.split())  # Remove extra spaces and newlines
        cleaned_text = cleaned_text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation

        # Save the cleaned text to a file
        with open(output_text_file, "w") as text_file:
            text_file.write(cleaned_text)

        print(f"Text extraction and cleaning complete. Cleaned text saved to '{output_text_file}'.")

    except Exception as e:
        print(f"An error occurred while processing {pdf_path}: {e}")

# Function to process all PDFs in a directory
def process_pdfs_in_directory(directory):
    """
    Process all PDF files in the specified directory and save extracted text into .txt files.

    :param directory: Path to the directory containing PDF files
    """
    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist.")
        return

    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in the directory {directory}.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory, pdf_file)
        txt_file_name = os.path.splitext(pdf_file)[0] + "_txtfile.txt"
        txt_file_path = os.path.join(directory, txt_file_name)

        # Process each PDF file
        ocr_extract_clean_text_from_pdf(pdf_path, txt_file_path)

# Function to generate job descriptions corresponding to resumes
def generate_detailed_job_descriptions(resume_dir, output_dir):
    """
    Generate detailed job descriptions with responsibilities, minimum requirements,
    and preferred requirements, and save them with the same name ending in '_jd.txt'.

    :param resume_dir: Directory containing resume text files.
    :param output_dir: Directory to save the generated job description files.
    """
    # 10 detailed job descriptions
    job_descriptions = [
         """**Job Title:** Data Scientist at Google

**Responsibilities:**
- Develop machine learning models to improve search and ad recommendations.
- Perform data analysis on large datasets to derive actionable insights.
- Collaborate with cross-functional teams to design and implement data-driven solutions.
- Create dashboards to track key performance metrics.

**Minimum Requirements:**
- Bachelor’s degree in Computer Science, Statistics, or related field.
- 3+ years of experience in data analysis and predictive modeling.
- Proficiency in Python, SQL, and machine learning frameworks (e.g., TensorFlow).
- Strong communication skills.

**Preferred Requirements:**
- Experience with cloud platforms like GCP or AWS.
- Familiarity with big data tools (e.g., Spark, Hadoop).
- Knowledge of A/B testing frameworks.
        """,
        """**Job Title:** Data Engineer at Microsoft

**Responsibilities:**
- Design, develop, and maintain robust ETL pipelines.
- Ensure data integrity and availability for analytics teams.
- Optimize database performance for scalability.
- Collaborate with stakeholders to define data requirements.

**Minimum Requirements:**
- Bachelor’s degree in Computer Science or related field.
- 3+ years of experience in data engineering.
- Proficiency in Python, SQL, and data pipeline tools (e.g., Airflow).
- Knowledge of relational databases (e.g., MySQL, PostgreSQL).

**Preferred Requirements:**
- Experience with Azure Data Lake or Azure Databricks.
- Familiarity with distributed computing (e.g., Kafka, Spark).
- Cloud certifications.
        """,
        """**Job Title:** Machine Learning Engineer at LinkedIn

**Responsibilities:**
- Develop and optimize machine learning models for personalized recommendations.
- Analyze large-scale datasets to identify trends.
- Work closely with data scientists to deploy scalable ML solutions.
- Experiment and improve model accuracy.

**Minimum Requirements:**
- Bachelor’s degree in Computer Science or Mathematics.
- 3+ years of experience in machine learning.
- Proficiency in Python and PyTorch.
- Solid understanding of algorithms and data structures.

**Preferred Requirements:**
- Experience in natural language processing (NLP).
- Familiarity with big data tools (e.g., Hadoop, Hive).
- Research publications in ML conferences.
        """,
        """**Job Title:** Data Scientist at Amazon

**Responsibilities:**
- Build predictive models to optimize supply chain efficiency.
- Perform statistical analysis to inform business decisions.
- Develop dashboards for performance monitoring.
- Lead cross-functional initiatives to leverage data insights.

**Minimum Requirements:**
- Bachelor’s degree in Statistics, Mathematics, or related field.
- 3+ years of experience in data science roles.
- Strong SQL and Python skills.
- Proficiency in data visualization tools (e.g., Tableau).

**Preferred Requirements:**
- Experience with AWS tools like Redshift and SageMaker.
- Knowledge of optimization algorithms.
- Advanced degree in a related field.
        """,
        """**Job Title:** Data Engineer at Apple

**Responsibilities:**
- Create and manage data pipelines to support machine learning models.
- Develop APIs for accessing and visualizing data.
- Ensure compliance with data security policies.
- Collaborate with product teams to meet data needs.

**Minimum Requirements:**
- Bachelor’s degree in Computer Science or Engineering.
- 3+ years of experience in data engineering.
- Proficiency in SQL, Python, and Scala.
- Knowledge of data governance practices.

**Preferred Requirements:**
- Experience with Spark and Kafka.
- Familiarity with macOS development environments.
- Certifications in data engineering.
        """,
        """**Job Title:** Machine Learning Engineer at Tesla

**Responsibilities:**
- Develop ML models for autonomous driving systems.
- Perform data preprocessing and feature engineering.
- Collaborate with hardware engineers to optimize model performance.
- Document and test ML workflows.

**Minimum Requirements:**
- Bachelor’s degree in Computer Science or Engineering.
- 3+ years of experience in ML engineering.
- Proficiency in Python and TensorFlow.
- Strong understanding of deep learning algorithms.

**Preferred Requirements:**
- Experience with autonomous systems.
- Familiarity with edge computing.
- Publications in AI conferences.
        """,
        """**Job Title:** Data Scientist at Meta

**Responsibilities:**
- Build models to improve user engagement on social platforms.
- Conduct A/B tests to evaluate feature performance.
- Develop predictive models for ad revenue optimization.
- Present findings to leadership.

**Minimum Requirements:**
- Bachelor’s degree in Computer Science or Statistics.
- 3+ years of experience in data science roles.
- Proficiency in Python, SQL, and R.
- Experience with experimentation platforms.

**Preferred Requirements:**
- Knowledge of social network graph algorithms.
- Familiarity with distributed data systems.
- Advanced degree in a relevant field.
        """,
        """**Job Title:** Data Engineer at Intel

**Responsibilities:**
- Design scalable data architectures for AI applications.
- Develop ETL pipelines for large datasets.
- Collaborate with researchers to deliver data solutions.
- Ensure high data quality and reliability.

**Minimum Requirements:**
- Bachelor’s degree in Computer Science or Engineering.
- 3+ years of experience in data engineering roles.
- Proficiency in Python, SQL, and Spark.
- Strong problem-solving skills.

**Preferred Requirements:**
- Experience with Intel hardware optimizations.
- Knowledge of distributed storage systems.
- Certifications in cloud platforms.
        """,
        """**Job Title:** Machine Learning Engineer at Nvidia

**Responsibilities:**
- Develop deep learning models for GPU-accelerated applications.
- Optimize training pipelines for high performance.
- Research new algorithms to enhance model accuracy.
- Collaborate with product teams on AI solutions.

**Minimum Requirements:**
- Bachelor’s degree in Computer Science or related field.
- 3+ years of experience in machine learning roles.
- Proficiency in Python and CUDA programming.
- Solid understanding of neural networks.

**Preferred Requirements:**
- Experience with large-scale training on GPUs.
- Knowledge of computer vision techniques.
- Publications in machine learning conferences.
        """,
        """**Job Title:** Data Engineer at Indeed

**Responsibilities:**
- Build and maintain scalable data pipelines for job analytics.
- Create dashboards to track key metrics.
- Work with product managers to meet data requirements.
- Monitor and troubleshoot data workflows.

**Minimum Requirements:**
- Bachelor’s degree in Computer Science or Engineering.
- 3+ years of experience in data engineering.
- Proficiency in SQL, Python, and Airflow.
- Experience with cloud platforms like GCP.

**Preferred Requirements:**
- Knowledge of distributed systems.
- Familiarity with streaming data pipelines.
- Certifications in data engineering.
        """,
        # Add remaining 9 job descriptions...
    ]

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # List all resume files in the directory
    resume_files = [f for f in os.listdir(resume_dir) if f.endswith('.txt')]
    
    for idx, resume_file in enumerate(resume_files):
        # Determine output file name
        jd_file_name = os.path.splitext(resume_file)[0] + "_jd.txt"
        jd_file_path = os.path.join(output_dir, jd_file_name)
        
        # Get a corresponding job description
        job_description = job_descriptions[idx % len(job_descriptions)]
        
        # Save the job description to a new file
        with open(jd_file_path, "w") as jd_file:
            jd_file.write(job_description)
        
        print(f"Saved job description to: {jd_file_path}")

# Example usage
if __name__ == "__main__":
    pdf_directory = "/Users/yajuanli/Desktop/LLMiss/llm_yj/resumes"  # Update with the correct directory path
    process_pdfs_in_directory(pdf_directory)

    resume_directory = "/Users/yajuanli/Desktop/LLMiss/llm_yj/resumes"  # Update with the actual path to your resume files
    output_directory = "/Users/yajuanli/Desktop/LLMiss/llm_yj/resumes"  # Update with the desired output directory for JD files
    generate_detailed_job_descriptions(resume_directory, output_directory)