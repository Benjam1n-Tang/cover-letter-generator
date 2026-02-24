# Cover Letter Generator

A web application that generates personalized cover letters using AI (GitHub Models API with OpenAI GPT-4o-mini) with an intelligent template system.

## Features

- 📝 **AI-Powered Generation**: Uses GitHub Models API (GPT-4o-mini) for human-like cover letter creation
- 📋 **Template System**: Create, save, and reuse cover letter templates with smart placeholder replacement
- 👤 **User Profile Management**: Store personal information for consistent use across all letters
- 📄 **Resume Integration**: Upload and parse resumes (PDF, DOCX, TXT formats) with visual status indicators
- 🎨 **Professional PDF Generation**: Creates polished PDFs with 0.75-inch margins and proper spacing
- 💾 **Streamlined File Management**: Direct PDF downloads with unique naming for easy organization
- 🌐 **Responsive Web Interface**: Clean, Bootstrap-powered UI that works on all devices
- 🤖 **Smart AI Prompts**: Enhanced prompts that generate authentic, professional-sounding content

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Get your GitHub Personal Access Token (PAT) from: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
2. Update the `.env` file with your configuration:

```env
GITHUB_TOKEN=your_github_token_here
FLASK_SECRET_KEY=your_secret_key_here  # Required for Flask sessions
DEBUG=True  # Set to False for production
```

**Note**: The Flask secret key is required for the application to function properly. You can use any secure random string.

### 3. Run the Application

```bash
python main.py
```

The application will start on `http://localhost:5000`

## Usage Guide

### Step 1: Setup Profile

1. Click "Setup Profile" to enter your personal information
2. Fill in: First Name, Last Name, Email, Phone, Address
3. Save the profile - you'll see a green checkmark when complete

### Step 2: Upload Resume

1. Click "Upload Resume"
2. Select your resume file (PDF, DOCX, or TXT)
3. Upload the file - the button will turn green when a resume is detected

### Step 3: Create Templates (Optional but Recommended)

1. Click "Manage Templates" to create reusable cover letter templates
2. Write your template using placeholders like `{company_name}`, `{job_title}`, `{location}`
3. Save templates for different industries or job types
4. Templates help maintain consistency and save time

### Step 4: Generate Cover Letter

1. Click "Generate Cover Letter" (enabled after profile + resume setup)
2. Select a template from the dropdown (optional - first template is selected by default)
3. Enter job details:
   - Company Name
   - Location
   - Job Description (paste the full job posting)
4. Click "Generate Cover Letter"
5. Review the AI-generated content
6. Save as PDF - the file will be automatically downloaded with a unique name

## File Structure

```
cover-letter-writer/
├── main.py                 # Flask application with all endpoints
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (GitHub token, Flask secret)
├── run.sh                 # Quick start script
├── app/                   # Application modules
│   ├── __init__.py
│   ├── profile_manager.py # User profile management
│   ├── resume_parser.py   # Resume parsing logic
│   ├── pdf_generator.py   # PDF generation with custom margins
│   └── template_manager.py # Template system with smart placeholders
├── templates/             # HTML templates
│   └── index.html         # Main interface with template management
├── static/                # CSS/JS assets
│   ├── style.css         # Bootstrap styling
│   └── script.js         # Frontend logic and template handling
└── data/                  # Data storage
    ├── profiles/          # User profiles (JSON)
    ├── resume/           # Uploaded resumes
    ├── templates/        # Saved cover letter templates (JSON)
    └── cover_letters/    # Generated PDF files
```

## Generated Files

Cover letters are saved with unique naming for easy organization:
`FirstName_LastName_CoverLetter_CompanyName_UniqueID.pdf`

Example: `John_Doe_CoverLetter_TechCorp_A1B2C3D4.pdf`

**Features:**

- No duplicate files - each generation gets a unique 8-character ID
- Human-readable naming with company name included
- Direct PDF downloads - no metadata files needed
- Professional formatting with 0.75-inch margins

## Supported Resume Formats

- **PDF**: Extracts text using PyPDF2
- **DOCX**: Parses Word documents using python-docx
- **TXT**: Plain text files

## API Endpoints

- `GET /` - Main interface
- `GET/POST /api/profile` - User profile management
- `POST /api/resume` - Resume upload and parsing
- `GET /api/download-resume/<resume_id>` - Download uploaded resume
- `POST /api/generate-cover-letter-ai` - AI-powered cover letter generation
- `GET /api/download/<filename>` - Download cover letter PDF directly
- `GET /api/templates` - List all saved templates
- `POST /api/templates` - Create new cover letter template
- `DELETE /api/templates/<template_id>` - Delete a template

## Troubleshooting

### Common Issues

1. **GitHub Token Error**: Make sure your GitHub PAT has the necessary permissions for GitHub Models API
2. **Flask Secret Key Error**: Ensure `FLASK_SECRET_KEY` is set in your `.env` file
3. **PDF Generation Error**: Check that reportlab is properly installed (`pip install reportlab`)
4. **Resume Parse Error**: Ensure your resume file is not corrupted or password-protected
5. **Template Issues**: Templates are stored as JSON files in `data/templates/` - check file permissions
6. **AI Generation Fails**: Verify your GitHub token has access to the Models API

### Advanced Features

**Template System:**

- Templates support placeholders like `{company_name}`, `{job_title}`, `{location}`
- Smart replacement automatically fills in job details from the form
- Templates are stored locally and persist between sessions

**AI Enhancement:**

- Uses carefully crafted prompts for human-like, professional output
- Avoids copying resume content verbatim
- Focuses on company connection and authentic enthusiasm
- Generates unique content for each application

### Logs

Check the console output for detailed error messages and debugging information. The application logs all API calls and errors for troubleshooting.

## Tech Stack

- **Backend**: Flask (Python) with session management
- **AI**: GitHub Models API (OpenAI GPT-4o-mini) with enhanced prompts
- **PDF Generation**: ReportLab with custom 0.75-inch margins
- **Resume Parsing**: PyPDF2, python-docx for multiple file formats
- **Template System**: JSON-based storage with smart placeholder replacement
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **File Storage**: Local filesystem with organized directory structure
- **Configuration**: Environment variables via python-dotenv

## Key Improvements

- 🎯 **Smart Templates**: Reusable templates with automatic placeholder replacement
- 🤖 **Enhanced AI**: More human-like, authentic cover letter generation
- 📏 **Professional Formatting**: Optimized 0.75-inch PDF margins
- 🔄 **Streamlined Workflow**: No unnecessary metadata files, direct PDF handling
- ✅ **Visual Feedback**: Green status indicators for completed setup steps
- 🎨 **Responsive Design**: Works seamlessly on desktop and mobile devices

## License

MIT License - feel free to modify and use for your needs!
