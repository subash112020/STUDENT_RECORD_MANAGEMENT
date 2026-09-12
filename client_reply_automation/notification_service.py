from plyer import notification
import winsound


def notify_client_reply():
    print("New client reply received!")

    notification.notify(  # pyright: ignore[reportOptionalCall]
        title="Client Reply Received",
        message="You have received a new reply from your client.",
        timeout=10
    )

    winsound.Beep(600, 500)
    winsound.Beep(800, 500)
    winsound.Beep(1000, 500)
    winsound.Beep(1200, 500)

    print("Notification sent successfully.")
