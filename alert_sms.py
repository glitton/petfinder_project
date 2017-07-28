"""Paws Finder. Uses Flask, Jinja, AJAX and JSON

Working on SMS alert capability via Twilio API
"""
import os
from twilio.rest import Client

# Twilio API credentials
twilio_api_key = os.environ["TWILIO_API_KEY"]
twilio_api_secret = os.environ["TWILIO_API_SECRET"]

#Create TWILIO client object
client = Client(twilio_api_key, twilio_api_secret)

#Create message
client.messages.create(
    to=os.environ["TWILIO_PHONE"],
    from_=os.environ["MY_PHONE"],
    body="Cody is waiting for you to adopt him!"
)


