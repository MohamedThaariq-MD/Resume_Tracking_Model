const { GoogleGenAI } = require('@google/genai');

// Initialize Gemini client conditionally to not crash if key is missing initially.
let ai = null;

function initializeAI() {
    if (!ai && process.env.GEMINI_API_KEY) {
        ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
    }
    return ai;
}

/**
 * Generate improvement suggestions for a resume based on the Job Description and calculated scores.
 * @param {string} resumeText - The parsed text of the candidate's resume
 * @param {string} jobDescription - The job description
 * @param {number} atsScore - The calculated ATS score
 * @param {Array<string>} missingSkills - The missing skills identified by the ML engine
 * @returns {Promise<string>}
 */
async function generateImprovementSuggestions(resumeText, jobDescription, atsScore, missingSkills) {
    const client = initializeAI();
    if (!client) {
        return "💡 API Key missing. Please add the GEMINI_API_KEY in the .env file to enable AI suggestions.";
    }

    const hasJD = !!jobDescription && jobDescription.trim() !== "" && jobDescription.trim() !== "{}";
    const prompt = hasJD ? `
You are an expert technical recruiter and ATS system optimizer.
Please provide 3-4 specific, actionable bullet points to improve the following resume for the provided Job Description.

Target Job Description:
${jobDescription}

Candidate Resume:
${extrapolateResume(resumeText)}

Current ATS Score: ${atsScore}/100
Missing Skills (Identified by basic semantic check): ${missingSkills && missingSkills.length ? missingSkills.join(", ") : "None"}

Keep your response concise and formatted in markdown bullet points. Do not include introductory text like "Here are some suggestions:" - just provide the bullet points directly.
` : `
You are an expert technical recruiter and resume reviewer.
Please provide 3-4 specific, actionable bullet points to generally improve the formatting, impact, and ATS-readability of the following resume.

Candidate Resume:
${extrapolateResume(resumeText)}

Current General Processing Score: ${atsScore}/100

Keep your response concise and formatted in markdown bullet points. Do not include introductory text like "Here are some suggestions:" - just provide the bullet points directly. Focus on action verbs, quantifiable achievements, and clear formatting.
`;

    try {
        const response = await client.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: prompt,
        });
        return response.text;
    } catch (error) {
        console.error("Gemini Suggestion Error:", error);
        return "💡 Error generating insights from the AI model. Please try again later.";
    }
}

/**
 * Handles conversational queries about the resume and job description.
 * @param {string} resumeText
 * @param {string} jobDescription
 * @param {Array<{role: string, text: string}>} chatHistory - Previous chat messages
 * @param {string} userMessage - The new question from the user
 */
async function handleChatQuery(resumeText, jobDescription, chatHistory, userMessage) {
    const client = initializeAI();
    if (!client) {
        return "💡 API Key missing. Please add the GEMINI_API_KEY in the .env file to enable AI chat.";
    }

    const hasJD = !!jobDescription && jobDescription.trim() !== "" && jobDescription.trim() !== "{}";
    const systemInstruction = hasJD ? `
You are an expert technical recruiter and AI assistant for a Resume Tracking application.
Your goal is to help candidates improve their resume and understand the job description they are applying for.

Here is the context for this conversation:
Job Description:
${jobDescription}

Candidate Resume:
${extrapolateResume(resumeText)}

Please answer the user's question concisely, referencing the context above when appropriate.
` : `
You are an expert technical recruiter and AI assistant for a Resume Tracking application.
Your goal is to help candidates improve the formatting, readability, and impact of their resume generally.

Here is the context for this conversation:
Candidate Resume:
${extrapolateResume(resumeText)}

Please answer the user's question concisely, referencing the context above when appropriate. Focus your advice on general resume best practices.
`;

    try {
        // Format the chat history for Gemini
        const contents = chatHistory.map(msg => ({
            role: msg.role === 'user' ? 'user' : 'model',
            parts: [{ text: msg.text }]
        }));

        // Add the new user message
        contents.push({
            role: 'user',
            parts: [{ text: systemInstruction + "\n\nUser Question: " + userMessage }]
        });

        const response = await client.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: contents,
        });

        return response.text;
    } catch (error) {
        console.error("Gemini Chat Error:", error);
        return "💡 Error generating a response from the AI model. Please try again later.";
    }
}

function extrapolateResume(text) {
    if (!text) return "No resume text provided.";
    return text.length > 2000 ? text.substring(0, 2000) + "..." : text;
}

module.exports = {
    generateImprovementSuggestions,
    handleChatQuery
};
