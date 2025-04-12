import json
from langchain.docstore.document import Document
from rag_system import RAGSystem

def load_json_terms(json_file):
    """JSON 파일에서 용어 데이터를 로드하고 Document 객체로 변환"""
    with open(json_file, 'r', encoding='utf-8') as f:
        terms = json.load(f)
    
    documents = []
    for term in terms:
        # 각 용어를 하나의 문서로 변환
        content = f"용어: {term['term']}\n정의: {term['definition']}\n예시: {term['example']}\n카테고리: {term['category']}"
        documents.append(Document(page_content=content))
    
    return documents

def main():
    # RAG 시스템 초기화 (.env 파일에서 API Key 로드)
    rag = RAGSystem()
    
    # JSON 파일에서 용어 데이터 로드
    documents = load_json_terms('dev_terms.json')
    
    # 벡터 저장소 생성
    rag.create_vectorstore(documents)
    
    # 벡터 저장소 저장
    rag.save_vectorstore("dev_terms_vectorstore")
    
    # 테스트 질문
    questions = [
        "비동기 처리가 무엇인가요?",
        "REST API에 대해 설명해주세요",
        "HTTP 상태 코드는 무엇인가요?"
    ]
    
    for question in questions:
        print(f"\n질문: {question}")
        answer, sources = rag.query(question)
        print(f"답변: {answer}")
        print("\n참고 문서:")
        for doc in sources:
            print(f"- {doc.page_content[:100]}...")

if __name__ == "__main__":
    main() 