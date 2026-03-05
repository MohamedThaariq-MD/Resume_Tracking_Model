import os
import json
import torch
from transformers import (
    T5ForConditionalGeneration, 
    T5Tokenizer, 
    Seq2SeqTrainer, 
    Seq2SeqTrainingArguments, 
    DataCollatorForSeq2Seq
)
from torch.utils.data import Dataset

class ResumeDataset(Dataset):
    def __init__(self, data_path, tokenizer, max_input_length=512, max_target_length=512):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.max_input_length = max_input_length
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        input_text = item['input_text']
        target_text = item['target_text']

        # Tokenize Inputs
        model_inputs = self.tokenizer(
            input_text, 
            max_length=self.max_input_length, 
            padding="max_length", 
            truncation=True, 
            return_tensors="pt"
        )
        
        # Tokenize Targets
        with self.tokenizer.as_target_tokenizer():
            labels = self.tokenizer(
                target_text, 
                max_length=self.max_target_length, 
                padding="max_length", 
                truncation=True, 
                return_tensors="pt"
            )

        # Remove the batch dimension added by return_tensors
        model_inputs = {k: v.squeeze(0) for k, v in model_inputs.items()}
        labels = labels["input_ids"].squeeze(0)
        
        # Replace padding token id with -100 so it's ignored in loss computation
        labels[labels == self.tokenizer.pad_token_id] = -100
        model_inputs["labels"] = labels

        return model_inputs

def train():
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")
    model_dir = os.path.join(base_dir, "models", "resume_generator_model")
    
    os.makedirs(model_dir, exist_ok=True)
    
    # Check for target files before starting
    train_path = os.path.join(data_dir, "train_dataset.json")
    val_path = os.path.join(data_dir, "val_dataset.json")
    if not os.path.exists(train_path) or not os.path.exists(val_path):
        print("Dataset not found. Please run dataset_prep.py first.")
        return

    # Use a small efficient model for generation
    model_name = "google/flan-t5-small"
    print(f"Loading {model_name}...")
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    train_dataset = ResumeDataset(train_path, tokenizer)
    val_dataset = ResumeDataset(val_path, tokenizer)

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir=model_dir,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=3,  # Set to a small number for testing
        predict_with_generate=True,
        logging_dir=os.path.join(base_dir, "logs"),
        logging_steps=10,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    print("Starting training...")
    trainer.train()

    print(f"Saving model to {model_dir}")
    trainer.save_model(os.path.join(model_dir, "best_model"))
    tokenizer.save_pretrained(os.path.join(model_dir, "best_model"))
    print("Training complete and model saved.")

if __name__ == "__main__":
    train()
