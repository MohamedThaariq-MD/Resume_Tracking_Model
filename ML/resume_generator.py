import os
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

class ResumeGeneratorModel:
    def __init__(self):
        self.is_loaded = False
        self.model = None
        self.tokenizer = None
        
        base_dir = os.path.dirname(__file__)
        self.model_path = os.path.join(base_dir, "models", "resume_generator_model", "best_model")
        
        # Try to load custom trained model, otherwise fallback to base
        self.load_model()
        
    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                print(f"Loading specially trained model from {self.model_path}")
                self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
                self.is_loaded = True
            else:
                print("Trained model not found. Proceeding with un-tuned base model (flan-t5-small) for demonstration.")
                # We use flan-t5-small as the base. In a real environment, you want the trained version.
                base_model_name = "google/flan-t5-small"
                self.tokenizer = T5Tokenizer.from_pretrained(base_model_name)
                self.model = T5ForConditionalGeneration.from_pretrained(base_model_name)
                self.is_loaded = True
        except Exception as e:
            print(f"Error loading generative model: {e}")
            self.is_loaded = False

    def generate_ats_resume(self, resume_text: str, jd_text: str) -> str:
        """
        Generates an ATS optimized resume based on the original resume and Job Description.
        """
        if not self.is_loaded:
            return "Error: Generative model is not loaded."
            
        input_text = f"Optimize this resume for this job description.\n\nJob Description:\n{jd_text}\n\nResume:\n{resume_text}"
        
        # Tokenize input
        inputs = self.tokenizer(
            input_text, 
            return_tensors="pt", 
            max_length=512, 
            truncation=True
        )
        
        # Generate output sequence
        outputs = self.model.generate(
            **inputs,
            max_length=1024,
            num_beams=4,              # Beam search for better quality
            early_stopping=True,
            no_repeat_ngram_size=3,   # Prevent repeating phrases
            temperature=0.7           # Slight variation
        )
        
        # Decode the generated sequence
        generated_resume = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_resume

# Global instance
resume_generator_instance = ResumeGeneratorModel()
