import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, AlertCircle, Loader, Briefcase, GraduationCap, ChevronRight, Zap, TrendingUp, Send, User, Bot, MessageSquare, Download } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from './components/ui/Card';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0f1d] to-[#121b2d] text-white font-sans relative overflow-x-hidden flex flex-col items-center">
      {/* Hero Header */}
      <header className="w-full pt-16 pb-10 flex flex-col items-center justify-center text-center px-4">
        <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6 tracking-tight">
          Resume Tracking System
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl px-4">
          Optimize your resume for ATS and find hidden skill gaps using advanced AI.
        </p>
      </header>

      <main className="w-full max-w-6xl px-6 pb-16 grid grid-cols-1 lg:grid-cols-2 gap-8 flex-grow">
        {/* Left Panel: Upload Form */}
        <div className="flex flex-col h-full min-h-[500px]">
          <UploadPanel onAnalyze={setAnalysisResult} loading={loading} setLoading={setLoading} />
        </div>

        {/* Right Panel: Dashboard Bento Grid or Empty State */}
        <div className="flex flex-col h-full">
          <AnimatePresence mode="wait">
            {!analysisResult ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full w-full"
              >
                <Card className="flex flex-col items-center justify-center text-center h-full min-h-[500px]">
                  <div className="w-20 h-20 bg-blue-500/10 rounded-full flex items-center justify-center mb-6 ring-8 ring-blue-500/5">
                    <TrendingUp className="w-10 h-10 text-blue-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-200 mb-2">Ready to analyze</h3>
                  <p className="text-slate-400 text-base max-w-xs">Upload your resume and job description to see the AI analysis.</p>
                </Card>
              </motion.div>
            ) : (
              <motion.div key="dashboard" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="h-full">
                <Dashboard result={analysisResult} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

function UploadPanel({ onAnalyze, loading, setLoading }) {
  const [file, setFile] = useState(null);
  const [jobDesc, setJobDesc] = useState("");
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleAnalyze = async () => {
    if (!file) return setError("Please attach a PDF resume.");
    // Job Description is now optional, so no error here.

    setLoading(true);
    setError(null);
    onAnalyze(null);

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("jobDescription", jobDesc);

    try {
      const res = await axios.post(`${API_BASE_URL}/api/resumes/analyze`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      onAnalyze({ ...res.data, jobDescription: jobDesc, originalFile: file });
    } catch (err) {
      setError(err.response?.data?.message || err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="flex flex-col h-full space-y-6">
      <div className="flex items-center space-x-3 mb-2">
        <div className="p-2 bg-blue-500/10 rounded-lg">
          <Upload className="w-6 h-6 text-blue-400" />
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Upload Details</h2>
      </div>

      <div className="flex-shrink-0">
        <label className="block text-sm font-semibold text-slate-300 mb-2">Resume (PDF)</label>
        <div
          className={`relative h-40 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group
            ${isDragging ? 'border-blue-500 bg-blue-500/10 scale-[1.02]' : file ? 'border-blue-500/50 bg-blue-500/5' : 'border-slate-700 hover:border-blue-500/50 hover:bg-slate-800/50'}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile?.type === 'application/pdf') {
              setFile(droppedFile);
              setError(null);
            } else {
              setError("Only PDF files are allowed.");
            }
          }}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            className="hidden"
            accept=".pdf"
            ref={fileInputRef}
            onChange={(e) => {
              const selectedFile = e.target.files?.[0];
              if (selectedFile?.type === 'application/pdf') {
                setFile(selectedFile);
                setError(null);
              } else if (selectedFile) {
                setError("Only PDF files are allowed.");
              }
              // Reset file input value to allow selecting same file again if removed
              e.target.value = null;
            }}
          />
          {!file ? (
            <>
              <div className="p-3 bg-slate-800 rounded-full mb-3 group-hover:scale-110 transition-transform duration-300">
                <FileText className="w-6 h-6 text-slate-400 group-hover:text-blue-400 transition-colors" />
              </div>
              <span className="text-sm font-medium text-slate-400 group-hover:text-slate-300 transition-colors">
                <span className="text-blue-400">Click to upload</span> or drag and drop
              </span>
              <span className="text-xs text-slate-500 mt-1">PDF (max. 10MB)</span>
            </>
          ) : (
            <div className="flex flex-col items-center">
              <CheckCircle className="w-10 h-10 text-emerald-400 mb-3" />
              <span className="font-medium text-emerald-200 truncate w-full px-8 text-center">{file.name}</span>
              <span className="text-xs text-slate-500 mt-2 flex items-center hover:text-red-400" onClick={(e) => { e.stopPropagation(); setFile(null); }}>
                Click to remove
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="flex-grow flex flex-col">
        <label className="block text-sm font-semibold text-slate-300 mb-2">Job Description (Optional)</label>
        <textarea
          className="flex-grow w-full bg-slate-900/50 border border-slate-700/80 rounded-xl p-4 text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all resize-none placeholder-slate-500 hover:border-slate-600 focus:border-transparent min-h-[160px]"
          placeholder="Paste the job requirements here..."
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
        />
      </div>

      {error && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-center shadow-lg">
          <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" /> {error}
        </motion.div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={loading || !file}
        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-4 rounded-xl shadow-lg shadow-blue-500/20 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600 text-base"
      >
        {loading ? <><Loader className="w-5 h-5 mr-3 animate-spin" /> Analyzing...</> : (jobDesc ? "Evaluate Compatibility" : "Analyze Resume")}
      </button>
    </Card>
  );
}

function Dashboard({ result }) {
  const [generatingResume, setGeneratingResume] = useState(false);
  const [generatedResume, setGeneratedResume] = useState("");
  const [magicEditing, setMagicEditing] = useState(false);
  const [magicEditError, setMagicEditError] = useState("");

  const handleGenerateResume = async () => {
    setGeneratingResume(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/api/resumes/generate`, {
        resumeText: result.raw_text,
        jobDescription: result.jobDescription || ""
      });
      setGeneratedResume(res.data.generated_resume || "No content generated.");
    } catch (err) {
      console.error("Failed to generate resume:", err);
      setGeneratedResume("Error generating resume. Please make sure the ML service is running and try again.");
    } finally {
      setGeneratingResume(false);
    }
  };

  const handleMagicEdit = async () => {
    if (!result.originalFile) {
      setMagicEditError("Original file is missing. Please re-upload your resume.");
      return;
    }

    if (!result.originalFile.name.endsWith('.docx')) {
      setMagicEditError("Magic Edit is currently only supported for .docx (Word) files. Please upload a Word document.");
      return;
    }

    const missingSkills = result.missing_skills || result.ml_analysis?.missing_skills || [];
    if (missingSkills.length === 0) {
      setMagicEditError("You aren't missing any skills! Magic Edit is not needed.");
      return;
    }

    setMagicEditing(true);
    setMagicEditError("");

    const formData = new FormData();
    formData.append("resume", result.originalFile);
    formData.append("resumeText", result.raw_text);
    formData.append("missingSkills", JSON.stringify(missingSkills));

    try {
      const res = await axios.post(`${API_BASE_URL}/api/resumes/magic-edit`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        responseType: 'arraybuffer'
      });

      // Force browser to download the binary arraybuffer
      const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const element = document.createElement("a");
      element.href = URL.createObjectURL(blob);
      element.download = `ATS_Optimized_${result.originalFile.name}`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      setTimeout(() => URL.revokeObjectURL(element.href), 100);

    } catch (err) {
      console.error("Failed to magic edit resume:", err);
      let errorMsg = "An unknown error occurred during Magic Edit.";
      // Try to parse arraybuffer error to string
      if (err.response && err.response.data) {
        try {
          const decodedError = JSON.parse(new TextDecoder().decode(err.response.data));
          errorMsg = decodedError.message || errorMsg;
        } catch (e) { }
      }
      setMagicEditError(errorMsg);
    } finally {
      setMagicEditing(false);
    }
  };

  const downloadAsText = () => {
    const element = document.createElement("a");
    const file = new Blob([generatedResume], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = "ATS_Optimized_Resume.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const hasJD = !!result.jobDescription;
  const ats = result.ats_score || result.ml_analysis?.ats_score || 0;
  const matchScoreRaw = result.match_score || result.ml_analysis?.match_score || 0;

  const missing = result.missing_skills || result.ml_analysis?.missing_skills || [];
  const matching = result.matching_skills || result.ml_analysis?.matching_skills || [];
  const expParsed = result.experience_parsed || result.ml_analysis?.experience_parsed || 0;
  const eduParsedArr = result.education_parsed || result.ml_analysis?.education_parsed || [];
  const eduParsed = eduParsedArr.length ? eduParsedArr.join(', ') : "Not Detected";

  let matchLabel = hasJD ? "Moderate Match" : "Moderate ATS Score";
  let matchColor = "from-amber-400 to-orange-500";
  let matchBg = "bg-amber-500/10";
  let matchBorder = "border-amber-500/20";
  let textColor = "text-amber-400";

  const primaryScore = hasJD ? matchScoreRaw : ats;

  if (primaryScore >= 80) {
    matchLabel = hasJD ? "Strong Match" : "Strong ATS Score";
    matchColor = "from-emerald-400 to-teal-500";
    matchBg = "bg-emerald-500/10";
    matchBorder = "border-emerald-500/20";
    textColor = "text-emerald-400";
  } else if (primaryScore <= 40) {
    matchLabel = hasJD ? "Weak Match" : "Weak ATS Score";
    matchColor = "from-rose-400 to-red-500";
    matchBg = "bg-rose-500/10";
    matchBorder = "border-rose-500/20";
    textColor = "text-rose-400";
  }

  const totalSkills = missing.length + matching.length;
  const skillMatchPct = totalSkills === 0 ? 0 : Math.round((matching.length / totalSkills) * 100);

  return (
    <Card className="h-full overflow-y-auto pr-2 custom-scrollbar flex flex-col space-y-6">
      {/* Top Header */}
      <div className="flex flex-wrap gap-4 items-center justify-between pb-4 border-b border-white/5">
        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-1">{hasJD ? "ATS Report" : "General Analysis"}</h2>
          <p className="text-slate-400 text-sm">For <span className="text-slate-200 font-medium">{result.filename || "Uploaded File"}</span></p>
        </div>
        <div className={`px-4 py-2 rounded-full ${matchBg} border ${matchBorder} ${textColor} font-bold text-sm flex items-center shadow-sm backdrop-blur-md`}>
          <CheckCircle className="w-sm h-4 mr-2" /> {matchLabel}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-grow">
        {/* Main Score Card */}
        <div className="md:col-span-2 bg-gradient-to-br from-white/5 to-transparent border border-white/5 rounded-2xl p-6 relative overflow-hidden backdrop-blur-sm shadow-inner flex flex-col justify-center">
          <div className="absolute -bottom-20 -right-20 w-64 h-64 bg-blue-500/10 blur-[80px] rounded-full pointer-events-none"></div>

          <div className="relative z-10 grid grid-cols-1 sm:grid-cols-2 gap-6 items-center h-full">
            <div className={`flex flex-col sm:flex-row gap-8`}>
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold mb-2">Base ATS Score</p>
                <div className="flex items-baseline space-x-2">
                  <span className={`text-6xl font-black bg-gradient-to-br ${!hasJD ? matchColor : "from-blue-400 to-indigo-500"} bg-clip-text text-transparent`}>{Math.round(ats)}</span>
                  <span className="text-2xl text-slate-500 font-bold">/ 100</span>
                </div>
              </div>

              {hasJD && (
                <div>
                  <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold mb-2">JD Match Score</p>
                  <div className="flex items-baseline space-x-2">
                    <span className={`text-6xl font-black bg-gradient-to-br ${matchColor} bg-clip-text text-transparent`}>{Math.round(matchScoreRaw)}</span>
                    <span className="text-2xl text-slate-500 font-bold">/ 100</span>
                  </div>
                </div>
              )}
            </div>

            {hasJD ? (
              <div className="flex flex-col justify-center space-y-2 bg-black/20 p-4 rounded-xl border border-white/5">
                <div className="flex justify-between text-xs font-bold uppercase tracking-wider">
                  <span className="text-slate-400">Skill Density</span>
                  <span className="text-white">{skillMatchPct}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden shadow-inner">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${skillMatchPct}%` }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="h-full bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full"
                  />
                </div>
                <p className="text-[10px] text-center text-slate-500 mt-1">Matching keywords vs requested keywords</p>
              </div>
            ) : (
              <div className="flex flex-col justify-center text-center p-4">
                <p className="text-sm text-slate-400">Add a Job Description to see targeted skill matching and compatibility insights.</p>
              </div>
            )}
          </div>
        </div>

        {/* Small Metrics Cards */}
        <div className="bg-slate-800/30 border border-white/5 rounded-2xl p-5 flex flex-col justify-center relative overflow-hidden group hover:border-white/10 transition-all">
          <div className="absolute top-2 right-2 p-2 opacity-10 group-hover:opacity-20 transition-opacity"><Briefcase className="w-12 h-12 text-blue-400" /></div>
          <div className="relative z-10">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-2">Experience</p>
            <div className="text-3xl font-bold text-blue-400">{expParsed} <span className="text-sm text-slate-500 font-medium">yrs</span></div>
          </div>
        </div>

        <div className="bg-slate-800/30 border border-white/5 rounded-2xl p-5 flex flex-col justify-center relative overflow-hidden group hover:border-white/10 transition-all">
          <div className="absolute top-2 right-2 p-2 opacity-10 group-hover:opacity-20 transition-opacity"><GraduationCap className="w-12 h-12 text-purple-400" /></div>
          <div className="relative z-10">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-2">Education</p>
            <div className="text-sm font-semibold text-slate-200 line-clamp-2 leading-snug">{eduParsed}</div>
          </div>
        </div>

        {/* Skills Cards */}
        {hasJD ? (
          <div className="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-emerald-500/5 border border-emerald-500/10 rounded-2xl p-5 shadow-sm">
              <h3 className="text-sm font-bold text-emerald-400 mb-3 flex items-center"><CheckCircle className="w-4 h-4 mr-2" /> Matches ({matching.length})</h3>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto pr-2 custom-scrollbar">
                {matching.length > 0 ? matching.map((skill, idx) => (
                  <span key={idx} className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-3 py-1 rounded-md text-xs font-medium">{skill}</span>
                )) : <span className="text-slate-500 text-xs font-medium">No matches found.</span>}
              </div>
            </div>

            <div className="bg-rose-500/5 border border-rose-500/10 rounded-2xl p-5 shadow-sm">
              <h3 className="text-sm font-bold text-rose-400 mb-3 flex items-center"><AlertCircle className="w-4 h-4 mr-2" /> Missing ({missing.length})</h3>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto pr-2 custom-scrollbar">
                {missing.length > 0 ? missing.map((skill, idx) => (
                  <span key={idx} className="bg-rose-500/10 border border-rose-500/20 text-rose-300 px-3 py-1 rounded-md text-xs font-medium">{skill}</span>
                )) : <span className="text-slate-500 text-xs font-medium">Fully qualified!</span>}
              </div>
            </div>
          </div>
        ) : (
          <div className="md:col-span-2 bg-blue-500/5 border border-blue-500/10 rounded-2xl p-5 shadow-sm">
            <h3 className="text-sm font-bold text-blue-400 mb-3 flex items-center"><CheckCircle className="w-4 h-4 mr-2" /> Extracted Skills ({result.extracted_skills?.length || 0})</h3>
            <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto pr-2 custom-scrollbar">
              {(result.extracted_skills || []).length > 0 ? (result.extracted_skills || []).map((skill, idx) => (
                <span key={idx} className="bg-blue-500/10 border border-blue-500/20 text-blue-300 px-3 py-1 rounded-md text-xs font-medium">{skill}</span>
              )) : <span className="text-slate-500 text-xs font-medium">No skills detected.</span>}
            </div>
          </div>
        )}

        {/* AI Recommendations */}
        <div className="md:col-span-2 bg-slate-800/50 border border-white/5 rounded-2xl p-5 shadow-sm">
          <h3 className="text-sm font-bold mb-3 flex items-center text-indigo-400"><Zap className="w-4 h-4 mr-2" /> AI Suggestions</h3>
          <div className="space-y-2 text-sm text-slate-300">
            {result.improvement_suggestions ? (
              <div className="whitespace-pre-wrap">{result.improvement_suggestions}</div>
            ) : (
              <div className="text-slate-500 italic">No AI suggestions generated. Ensure the API key is configured.</div>
            )}
          </div>

          {/* New Resume Generation Section */}
          <div className="mt-8 pt-6 border-t border-white/10">
            <h3 className="text-sm font-bold mb-3 flex items-center text-blue-400"><FileText className="w-5 h-5 mr-2" /> ATS Resume Generator</h3>
            <p className="text-sm text-slate-400 mb-5">Let our specialized AI model rewrite your resume to better match this job description and pass ATS filters.</p>

            {generatedResume ? (
              <div className="bg-slate-900/80 rounded-xl p-5 border border-blue-500/20 max-h-96 overflow-y-auto custom-scrollbar relative">
                <div className="absolute top-4 right-4 flex space-x-2">
                  <button
                    onClick={() => navigator.clipboard.writeText(generatedResume)}
                    className="flex items-center text-xs bg-slate-800 hover:bg-slate-700 text-white px-3 py-1.5 rounded shadow transition-colors border border-slate-700"
                  >
                    Copy
                  </button>
                  <button
                    onClick={downloadAsText}
                    className="flex items-center text-xs bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded shadow transition-colors"
                  >
                    <Download className="w-3 h-3 mr-1" /> Download
                  </button>
                </div>
                <div className="whitespace-pre-wrap text-sm text-slate-200 mt-8 font-mono leading-relaxed">{generatedResume}</div>
                <button
                  onClick={() => setGeneratedResume("")}
                  className="mt-4 text-xs text-slate-400 hover:text-white transition-colors"
                >
                  Generate again
                </button>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={handleGenerateResume}
                  disabled={generatingResume}
                  className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-6 py-3 rounded-xl font-semibold shadow-lg shadow-blue-500/20 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed group duration-300"
                >
                  {generatingResume ? <><Loader className="w-5 h-5 mr-2 animate-spin" /> Generating Base Resume...</> : <><FileText className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" /> Create ATS Friendly Text Resume</>}
                </button>

                {result.originalFile?.name?.endsWith('.docx') && hasJD && (
                  <button
                    onClick={handleMagicEdit}
                    disabled={magicEditing}
                    className="w-full sm:w-auto bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-6 py-3 rounded-xl font-semibold shadow-lg shadow-emerald-500/20 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed group duration-300"
                  >
                    {magicEditing ? <><Loader className="w-5 h-5 mr-2 animate-spin" /> Magically Editing DOCX...</> : <><Bot className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" /> Magic Edit DOCX File In-Place</>}
                  </button>
                )}
              </div>
            )}

            {magicEditError && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-center shadow-sm">
                <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" /> {magicEditError}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Chat Interface */}
      <AIChat result={result} />

    </Card>
  );
}

// New AI Chat Component
function AIChat({ result }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', text: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE_URL}/api/resumes/chat`, {
        resumeText: result.raw_text,
        jobDescription: result.jobDescription,
        chatHistory: messages,
        message: input
      });
      setMessages([...newMessages, { role: 'model', text: res.data.reply }]);
    } catch (error) {
      setMessages([...newMessages, { role: 'model', text: "💡 I'm sorry, I encountered an error connecting to the AI." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col h-[400px] overflow-hidden shadow-xl">
      <div className="bg-indigo-600/20 py-3 px-4 flex items-center border-b border-indigo-500/20">
        <MessageSquare className="w-5 h-5 text-indigo-400 mr-2" />
        <h3 className="font-semibold text-indigo-200 text-sm">AI Recruiter Chat</h3>
      </div>

      <div className="flex-grow overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.length === 0 && (
          <div className="text-center text-slate-500 text-sm mt-4">
            Ask me anything about your resume, the job description, or the suggestions!
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700'}`}>
              <div className="flex items-center mb-1">
                {msg.role === 'user' ? <User className="w-3 h-3 mr-1 opacity-70" /> : <Bot className="w-3 h-3 mr-1 text-indigo-400" />}
                <span className="text-[10px] uppercase font-bold opacity-70">{msg.role === 'user' ? 'You' : 'AI'}</span>
              </div>
              <div className="whitespace-pre-wrap">{msg.text}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 text-slate-400 p-3 rounded-2xl rounded-bl-none border border-slate-700 text-sm flex items-center space-x-2">
              <Loader className="w-4 h-4 animate-spin" /> <span>Thinking...</span>
            </div>
          </div>
        )}
      </div>

      <div className="p-3 bg-slate-800/80 border-t border-slate-700/50 flex items-center space-x-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask a question..."
          className="flex-grow bg-slate-900 border border-slate-700 hover:border-slate-600 transition-colors rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()} className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white p-3 rounded-xl transition-transform active:scale-95 shadow-lg shadow-indigo-600/20">
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
