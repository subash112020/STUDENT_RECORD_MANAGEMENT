
from flask import Flask, render_template, jsonify
from gmail_service import get_gmail_service
from gmail_service import get_latest_client_reply

from datetime import datetime
import pytz

app = Flask(__name__)

CLIENT_EMAIL = "subashoffcl@gmail.com"

last_message_id = None

def is_working_hours():

    timezone = pytz.timezone("Asia/Kolkata")

    current_time = datetime.now(timezone)

    hour = current_time.hour

    print("Current time:", current_time)

    return 9 <= hour < 18



def check_for_new_reply():

    global last_message_id

    service = get_gmail_service()

    message_id = get_latest_client_reply(
        service,
        CLIENT_EMAIL
    )

    if message_id is None:

        print(
            f"No client reply found from {CLIENT_EMAIL}."
        )

        return {
            "new_reply": False,
            "message": "No client reply found."
        }


    if message_id != last_message_id:

        print("New client reply detected!")

        last_message_id = message_id



        if is_working_hours():

            print("Working hours.")

            return {
                "new_reply": True,
                "message": "New client reply detected!",
                "message_id": message_id,
                "working_hours": True
            }

        else:

            print("Outside working hours.")

            return {
                "new_reply": True,
                "message": "New client reply detected!",
                "message_id": message_id,
                "working_hours": False
            }


    return {
        "new_reply": False,
        "message": "No new reply."
    }



@app.route("/")
def home():

    return render_template("index.html")


@app.route("/check-replies")
def check_replies():

    result = check_for_new_reply()

    return jsonify(result)



if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
