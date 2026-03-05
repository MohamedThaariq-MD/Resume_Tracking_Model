const mongoose = require('mongoose');

// Global flag to track DB state
let isDbConnected = false;

const connectDB = async () => {
    try {
        const mongoURI = process.env.MONGO_URI || 'mongodb://localhost:27017/resume-tracker';

        // Use shorter timeout so it doesn't hang forever
        const conn = await mongoose.connect(mongoURI, {
            serverSelectionTimeoutMS: 3000
        });

        isDbConnected = true;
        console.log(`MongoDB Connected: ${conn.connection.host}`);
    } catch (error) {
        console.warn(`[WARNING] MongoDB Connection Failed: ${error.message}`);
        console.warn(`[WARNING] Database features will be disabled until MongoDB is available.`);
        isDbConnected = false;
        // Commenting out process.exit(1) so the server can still run ML endpoints
        // process.exit(1); 
    }
};

module.exports = { connectDB, isConnected: () => isDbConnected };
