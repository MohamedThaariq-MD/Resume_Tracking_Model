import React from 'react';
import { motion } from 'framer-motion';

export default function Card({ children, className = '' }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`bg-slate-900/60 backdrop-blur-md border border-white/5 rounded-2xl p-8 shadow-lg transition-all duration-300 hover:scale-[1.01] ${className}`}
        >
            {children}
        </motion.div>
    );
}
