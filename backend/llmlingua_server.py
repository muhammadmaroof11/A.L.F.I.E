from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from llmlingua import PromptCompressor
except ImportError:
    PromptCompressor = None

app = FastAPI(title="ALFIE Token Compressor (LLMLingua-2)")

# Initialize the compressor on startup (Downloads the small model, usually ~1GB)
compressor = None


@app.on_event("startup")
def load_model():
    global compressor
    if PromptCompressor is None:
        print("LLMLingua not installed. Running in dummy mode.")
        return
    # Use LLMLingua-2 (small, fast, great for general tasks)
    compressor = PromptCompressor(
        model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
        use_llmlingua2=True,
        device_map="cpu",  # Use CPU to avoid requiring a GPU for the compressor
    )


class CompressRequest(BaseModel):
    context: str
    target_token: int = 500


@app.post("/compress")
async def compress_prompt(req: CompressRequest):
    if not compressor:
        # Dummy fallback
        return {"compressed_prompt": req.context, "saved_tokens": 0}

    try:
        results = compressor.compress_prompt(
            req.context,
            instruction="",
            question="",
            target_token=req.target_token,
            rank_method="llmlingua2",
        )
        return {
            "compressed_prompt": results["compressed_prompt"],
            "saved_tokens": results["origin_tokens"] - results["compressed_tokens"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
