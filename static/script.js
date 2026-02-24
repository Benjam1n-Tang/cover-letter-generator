// Cover Letter Generator JavaScript

class CoverLetterGenerator {
  constructor() {
    this.profileLoaded = false;
    this.resumeUploaded = false;
    this.setupEventListeners();
    this.loadInitialData();
  }

  setupEventListeners() {
    // Profile form
    document
      .getElementById('saveProfileBtn')
      .addEventListener('click', () => this.saveProfile());

    // Resume upload
    document
      .getElementById('uploadResumeBtn')
      .addEventListener('click', () => this.uploadResume());

    // Resume PDF generation
    document
      .getElementById('generateResumeBtn')
      .addEventListener('click', () => this.generateResumePdf());

    // Cover letter generation
    document
      .getElementById('generateBtn')
      .addEventListener('click', () => this.showGenerateSection());
    document
      .getElementById('coverLetterForm')
      .addEventListener('submit', (e) => this.generateCoverLetter(e));

    // Cover letter editing
    document
      .getElementById('savePdfBtn')
      .addEventListener('click', () => this.saveCoverLetterPdf());
    document
      .getElementById('backToFormBtn')
      .addEventListener('click', () => this.backToForm());
  }

  async loadInitialData() {
    await this.loadProfile();
    await this.loadCoverLetters();
    this.updateUI();
  }

