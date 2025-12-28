import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai


current_file = Path(__file__).resolve()
env_path = current_file.parent.parent / ".env"

# 明示的にロード
load_dotenv(dotenv_path=env_path)

# 環境変数から取得
api_key = os.getenv("GOOGLE_API_KEY")


# デバッグ用：Noneならここで例外を投げて止める（JavaのAssertに近い）
if not api_key:
    raise ValueError(f"APIキーが取得できません。パスを確認してください: {env_path}")

# クライアントの初期化（キーワード引数を忘れずに）
client = genai.Client(api_key=api_key)

# 利用可能なモデルをリストアップ
print("--- Available Gemini Models ---")
for model in client.models.list():
    # 最新SDKではプロパティ名が異なります。
    # model.name だけでも十分ですが、詳細が見たい場合は print(model) で全属性を確認できます。
    print(f"Name: {model.name}")

    # チャットに使えるかどうかの判断（簡易版）
    if "generateContent" in str(model):
        print("💡 This model supports Chat/Generation")

    print("-" * 30)


prompt = input("enter your prompt :")

# モデル名は現在安定している 1.5-flash にしておきましょう
response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)


print("\nthe response is")
print("--------------------")
print(response.text)
