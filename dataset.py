import json

# 개발 용어 리스트
terms = [
    {
        "term": "비동기 처리",
        "definition": "작업이 완료될 때까지 기다리지 않고 다음 작업을 수행하는 방식입니다.",
        "example": "JavaScript의 setTimeout, fetch API 등",
    },
    {
        "term": "REST API",
        "definition": "HTTP 기반의 API 설계 방식으로, 자원을 URI로 구분하고 HTTP 메서드로 행위를 정의합니다.",
        "example": "GET /users/1 → 유저 정보 조회",
    },
    {
        "term": "상태 코드",
        "definition": "HTTP 요청에 대한 서버의 응답 상태를 나타내는 숫자 코드입니다.",
        "example": "200(성공), 404(찾을 수 없음), 500(서버 오류)",
    },
    {
        "term": "API",
        "definition": "애플리케이션 프로그램 인터페이스의 줄임말로, 컴퓨터와 애플리케이션이 서로 통신하는 방식을 말합니다",
        "example": "웹 서비스에서 사용자 인증, 데이터 전송, 예약 시스템 등",
    },
    {
        "term": "JSON",
        "definition": "JavaScript Object Notation의 줄임말로, 데이터 교환을 위한 경량의 데이터 형식입니다.",
        "example": "{\"name\": \"John\", \"age\": 30, \"city\": \"New York\"}",
    },
    {
        "term": "XML",
        "definition": "eXtensible Markup Language의 줄임말로, 데이터 교환을 위한 표준 형식입니다.",
        "example": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><note><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Don't forget me this weekend!</body></note>",
    },
    {
        "term": "HTML",
        "definition": "Hypertext Markup Language의 줄임말로, 웹 페이지를 만들기 위한 표준 형식입니다.",
        "example": "<html><body><h1>Hello, World!</h1></body></html>",
    },
    {
        "term": "CSS",
        "definition": "Cascading Style Sheets의 줄임말로, 웹 페이지의 스타일을 정의하는 표준 형식입니다.",
        "example": "body { font-family: Arial, sans-serif; }",
    },
    {
        "term": "JavaScript",
        "definition": "클라이언트 측 스크립트 언어로, 웹 페이지의 동작을 제어하는 프로그래밍 언어입니다.",
        "example": "var x = 10;",
    },
    {
        "term": "Python",
        "definition": "프로그래밍 언어로, 데이터 분석, 웹 개발, 인공지능 등 다양한 분야에서 사용됩니다.",       
        "example": "print('Hello, World!')",
    }
]

# JSON 파일로 저장
with open('dev_terms.json', 'w', encoding='utf-8') as f:
    json.dump(terms, f, ensure_ascii=False, indent=2)

print("JSON 파일 생성")