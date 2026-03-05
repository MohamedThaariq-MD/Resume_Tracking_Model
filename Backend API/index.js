const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { connectDB, isConnected } = require('./src/config/db');

// Load environment variables
dotenv.config();

// Connect to MongoDB
connectDB(); // Attempt to connect, but won't exit if DB is unavailable

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Basic route
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok', message: 'Backend API is running' });
});

// Import specific routes
app.use('/api/resumes', require('./src/routes/resumeRoutes'));
app.use('/api/jds', require('./src/routes/jdRoutes'));

const PORT = process.env.PORT || 5000;

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on port ${PORT}`);
});
