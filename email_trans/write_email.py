from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
load_dotenv()
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


llm=ChatNVIDIA(
    base_url = "https://integrate.api.nvidia.com/v1/",
    model="google/diffusiongemma-26b-a4b-it",
    temperature=0.5,
    max_completion_tokens=4000,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a professional email writer. Write in {tone} style.And do not write subject ,company name , employee name and other things related to this just write main content"),
    ("human", "Write a concise email about: {topic}"),
])


chain= prompt | llm


def generate_email(topic: str, tone: str = "Formal Keigo") -> str:
    topic = topic.strip()
    if not topic:
        raise ValueError("Please enter a topic.")
    tone_guidance = {
        "Formal Keigo": "formal, courteous business English suitable for Japanese keigo translation",
        "Business": "concise, professional business English",
        "Casual": "friendly, relaxed conversational English",
    }
    tone = tone_guidance.get(tone, tone_guidance["Formal Keigo"])
    result = chain.invoke({"topic": topic, "tone": tone})
    return result.content.strip()


if __name__ == "__main__":
    print(generate_email("informing client for project completion."))

