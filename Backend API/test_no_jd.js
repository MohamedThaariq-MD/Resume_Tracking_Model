const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

async function testUploadWithoutJD() {
    const url = 'http://localhost:5000/api/resumes/analyze';
    const filePath = 'd:\\ResumeTracker\\Backend API\\uploads\\1772449471168.pdf'; // Use an existing test file

    if (!fs.existsSync(filePath)) {
        console.log("Please copy a test pdf into the uploads folder.");
        return;
    }

    const formData = new FormData();
    formData.append('resume', fs.createReadStream(filePath));
    // Notice we are NOT appending jobTitle, jobDescription, or requiredSkills

    try {
        const response = await axios.post(url, formData, {
            headers: formData.getHeaders(),
        });
        console.log('Success:', response.status);
        console.log("Extracted Skills count:", response.data.extracted_skills?.length);
        console.log("Suggestions prefix:", response.data.improvement_suggestions.substring(0, 100));
    } catch (error) {
        if (error.response) {
            console.log('Error Status:', error.response.status);
            console.log('Error Data:', error.response.data);
        } else {
            console.log('Error Message:', error.message);
        }
    }
}

testUploadWithoutJD();
