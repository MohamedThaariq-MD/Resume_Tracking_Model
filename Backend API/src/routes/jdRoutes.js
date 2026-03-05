const express = require('express');
const router = express.Router();
const JobDescription = require('../models/JobDescription');

// @route   POST /api/jds
// @desc    Create a new Job Description
// @access  Public
router.post('/', async (req, res) => {
    try {
        const { title, description, requiredSkills } = req.body;
        const newJD = new JobDescription({ title, description, requiredSkills });
        const savedJD = await newJD.save();
        res.status(201).json(savedJD);
    } catch (error) {
        res.status(500).json({ message: 'Server Error', error: error.message });
    }
});

// @route   GET /api/jds
// @desc    Get all Job Descriptions
// @access  Public
router.get('/', async (req, res) => {
    try {
        const jds = await JobDescription.find().sort({ createdAt: -1 });
        res.json(jds);
    } catch (error) {
        res.status(500).json({ message: 'Server Error', error: error.message });
    }
});

module.exports = router;
