# Cover Letter Generator

A web application that generates personalized cover letters using AI (GitHub Models API with OpenAI GPT-4o-mini).

## Features

- 📝 **AI-Powered Generation**: Uses GitHub Models API for intelligent cover letter creation
- 👤 **User Profile Management**: Store personal information for consistent use
- 📄 **Resume Integration**: Upload and parse resumes (PDF, DOCX, TXT formats)
- 🎨 **PDF Generation**: Creates professional PDF cover letters
- 💾 **Storage & Download**: Save and download generated cover letters
- 🌐 **Simple Web Interface**: Clean, responsive HTML frontend

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure GitHub Token

1. Get your GitHub Personal Access Token (PAT) from: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
2. Update the `.env` file with your token:

```env
GITHUB_TOKEN=your_github_token_here
```

### 3. Run the Application

```bash
python main.py
```

The application will start on `http://localhost:5000`

## Usage Guide

### Step 1: Setup Profile

1. Click "Setup Profile" to enter your personal information
2. Fill in: First Name, Last Name, Email, Phone, Address
3. Save the profile

### Step 2: Upload Resume

1. Click "Upload Resume"
2. Select your resume file (PDF, DOCX, or TXT)
3. Upload the file

### Step 3: Generate Cover Letter

1. Click "Generate Cover Letter" (enabled after profile + resume setup)
2. Enter job details:
   - Company Name
   - Location
   - Job Description (paste the full job posting)
3. Click "Generate Cover Letter"
4. The PDF will be automatically downloaded

## File Structure

```
cover-letter-writer/
├── main.py                 # Flask application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── app/                   # Application modules
│   ├── __init__.py
│   ├── profile_manager.py # User profile management
│   ├── resume_parser.py   # Resume parsing logic
│   └── pdf_generator.py   # PDF generation
├── templates/             # HTML templates
│   └── index.html
├── static/                # CSS/JS assets
│   ├── style.css
│   └── script.js
└── data/                  # Data storage
    ├── profiles/          # User profiles
    ├── resume/           # Uploaded resumes
    └── cover_letters/    # Generated cover letters
```

## Generated Files

Cover letters are saved with the naming format:
`FirstName_LastName_CoverLetter_CompanyName.pdf`

## Supported Resume Formats

- **PDF**: Extracts text using PyPDF2
- **DOCX**: Parses Word documents using python-docx
- **TXT**: Plain text files

## API Endpoints

- `GET /` - Main interface
- `GET/POST /api/profile` - User profile management
- `POST /api/resume` - Resume upload
- `POST /api/generate-cover-letter` - Generate cover letter
- `GET /api/download/<id>` - Download cover letter
- `GET /api/cover-letters` - List all cover letters

## Troubleshooting

### Common Issues

1. **GitHub Token Error**: Make sure your GitHub PAT has the necessary permissions
2. **PDF Generation Error**: Check that reportlab is properly installed
3. **Resume Parse Error**: Ensure your resume file is not corrupted or password-protected

### Logs

Check the console output for detailed error messages and debugging information.

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: GitHub Models API (OpenAI GPT-4o-mini)
- **PDF Generation**: ReportLab
- **Resume Parsing**: PyPDF2, python-docx
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **File Storage**: Local filesystem

## License

MIT License - feel free to modify and use for your needs!
