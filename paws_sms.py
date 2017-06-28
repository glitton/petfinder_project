"""Paws Finder. Uses Flask, Jinja, AJAX and JSON

Working on SMS alert capability via Twilio API
"""
from flask import Flask, Response, request
from flask_debugtoolbar import DebugToolbarExtension
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os

# Twilio API credentials
twilio_api_key = os.environ["TWILIO_API_KEY"]
twilio_api_secret = os.environ["TWILIO_API_SECRET"]

#Create TWILIO client object
client = Client(twilio_api_key, twilio_api_secret)

# #Create message
# client.messages.create(
#     to=os.environ["TWILIO_PHONE"],
#     from_="+14158703258",
#     body="Cody is waiting for you to adopt him!"


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "LGkjsdFlfkjaBldsmDasVfd36p9!9u0m43qlnXalrCd1f43aB"

@app.route("/", methods=["GET"])
def send_alert():
    """Send updates about saved pets to users"""

    #Create alert message
    message = client.messages.create(
         to = "TWILIO_PHONE",
         from_ = "MY_PHONE",
         body = "There are updates to your saved pets! Type 'Yes' if interested.",
         media_url = ["http://bit.ly/2tlWPcH"])

    return Response("Shelter alert sent!"), 200


@app.route("/sms", methods=["POST"])
def respond_to_shelter_alert():
    """User response to alert from shelter"""
    
    response = MessagingResponse()

    # Based on users response, message is returned
    inbound_message = request.form.get("Body")

    # Respond to the user 
    if inbound_message == "Yes":
        response.message("Thank you. Please contact us for an appointment.")
    else:
        response.message("Hi! Not quite sure what you meant.  Check PAWS Finder for updates.")

    return str(response)

if __name__ == "__main__":

        # Do not debug for demo
    app.debug = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run(host="0.0.0.0")


