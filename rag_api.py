from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_system import RAGSystem
from additional_query_system import AdditionalQuerySystem
from typing import List, Optional
import json
import asynci
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(
    title="IT Terminology RAG API",
    description="API for retrieving IT terminology information using RAG system",
    version="1.0.0"
)

# CORS 설정 - 백엔드 서버의 도메인만 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-backend-domain.com"],  # 백엔드 서버 도메인
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG 시스템 초기화
rag_system = None
additional_query_system = None
executor = ThreadPoolExecutor(max_workers=4)  # 동시 처리 가능한 작업 수 설정

class Question(BaseModel):
    question: str
    category: str  # 백엔드에서 전달받은 카테고리

class AdditionalQuestion(BaseModel):
    previous_answer: dict
    additional_request: str
    category: str

class TermInfo(BaseModel):
    term: str
    definition: str
    example: str

class Answer(BaseModel):
    term_info: TermInfo
    sources: List[str]

@app.on_event("startup")
async def startup_event():
    global rag_system, additional_query_system
    try:
        # RAG 시스템 초기화
        rag_system = RAGSystem()
        additional_query_system = AdditionalQuerySystem()
        
        # 벡터 저장소 로드 (비동기로 처리)
        await asyncio.get_event_loop().run_in_executor(
            executor,
            rag_system.load_vectorstore,
            "dev_terms_vectorstore"
        )
    except Exception as e:
        print(f"Failed to initialize systems: {str(e)}")
        raise

async def run_in_threadpool(func, *args):
    return await asyncio.get_event_loop().run_in_executor(executor, func, *args)

@app.post("/ask", 
         response_model=Answer,
         summary="Ask a question about IT terminology",
         description="Returns information about IT terms in a structured format, tailored to the user's category")
async def ask_question(question: Question):
    try:
        if not rag_system:
            raise HTTPException(status_code=500, detail="RAG system is not initialized")
        
        # 비동기로 질문 처리
        answer, sources = await run_in_threadpool(
            rag_system.query,
            question.question,
            question.category
        )
        
        # JSON 문자열을 파싱
        try:
            term_info = json.loads(answer)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid response format from the model")
        
        # 소스 문서에서 내용 추출
        source_contents = [doc.page_content for doc in sources]
        
        return Answer(
            term_info=TermInfo(**term_info),
            sources=source_contents
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/additional",
         response_model=Answer,
         summary="Ask for additional information about a previous answer",
         description="Returns additional information based on the user's follow-up request")
async def ask_additional_question(question: AdditionalQuestion):
    try:
        if not additional_query_system:
            raise HTTPException(status_code=500, detail="Additional query system is not initialized")
        
        # 비동기로 추가 질문 처리
        additional_answer = await run_in_threadpool(
            additional_query_system.process_additional_query,
            question.previous_answer,
            question.additional_request,
            question.category
        )
        
        return Answer(
            term_info=TermInfo(**additional_answer),
            sources=[]  # 추가 질문의 경우 소스는 없음
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    # 스레드 풀 종료
    executor.shutdown(wait=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 