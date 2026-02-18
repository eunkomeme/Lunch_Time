# 🍽 Lunch Time

회사 동기들끼리 점심 약속을 조율하기 위해 만든 간단한 웹 서비스입니다.

오늘 점심에 참여 가능한 사람을 확인하고,  
식당과 시간을 정할 수 있도록 도와줍니다.

🔗 Live Demo: https://bit.ly/ojang <br> 
🚀 Deployed on Railway  

---

## 📌 What This Project Does

- 점심 참여 가능 여부 체크
- 개인 일정 있는 사람 표시
- 현재 참여 인원 확인
- 식당 선택 공유
- 실시간 상태 반영

소규모 인원이 동시에 접속해 사용하는 것을 전제로 만들었습니다.

---

## 🛠 Tech Stack

| 항목 | 기술 |
|------|------|
| Language | Python 3 |
| Backend Framework | Flask |
| Real-time Communication | Flask-SocketIO |
| Async Mode | eventlet |
| Production Server | Gunicorn |
| Data Storage | In-memory (Python dict) |
| Deployment | Railway |
| Frontend | HTML, CSS, Vanilla JavaScript |

---

## ⚙️ How It Works

- Flask 서버에서 기본 라우팅 처리
- Flask-SocketIO로 사용자 상태를 실시간 공유
- 서버 메모리(dict)에 현재 참여 상태 저장
- 상태 변경 시 모든 클라이언트에 즉시 반영

데이터베이스는 사용하지 않았으며,  
서버가 재시작되면 데이터는 초기화됩니다.

---

## 📂 Project Structure

```
.
├── app.py
├── requirements.txt
├── templates/
├── static/
```

---

## 🚀 Run Locally

```
pip install -r requirements.txt
python app.py
```

또는

```
gunicorn -k eventlet -w 1 app:app
```

---

## 📎 Notes

이 프로젝트는 소규모 그룹의 간단한 일정 조율을 목적으로 제작되었습니다.  
기능을 최소화하고 실시간 동기화 구현에 초점을 맞추었습니다.
