# train_lora_flan_t5_base.py
"""
Fine-tune Flan-T5-Base with LoRA (PEFT) — CPU friendly, Windows-safe.
Saves only LoRA adapters (small files).
"""

import os
import shutil
import argparse
from datasets import load_dataset
import numpy as np
import evaluate
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    EarlyStoppingCallback
)
from peft import LoraConfig, get_peft_model, PeftModel, PeftConfig

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="google/flan-t5-base")
    parser.add_argument("--dataset_csv", type=str, default="../dataset_prepared.csv")
    parser.add_argument("--output_dir", type=str, default="../models_saved/flan_t5_base_lora")
    parser.add_argument("--num_train_epochs", type=int, default=5)
    parser.add_argument("--train_batch", type=int, default=8)
    parser.add_argument("--eval_batch", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=5e-5)
    parser.add_argument("--max_input_length", type=int, default=256)
    parser.add_argument("--max_target_length", type=int, default=256)
    parser.add_argument("--save_total_limit", type=int, default=3)
    return parser.parse_args()

def main():
    args = parse_args()
    output_dir = args.output_dir + "_" + args.model_name.replace("/", "_")
    print("=== CONFIG ===")
    print("Model:", args.model_name)
    print("Dataset:", args.dataset_csv)
    print("Output:", output_dir)
    print("================\n")

    # Delete existing output dir to avoid Windows file lock issues
    if os.path.exists(output_dir):
        print("Removing existing output directory to avoid Windows lock issues...")
        shutil.rmtree(output_dir, ignore_errors=True)

    # Load dataset (expects CSV with columns: question, answer)
    ds = load_dataset("csv", data_files={"train": args.dataset_csv})["train"]
    ds = ds.rename_columns({"question": "input_text", "answer": "target_text"})
    ds = ds.train_test_split(test_size=0.05, seed=42)

    # Tokenizer and base model
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, use_fast=True)
    # ensure tokenizer has pad token
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "<pad>"})

    base_model = AutoModelForSeq2SeqLM.from_pretrained(
        args.model_name,
        cache_dir=None  # optional
    )
    base_model.config.pad_token_id = tokenizer.pad_token_id

    # LoRA config (small, safe defaults)
    lora_config = LoraConfig(
        r=8,                 # rank
        lora_alpha=32,
        target_modules=["q", "v", "k", "o", "wi", "wo"],  # common targets; PEFT will filter available modules
        lora_dropout=0.05,
        bias="none",
        task_type="SEQ_2_SEQ_LM"
    )

    # Wrap model with PEFT LoRA
    model = get_peft_model(base_model, lora_config)
    model.print_trainable_parameters()  # show trainable params (should be small)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Preprocessing function
    def preprocess_function(examples):
        inputs = ["question: " + str(q) for q in examples["input_text"]]
        model_inputs = tokenizer(
            inputs,
            max_length=args.max_input_length,
            truncation=True,
            padding="max_length"
        )
        labels = tokenizer(
            examples["target_text"],
            max_length=args.max_target_length,
            truncation=True,
            padding="max_length"
        )["input_ids"]

        # replace pad token id's in labels by -100 so they are ignored by loss
        labels = [
            [(t if t != tokenizer.pad_token_id else -100) for t in label] for label in labels
        ]
        model_inputs["labels"] = labels
        return model_inputs

    tokenized = ds.map(preprocess_function, batched=True, remove_columns=ds["train"].column_names)

    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # Metrics (ROUGE)
    rouge = evaluate.load("rouge")
    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        preds = preds[0] if isinstance(preds, tuple) else preds
        preds = np.where(preds < 0, tokenizer.pad_token_id, preds)
        labels = np.where(labels < 0, tokenizer.pad_token_id, labels)

        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        result = rouge.compute(predictions=decoded_preds, references=decoded_labels)
        return {k: round(v * 100, 4) for k,v in result.items()}

    # Training arguments (CPU friendly)
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=50,
        per_device_train_batch_size=args.train_batch,
        per_device_eval_batch_size=args.eval_batch,
        num_train_epochs=args.num_train_epochs,
        predict_with_generate=True,
        generation_max_length=128,
        learning_rate=args.learning_rate,
        save_total_limit=args.save_total_limit,
        fp16=False,
        report_to="none",
        load_best_model_at_end=True,
        metric_for_best_model="eval_rouge1",
        greater_is_better=True
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

    # Train
    trainer.train()

    # Save LoRA adapters only (small)
    print("\nSaving LoRA adapters (small).")
    model.save_pretrained(output_dir)  # PEFT saves adapter weights only

    # Also save the tokenizer so inference is easy later
    tokenizer.save_pretrained(output_dir)
    print("Saved to", output_dir)

if __name__ == "__main__":
    main()
