from flask import Flask, request, jsonify
import anthropic
import os

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """당신은 (주)해나무의 개인 AI 비서입니다.
사용자의 이름은 정모입니다.
당근 광고 대행사 업무를 돕고, 일정 관리, 메일 초안 작성, 영업 관련 질문에 답변합니다.
항상 친절하고 간결하게 한국어로 답변하세요.
답변은 카카오톡 메시지에 맞게 짧고 명확하게 작성하세요."""

conversation_history = {}

@app.route("/", methods=["GET"])
def health():
    return "해나무 AI 비서 서버 정상 작동 중 ✅", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        user_id = data["userRequest"]["user"]["id"]
        user_message = data["userRequest"]["utterance"]

        if user_id not in conversation_history:
            conversation_history[user_id] = []

        conversation_history[user_id].append({
            "role": "user",
            "content": user_message
        })

        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=conversation_history[user_id]
        )

        reply = response.content[0].text

        conversation_history[user_id].append({
            "role": "assistant",
            "content": reply
        })

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": reply
                        }
                    }
                ]
            }
        })

    except Exception as e:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"오류가 발생했습니다: {str(e)}"
                        }
                    }
                ]
            }
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
