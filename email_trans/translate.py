import torch
from langchain_core.runnables import RunnableLambda
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "C:\\Users\\kumar\\OneDrive\\Desktop\\colg\\college-minor-project-\\model" 

def _build_chain():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, src_lang="eng_Latn")
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    model.eval()
    jpn_id = tokenizer.convert_tokens_to_ids("jpn_Jpan")

    def _translate(inputs: dict) -> str:
        enc = tokenizer(
            inputs["text"],
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        with torch.no_grad():
            out = model.generate(
                **enc,
                forced_bos_token_id=jpn_id,
                max_new_tokens=256,
                num_beams=4,
            )
        return tokenizer.batch_decode(out, skip_special_tokens=True)[0]

    return RunnableLambda(_translate)


print("Loading translation model...")
translation_chain = _build_chain()
print("Model loaded successfully!")


def translate(english_text: str) -> str:
    """Translates English text to Japanese."""
    english_text = english_text.strip()
    if not english_text:
        return ""
    return translation_chain.invoke({"text": english_text}).strip()


if __name__ == "__main__":
    test_text = "myy name is ramu"
    print(f"English:  {test_text}")
    print(f"Japanese: {translate(test_text)}")