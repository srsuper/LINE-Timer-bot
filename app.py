from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from time import time

from datetime import timedelta

from collections import defaultdict

app = Flask(__name__)

line_bot_api = LineBotApi('d007709718f8a8af2042ae3ebc48aca5')
handler = WebhookHandler('hFcHkq7njlfHTSIAyNbkgTp3FQdbV7ntUr3DNMucqCgM4UYWB4RHblMw1oO7QZNaS8Pb+mbn+PdC01dx5JperIBvSjl58oNCWWLVEgDjhIYEq9lObjhAVfrtX6+6zrBBcfGXxpKthYd4ke17od+iiswh8p6xlupEHSzmJbGEAiwlZrQn+cnjYYg8swHSC/3b')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

user = defaultdict(lambda:{"total":0})
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    id = event.source.user_id   #LINEのユーザーIDの取得

    if event.message.text == "start":
        user[id]["start"] = time()  #start実行時の時間を取得
        totalTimeStr = timedelta(seconds = user[id]["total"])  #s -> h:m:s
        reply_message = f"Start Timer\n\nTotal: {totalTimeStr}"

    elif event.message.text == "stop":
        end = time()  #end実行時の時間を取得
        dif = int(end - user[id]["start"])  #経過時間を取得
        user[id]["total"] += dif  #総時間を更新
        timeStr = timedelta(seconds = dif)
        totalTimeStr = timedelta(seconds = user[id]["total"])
        reply_message = f"Stop Timer\n\nTime: {timeStr}s\nTotal: {totalTimeStr}"

    elif event.message.text == "reset":
        user[id]["total"] = 0 #総時間を0にリセット
        totalTimeStr = timedelta(seconds = user[id]["total"])
        reply_message = f"Reset Timer\n\nTotal: {totalTimeStr}"

    else:
        reply_message = "Please send \"start\" or \"stop\"or \"reset\""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message))


if __name__ == "__main__":
    app.run()
