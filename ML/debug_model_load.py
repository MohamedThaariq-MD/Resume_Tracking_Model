import sys
import traceback
import faulthandler

faulthandler.enable()

print("Attempting to load model via dedicated script...")

try:
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    import torch
    
    print("Transformers imported.")
    
    model_name = "google/flan-t5-small"
    print(f"Loading tokenizer for {model_name}...")
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    
    print(f"Loading model for {model_name}...")
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    print("Done loading model successfully!")
    sys.exit(0)
    
except Exception as e:
    print(f"Failed with exception: {e}")
    traceback.print_exc()
    sys.exit(1)
