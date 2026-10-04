import torch
from langchain_core.runnables import RunnableLambda
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_PATH = "C:\\Users\\kumar\\OneDrive\\Desktop\\clg2 pros\\model"


def _build_chain():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
    model.eval()

    def _translate(inputs: dict) -> str:
        enc = tokenizer(
            inputs["text"],
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=256, num_beams=4)
        return tokenizer.decode(out[0], skip_special_tokens=True)

    return RunnableLambda(_translate)


print("⏳ Loading translation model...")
translation_chain = _build_chain()
print("✅ Model loaded successfully!")


def translate(english_text: str) -> str:
    """Translates English text to Japanese."""
    return translation_chain.invoke({"text": english_text}).strip()


if __name__ == "__main__":
    test_text = "Hello, thank you for your email. Can we meet tomorrow?"
    print(f"English:  {test_text}")
    print(f"Japanese: {translate(test_text)}")