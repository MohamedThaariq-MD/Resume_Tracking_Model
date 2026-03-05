import json
import os

def generate_mock_dataset(output_path: str, num_samples: int = 20):
    """
    Generates a mock dataset for training the resume generator.
    In a real scenario, this would load real parsed resumes and JDs,
    and a human/LLM curated 'ideal ATS resume'.
    """
    dataset = []
    
    for i in range(num_samples):
        # Extremely simplified mock data
        resume = f"Software Engineer with {i} years experience. Skils: python, sql. Some older experience in java."
        jd = f"Looking for Backend Engineer. Required skills: Python, FastAPI, SQL. Experience: {i} years."
        
        # The ideal generated output (more tailored to the JD)
        target = (
            f"Software Engineer | {i} Years Experience\n"
            f"Professional Summary: Experienced Backend Engineer proficient in Python, SQL, and FastAPI.\n\n"
            f"Skills: Python, FastAPI, SQL, Java\n\n"
            f"Experience:\n- Developed backend services using Python and SQL.\n- Leveraged FastAPI for high-performance APIs."
        )
        
        input_text = f"Optimize this resume for this job description.\n\nJob Description:\n{jd}\n\nResume:\n{resume}"
        
        dataset.append({
            "input_text": input_text,
            "target_text": target
        })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    print(f"Generated {num_samples} mock samples at {output_path}")

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    generate_mock_dataset(os.path.join(data_dir, "train_dataset.json"), num_samples=50)
    generate_mock_dataset(os.path.join(data_dir, "val_dataset.json"), num_samples=10)
