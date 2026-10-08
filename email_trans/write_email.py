from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
load_dotenv()
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


llm=ChatNVIDIA(
    base_url = "https://integrate.api.nvidia.com/v1/",
    model="google/diffusiongemma-26b-a4b-it",
    temperature=0.5
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a professional email writer. Write in a formal tone."),
    ("human", "Write a short email about: {topic}"),
])


chain= prompt | llm

result=chain.invoke({"topic":"informing client for project completion."})

print(result.content)

