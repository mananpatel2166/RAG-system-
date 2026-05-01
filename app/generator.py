from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch


class Generator:

    MODEL_NAME    = "google/flan-t5-base"
    MAX_NEW_TOKENS = 256
    MAX_INPUT_TOKENS = 1024  

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model_name = model_name
        print(f"Loading generator model: {model_name} ...")
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model     = T5ForConditionalGeneration.from_pretrained(model_name)
        self.device    = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        print(f"Generator ready on {self.device}.")

    def generate(self, question: str, context: str) -> str:
       
        prompt = (
            "Answer the question based only on the context below. "
            "If the answer is not in the context, say 'I don't know based on the provided document.'\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=self.MAX_INPUT_TOKENS,
            truncation=True,
        ).to(self.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=self.MAX_NEW_TOKENS,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )

        answer = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return answer.strip()
