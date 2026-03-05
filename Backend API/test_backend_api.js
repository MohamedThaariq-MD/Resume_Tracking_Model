const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');
const path = require('path');

async function testUpload() {
    const url = 'http://localhost:5000/api/resumes/analyze';
    const filePath = 'd:\\ResumeTracker\\Backend API\\uploads\\1772449471168.pdf'; // Use an existing test file

    const formData = new FormData();
    formData.append('resume', fs.createReadStream(filePath));
    formData.append('jobTitle', 'Software Engineer');
    formData.append('jobDescription', 'We need a python developer.');
    formData.append('requiredSkills', '["python", "react"]');

    try {
        const response = await axios.post(url, formData, {
            headers: formData.getHeaders(),
        });
        console.log('Success:', response.status);
        console.log(response.data);
    } catch (error) {
        if (error.response) {
            console.log('Error Status:', error.response.status);
            console.log('Error Data:', error.response.data);
        } else {
            console.log('Error Message:', error.message);
        }
    }
}

testUpload();
