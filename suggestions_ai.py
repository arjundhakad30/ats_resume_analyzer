from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import os

# ===== CHANGE THIS PATH to your local model folder =====
model_path = r"C:/Users/Shree/Downloads/codellama"  # <- update this

generator = None

try:
    if os.path.exists(model_path):
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", local_files_only=True)
        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
        print("✅ Model loaded successfully")
    else:
        print("⚠️ Model path does not exist. Fallback mode enabled.")

except Exception as e:
    print("⚠️ Model loading failed:", e)

# ===== Function to rewrite sections =====
def rewrite_section(section_text, section_name):
    if generator:
        prompt = f"Improve this resume {section_name} section to be ATS-friendly:\n{section_text}"
        output = generator(prompt, max_length=200, do_sample=True)
        return output[0]['generated_text']
    else:
        # fallback
        return f"(Offline model not loaded) Original {section_name} section:\n{section_text[:300]}"
