from fastapi import FastAPI, HTTPException
import pika
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import fasttext
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class Comment(BaseModel):
    text: str
    sentiment: str


class Comments(BaseModel):
    comments: List[Comment]
    count_positive_comments: int
    count_negative_comments: int


@app.get("/ml/{video_id}")
async def get_comments(video_id: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', credentials=pika.PlainCredentials('rmuser', 'rmpassword')))
    channel = connection.channel()
    try:
        queue_name = video_id
        channel.queue_declare(queue=queue_name, passive=True)
    except pika.exceptions.ChannelClosedByBroker:
        raise HTTPException(status_code=404, detail="Queue not found")

    messages = []

    while True:
        method_frame, _, body = channel.basic_get(queue_name, auto_ack=True)
        if method_frame and body:  # Добавляем проверку на наличие данных в сообщении
            # Декодируем JSON-сообщение
            message = body.decode()
            messages.append(message)
        elif not method_frame:
            break

    connection.close()

    if not messages:
        raise HTTPException(status_code=404, detail="No comments found")
    predict_sentiment, count_positive, count_negative = get_sentiment_predict(messages)
    return Comments(comments=predict_sentiment, count_positive_comments=count_positive, count_negative_comments=count_negative)

def preprocess_text(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'[^a-zA-Zа-яА-Я\s]', '', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_sentiment_predict(comment_list: List[str]):
    model_path = "fasttext/model.bin"
    fasttext_model = fasttext.load_model(model_path)
    count_positive = 0
    count_negative = 0
    predictions = []

    for comment in comment_list:
        processed_comment = preprocess_text(comment)
        # Сделаем предсказание sentiment
        predicted_label = fasttext_model.predict(processed_comment)[0][0]
        sentiment = 'positive' if predicted_label == "__label__0" else 'negative'
        if sentiment == 'positive':
            count_positive += 1
        else:
            count_negative += 1
        predictions.append({"text": comment, "sentiment": sentiment})
    return predictions, count_positive, count_negative

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
