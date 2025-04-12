import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import pickle
import json
import warnings

class RAGSystem:
    def __init__(self, api_key=None, embedding_k=4, retrieval_k=4):
        # API Key 설정
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            # .env 파일에서 로드 시도
            load_dotenv()
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OpenAI API Key가 설정오류")

        # OpenAI 임베딩 초기화
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1536
        )
        # FAISS 벡터 저장소 초기화
        self.vectorstore = None
        # 텍스트 분할기 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        # LLM 초기화
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini"  # 사용할 GPT 모델 지정
        )
        # k 파라미터 저장
        self.embedding_k = embedding_k
        self.retrieval_k = retrieval_k

        # Few-shot 예시 (분야별)
        self.few_shot_examples = """
        Example 1 (Frontend Developer):
        Question: What is React? (Category: frontend)
        Answer: {
            "term": "React",
            "definition": "A JavaScript library for building user interfaces, particularly single-page applications where UI updates are frequent.",
            "example": "Creating a dynamic form with real-time validation using React hooks and state management."
        }

        Example 2 (Backend Developer):
        Question: What is REST API? (Category: backend)
        Answer: {
            "term": "REST API",
            "definition": "An architectural style for designing networked applications that uses HTTP methods to perform operations on resources identified by URIs.",
            "example": "Implementing a user authentication system using REST endpoints: POST /auth/login, GET /users/profile, etc."
        }

        Example 3 (AI Engineer):
        Question: What is Machine Learning? (Category: ai)
        Answer: {
            "term": "Machine Learning",
            "definition": "A subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
            "example": "Training a neural network to classify images using TensorFlow and implementing transfer learning for better accuracy."
        }

        Example 4 (Designer):
        Question: What is UI/UX Design? (Category: design)
        Answer: {
            "term": "UI/UX Design",
            "definition": "The process of designing user interfaces and experiences to create intuitive and engaging digital products.",
            "example": "Creating wireframes and prototypes in Figma, focusing on user flow and accessibility guidelines."
        }
        """

        # 커스텀 프롬프트 템플릿
        self.qa_prompt = PromptTemplate(
            template="""You are an expert in IT terminology. Please answer the following question using the given context.
            Your response must strictly follow this JSON format:
            {{
                "term": "Term",
                "definition": "Definition",
                "example": "Example"
            }}

            The user is a {category} developer/designer. Please provide examples and explanations that are relevant to their field.
            Focus on practical applications and scenarios that would be most useful for someone in the {category} field.

            Here are some examples:
            {few_shot_examples}

            Context: {context}

            Question: {question}
            Category: {category}
            Answer: """,
            input_variables=["context", "question", "category"],
            partial_variables={"few_shot_examples": self.few_shot_examples}
        )

    def create_vectorstore(self, documents):
        #문서를 벡터 저장소로 변환
        # 문서 분할
        texts = self.text_splitter.split_documents(documents)
        # FAISS 벡터 저장소 생성
        self.vectorstore = FAISS.from_documents(texts, self.embeddings)
        return self.vectorstore

    def save_vectorstore(self, path):
        # 벡터 저장소를 파일로 저장
        if self.vectorstore:
            self.vectorstore.save_local(path)

    def load_vectorstore(self, path):
        """Load FAISS vector store from disk with Python 3.13+ compatibility"""
        try:           
            # FAISS 벡터 저장소 로드
            self.vectorstore = FAISS.load_local(
                path,
                self.embeddings,
                allow_dangerous_deserialization=True  # Python 3.13+에서 필요한 설정
            )
            print(f"Vector store loaded successfully from {path}")
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            raise

    def get_qa_chain(self):
        # QA 체인 생성
        if not self.vectorstore:
            raise ValueError("Vectorstore가 초기화되지 않았습니다.")
        
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.retrieval_k}
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": self.qa_prompt  # 커스텀 프롬프트 사용
            }
        )

    def query(self, question):
        #질문에 대한 답변 생성
        qa_chain = self.get_qa_chain()
        result = qa_chain({"query": question})
        return result["result"], result["source_documents"] 