  async loadProfile() {
    try {
      const response = await fetch('/api/profile');
      if (response.ok) {
        const profile = await response.json();
        if (profile && profile.first_name) {
          this.populateProfileForm(profile);
          this.profileLoaded = true;
          this.showAlert('Profile loaded successfully!', 'success');
        }
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  }

  populateProfileForm(profile) {
    document.getElementById('firstName').value = profile.first_name || '';
    document.getElementById('lastName').value = profile.last_name || '';
    document.getElementById('email').value = profile.email || '';
    document.getElementById('phone').value = profile.phone || '';
    document.getElementById('address').value = profile.address || '';
    document.getElementById('city').value = profile.city || '';
    document.getElementById('state').value = profile.state || '';
    document.getElementById('zipCode').value = profile.zip_code || '';
  }

  async saveProfile() {
    const profileData = {
      first_name: document.getElementById('firstName').value.trim(),
      last_name: document.getElementById('lastName').value.trim(),
      email: document.getElementById('email').value.trim(),
      phone: document.getElementById('phone').value.trim(),
      address: document.getElementById('address').value.trim(),
      city: document.getElementById('city').value.trim(),
      state: document.getElementById('state').value.trim(),
      zip_code: document.getElementById('zipCode').value.trim(),
    };

    // Validate required fields
    const requiredFields = [
      'first_name',
      'last_name',
      'email',
      'phone',
      'address',
      'city',
      'state',
      'zip_code',
    ];
    const missingFields = requiredFields.filter((field) => !profileData[field]);

    if (missingFields.length > 0) {
      this.showAlert(
        `Please fill in all required fields: ${missingFields.join(', ')}`,
        'danger',
      );
      return;
    }

    try {
      const response = await fetch('/api/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      });

      if (response.ok) {
        this.profileLoaded = true;
        this.showAlert('Profile saved successfully!', 'success');
        bootstrap.Modal.getInstance(
          document.getElementById('profileModal'),
        ).hide();
        this.updateUI();
      } else {
        const error = await response.json();
        this.showAlert(error.error || 'Error saving profile', 'danger');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      this.showAlert('Error saving profile', 'danger');
    }
  }

  async uploadResume() {
    const fileInput = document.getElementById('resumeFile');
    const file = fileInput.files[0];

    if (!file) {
      this.showAlert('Please select a resume file', 'danger');
      return;
    }

    const formData = new FormData();
    formData.append('resume', file);

    const uploadBtn = document.getElementById('uploadResumeBtn');
    const spinner = document.getElementById('uploadSpinner');

    uploadBtn.disabled = true;
    spinner.style.display = 'inline-block';

    try {
      const response = await fetch('/api/resume', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        this.resumeUploaded = true;
        this.showAlert('Resume uploaded successfully!', 'success');
        bootstrap.Modal.getInstance(
          document.getElementById('resumeModal'),
        ).hide();
        this.updateUI();

        // Reset file input
        fileInput.value = '';
      } else {
        const error = await response.json();
        this.showAlert(error.error || 'Error uploading resume', 'danger');
      }
    } catch (error) {
      console.error('Error uploading resume:', error);
      this.showAlert('Error uploading resume', 'danger');
    } finally {
      uploadBtn.disabled = false;
      spinner.style.display = 'none';
    }
  }

  async generateResumePdf() {
    if (!this.profileLoaded) {
      this.showAlert('Please set up your profile first', 'warning');
      return;
    }

    if (!this.resumeUploaded) {
      this.showAlert('Please upload your resume first', 'warning');
      return;
    }

    const generateBtn = document.getElementById('generateResumeBtn');
    const originalText = generateBtn.innerHTML;

    generateBtn.disabled = true;
    generateBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm me-1"></span>Generating...';

    try {
      const response = await fetch('/api/generate-resume-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      if (response.ok) {
        const result = await response.json();
        this.showAlert('Resume PDF generated successfully!', 'success');

        // Auto-download the generated resume PDF
        this.downloadResumePdf(result.resume_id);
      } else {
        const error = await response.json();
        this.showAlert(error.error || 'Error generating resume PDF', 'danger');
      }
    } catch (error) {
      console.error('Error generating resume PDF:', error);
      this.showAlert('Error generating resume PDF', 'danger');
    } finally {
      generateBtn.disabled = false;
      generateBtn.innerHTML = originalText;
    }
  }

  downloadResumePdf(resumeId) {
    window.open(`/api/download-resume/${resumeId}`, '_blank');
  }

  showGenerateSection() {
    if (!this.profileLoaded) {
      this.showAlert('Please set up your profile first', 'warning');
      return;
    }

    if (!this.resumeUploaded) {
      this.showAlert('Please upload your resume first', 'warning');
      return;
    }

    document.getElementById('generateSection').style.display = 'block';
    document
      .getElementById('generateSection')
      .scrollIntoView({ behavior: 'smooth' });
  }

  async generateCoverLetter(event) {
    event.preventDefault();

    const formData = {
      hiring_manager: document.getElementById('hiringManager').value.trim(),
      hiring_manager_role: document
        .getElementById('hiringManagerRole')
        .value.trim(),
      job_role: document.getElementById('jobRole').value.trim(),
      company_name: document.getElementById('companyName').value.trim(),
      company_address: document.getElementById('companyAddress').value.trim(),
      company_city: document.getElementById('companyCity').value.trim(),
      company_state: document.getElementById('companyState').value.trim(),
      company_zip: document.getElementById('companyZip').value.trim(),
      job_description: document.getElementById('jobDescription').value.trim(),
    };

    // Validate required fields
    if (
      !formData.job_role ||
      !formData.company_name ||
      !formData.company_city ||
      !formData.company_state ||
      !formData.job_description
    ) {
      this.showAlert(
        'Please fill in all required job information fields',
        'danger',
      );
      return;
    }

    // Validate hiring manager fields - if one is provided, both must be provided
    if (
      (formData.hiring_manager && !formData.hiring_manager_role) ||
      (!formData.hiring_manager && formData.hiring_manager_role)
    ) {
      this.showAlert(
        'If you provide a hiring manager name, you must also provide their role',
        'danger',
      );
      return;
    }

    const generateBtn = document.getElementById('generateCoverLetterBtn');
    const spinner = document.getElementById('generateSpinner');

    generateBtn.disabled = true;
    spinner.style.display = 'inline-block';
    generateBtn.classList.add('loading');

    try {
      const response = await fetch('/api/generate-cover-letter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();

        // Show the editor with generated text
        this.showEditor(
          result.cover_letter_text,
          result.company_name,
          result.company_location,
          result.company_address,
          result.hiring_manager,
          result.hiring_manager_role,
          result.job_role,
        );

        this.showAlert(
          'Cover letter generated! Please review and edit before saving.',
          'success',
        );
      } else {
        const error = await response.json();
        this.showAlert(
          error.error || 'Error generating cover letter',
          'danger',
        );
      }
    } catch (error) {
      console.error('Error generating cover letter:', error);
      this.showAlert('Error generating cover letter', 'danger');
    } finally {
      generateBtn.disabled = false;
      spinner.style.display = 'none';
      generateBtn.classList.remove('loading');
    }
  }

  showEditor(
    coverLetterText,
    companyName,
    companyLocation,
    companyAddress = '',
    hiringManager = '',
    hiringManagerRole = '',
    jobRole = '',
  ) {
    // Hide generate section and show editor
    document.getElementById('generateSection').style.display = 'none';
    document.getElementById('editorSection').style.display = 'block';

    // Populate editor
    document.getElementById('coverLetterEditor').value = coverLetterText;

    // Build company info display
    let companyInfo = `${companyName}`;
    if (jobRole) {
      companyInfo += ` - ${jobRole}`;
    }
    companyInfo += ` - ${companyLocation}`;

    document.getElementById('companyInfo').textContent = companyInfo;

    // Store data for later use
    this.currentCoverLetter = {
      text: coverLetterText,
      company: companyName,
      company_location: companyLocation,
      company_address: companyAddress,
      hiring_manager: hiringManager,
      hiring_manager_role: hiringManagerRole,
      job_role: jobRole,
    };

    // Scroll to editor
    document
      .getElementById('editorSection')
      .scrollIntoView({ behavior: 'smooth' });
  }

  backToForm() {
    document.getElementById('editorSection').style.display = 'none';
    document.getElementById('generateSection').style.display = 'block';
    document
      .getElementById('generateSection')
      .scrollIntoView({ behavior: 'smooth' });
  }

  async saveCoverLetterPdf() {
    const editedText = document
      .getElementById('coverLetterEditor')
      .value.trim();

    if (!editedText) {
      this.showAlert('Please enter cover letter content', 'danger');
      return;
    }

    if (!this.currentCoverLetter) {
      this.showAlert('No cover letter data available', 'danger');
      return;
    }

    const savePdfBtn = document.getElementById('savePdfBtn');
    const spinner = document.getElementById('savePdfSpinner');

    savePdfBtn.disabled = true;
    spinner.style.display = 'inline-block';

    try {
      const response = await fetch('/api/generate-cover-letter-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cover_letter_text: editedText,
          company_name: this.currentCoverLetter.company,
          company_location: this.currentCoverLetter.company_location,
          company_address: this.currentCoverLetter.company_address,
          hiring_manager: this.currentCoverLetter.hiring_manager,
          hiring_manager_role: this.currentCoverLetter.hiring_manager_role,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        this.showAlert('Cover letter PDF saved successfully!', 'success');

        // Auto-download the PDF
        this.downloadCoverLetter(result.cover_letter_id);

        // Refresh cover letters list
        await this.loadCoverLetters();

        // Reset form and go back
        document.getElementById('coverLetterForm').reset();
        this.backToForm();
      } else {
        const error = await response.json();
        this.showAlert(error.error || 'Error saving PDF', 'danger');
      }
    } catch (error) {
      console.error('Error saving PDF:', error);
      this.showAlert('Error saving PDF', 'danger');
    } finally {
      savePdfBtn.disabled = false;
      spinner.style.display = 'none';
    }
  }

  async loadCoverLetters() {
    try {
      const response = await fetch('/api/cover-letters');
      if (response.ok) {
        const coverLetters = await response.json();
        this.displayCoverLetters(coverLetters);
      }
    } catch (error) {
      console.error('Error loading cover letters:', error);
    }
  }

  displayCoverLetters(coverLetters) {
    const container = document.getElementById('coverLettersList');

    if (coverLetters.length === 0) {
      container.innerHTML =
        '<p class="text-muted">No cover letters generated yet.</p>';
      return;
    }

    const html = coverLetters
      .map(
        (cl) => `
            <div class="cover-letter-item fade-in">
                <h6>${cl.company_name}</h6>
                <p class="text-muted mb-2">${cl.location}</p>
                <p class="text-muted mb-2" style="font-size: 0.8rem;">
                    ${new Date(cl.created_at).toLocaleDateString()}
                </p>
                <button class="btn btn-primary btn-sm" onclick="app.downloadCoverLetter('${cl.id}')">
                    <i class="fas fa-download me-1"></i>Download PDF
                </button>
            </div>
        `,
      )
      .join('');

    container.innerHTML = html;
  }

  downloadCoverLetter(coverletterId) {
    window.open(`/api/download/${coverletterId}`, '_blank');
  }

  updateUI() {
    // Update setup step indicators
    const profileStep = document.querySelector('.setup-step:nth-child(1)');
    const resumeStep = document.querySelector('.setup-step:nth-child(2)');
    const generateStep = document.querySelector('.setup-step:nth-child(3)');

    // Update profile step
    if (this.profileLoaded) {
      profileStep.querySelector('.step-number').style.background =
        'var(--success-color)';
      profileStep.querySelector('button').innerHTML =
        '<i class="fas fa-check me-1"></i>Profile Setup';
      profileStep
        .querySelector('button')
        .classList.remove('btn-outline-primary');
      profileStep.querySelector('button').classList.add('btn-success');
    }

    // Update resume step
    if (this.resumeUploaded) {
      resumeStep.querySelector('.step-number').style.background =
        'var(--success-color)';
      resumeStep.querySelector('button').innerHTML =
        '<i class="fas fa-check me-1"></i>Resume Uploaded';
      resumeStep
        .querySelector('button')
        .classList.remove('btn-outline-primary');
      resumeStep.querySelector('button').classList.add('btn-success');

      // Enable resume PDF generation button
      document.getElementById('generateResumeBtn').disabled = false;
    }

    // Enable generate button if both profile and resume are ready
    if (this.profileLoaded && this.resumeUploaded) {
      generateStep.querySelector('button').disabled = false;
      generateStep.querySelector('.step-number').style.background =
        'var(--success-color)';
    }
  }

  showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer');
    const alertId = 'alert_' + Date.now();

    const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert" id="${alertId}">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

    alertContainer.insertAdjacentHTML('beforeend', alertHtml);

    // Auto-dismiss after duration
    if (duration > 0) {
      setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
          const alert = new bootstrap.Alert(alertElement);
          alert.close();
        }
      }, duration);
    }
  }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.app = new CoverLetterGenerator();
});
