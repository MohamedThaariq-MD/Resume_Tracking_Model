const express = require('express');
const router = express.Router();
const multer = require('multer');
const Resume = require('../models/Resume');
const path = require('path');
const fs = require('fs');
const axios = require('axios'); // We'll need axios to call the ML service later
const FormData = require('form-data');
const { isConnected } = require('../config/db');
const { generateImprovementSuggestions, handleChatQuery } = require('../services/llmService');
// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = 'uploads/';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir);
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + path.extname(file.originalname)); // Appending extension
    }
});

const upload = multer({ storage: storage });
const memoryUpload = multer({ storage: multer.memoryStorage() });

// @route   POST /api/resumes/upload
// @desc    Upload a resume file
// @access  Public
router.post('/upload', upload.single('resume'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ message: 'No file uploaded' });
        }
        // Placeholder for calling ML service later
        // 1. Send file path to Python ML service
        // 2. Python service returns extracted text, skills, and ATS score against a JD

        // For now, just save basic info
        const newResume = new Resume({
            candidateName: req.body.candidateName || 'Unknown',
            filePath: req.file.path,
        });

        const savedResume = await newResume.save();
        res.status(201).json(savedResume);
    } catch (error) {
        res.status(500).json({ message: 'Server Error', error: error.message });
    }
});

// @route   POST /api/resumes/analyze
// @desc    Upload a resume file and proxy analysis to the ML backend
// @access  Public
router.post('/analyze', memoryUpload.single('resume'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ message: 'No file uploaded' });
        }

        const { jobTitle, jobDescription, requiredSkills } = req.body;

        // 1. Build and send multipart/form-data to FastAPI ML Engine
        const mlServiceUrl = process.env.ML_SERVICE_URL || 'http://127.0.0.1:8000';

        try {
            // First pass to ML parser to extract text
            const formData = new FormData();
            formData.append('file', req.file.buffer, { filename: req.file.originalname });

            const parseRes = await axios.post(`${mlServiceUrl}/analyze_resume`, formData, {
                headers: formData.getHeaders()
            });
            const extractedRawText = parseRes.data.raw_text || "fallback text";

            // Second pass to ML ATS Scorer
            // The python function expects a Form payload for resume_text, and JSON for req

            const atsFormData = new FormData();
            atsFormData.append('resume_text', extractedRawText);

            const reqData = JSON.stringify({
                title: jobTitle || "Candidate Target Role",
                description: jobDescription || "",
                required_skills: requiredSkills ? (typeof requiredSkills === 'string' ? JSON.parse(requiredSkills) : requiredSkills) : []
            });
            atsFormData.append('req', reqData); // Pydantic expects `req` string or json

            // To support FastAPI mix of Form and JSON body, we adapt axios
            const atsRes = await axios.post(`${mlServiceUrl}/calculate_ats`, atsFormData, {
                headers: atsFormData.getHeaders()
            });

            const finalResponse = {
                filename: req.file.originalname,
                ...parseRes.data,
                ...atsRes.data
            };

            try {
                const missing = atsRes.data.missing_skills || [];
                const suggestions = await generateImprovementSuggestions(
                    extractedRawText,
                    reqData,
                    atsRes.data.ats_score,
                    missing
                );
                finalResponse.improvement_suggestions = suggestions;
            } catch (llmError) {
                console.error("LLM Error:", llmError);
                finalResponse.improvement_suggestions = "💡 Error generating insights from the AI model. Please try again later.";
            }

            return res.status(200).json(finalResponse);

        } catch (mlError) {
            console.error(mlError.response?.data || mlError);

            // Forward the actual error from ML service if available
            if (mlError.response) {
                const status = mlError.response.status;
                const message = mlError.response.data?.detail || 'Error from ML Service';
                return res.status(status).json({ message: message });
            }

            return res.status(502).json({ message: 'ML Service failed to respond', details: mlError.message });
        }

    } catch (error) {
        res.status(500).json({ message: 'Server Error', error: error.message });
    }
});

// @route   GET /api/resumes
// @desc    Get all resumes
// @access  Public
router.get('/', async (req, res) => {
    try {
        const resumes = await Resume.find().sort({ createdAt: -1 });
        res.json(resumes);
    } catch (error) {
        res.status(500).json({ message: 'Server Error', error: error.message });
    }
});

// @route   POST /api/resumes/chat
// @desc    Chat with LLM about job description and resume
// @access  Public
router.post('/chat', async (req, res) => {
    try {
        const { resumeText, jobDescription, chatHistory, message } = req.body;
        if (!message) {
            return res.status(400).json({ message: 'Message is required' });
        }

        const reply = await handleChatQuery(resumeText || "", jobDescription || "", chatHistory || [], message);
        res.status(200).json({ reply });
    } catch (error) {
        console.error("Chat Route Error:", error);
        res.status(500).json({ message: 'Server Error during chat', error: error.message });
    }
});

// @route   POST /api/resumes/generate
// @desc    Generate an ATS-friendly resume via ML service
// @access  Public
router.post('/generate', async (req, res) => {
    try {
        const { resumeText, jobDescription } = req.body;
        if (!resumeText || !jobDescription) {
            return res.status(400).json({ message: 'Resume text and job description are required' });
        }

        const mlServiceUrl = process.env.ML_SERVICE_URL || 'http://127.0.0.1:8000';

        const response = await axios.post(`${mlServiceUrl}/llm/generate_resume`, {
            jd_text: jobDescription,
            resume_text: resumeText
        });

        res.status(200).json(response.data);
    } catch (error) {
        console.error("Generate Resume Route Error:", error.response?.data || error.message);
        res.status(500).json({ message: 'Server Error during resume generation', error: error.message });
    }
});

// @route   POST /api/resumes/magic-edit
// @desc    Upload a DOCX resume and intelligently replace missing skills
// @access  Public
router.post('/magic-edit', memoryUpload.single('resume'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ message: 'No file uploaded' });
        }
        if (!req.file.originalname.endsWith('.docx')) {
            return res.status(400).json({ message: 'Only DOCX files are supported for Magic Edit' });
        }

        const { resumeText, missingSkills } = req.body;
        if (!resumeText || !missingSkills) {
            return res.status(400).json({ message: 'Resume text and missing skills are required' });
        }

        const mlServiceUrl = process.env.ML_SERVICE_URL || 'http://127.0.0.1:8000';

        const formData = new FormData();
        formData.append('file', req.file.buffer, { filename: req.file.originalname });
        formData.append('resume_text', resumeText);
        formData.append('missing_skills', missingSkills); // Should be a JSON string of array

        const response = await axios.post(`${mlServiceUrl}/llm/magic_edit`, formData, {
            headers: formData.getHeaders(),
            responseType: 'arraybuffer' // Expect a binary file back
        });

        // Set headers so the client sees it as a file download
        res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
        res.setHeader('Content-Disposition', `attachment; filename=Magic_${req.file.originalname}`);
        res.send(response.data);

    } catch (error) {
        console.error("Magic Edit Route Error:", error.response?.data?.toString() || error.message);

        if (error.response && error.response.status !== 500) {
            const status = error.response.status;
            let message = 'Error from ML Service';
            try {
                message = JSON.parse(error.response.data.toString()).detail || message;
            } catch (e) { }
            return res.status(status).json({ message: message });
        }
        res.status(500).json({ message: 'Server Error during magic edit', error: error.message });
    }
});

module.exports = router;
