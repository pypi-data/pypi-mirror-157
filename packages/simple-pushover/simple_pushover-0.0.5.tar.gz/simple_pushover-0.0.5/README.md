# PushOver Push Notification API Module
A single Python Module that allows for the interaction with PushOver's Push Notification API. PushOver offers a service that makes it really easy to send Push Notification to devices (laptops, phones, etc). This is all accomplished easily through the use of POST Requests to their API Endpoint. This module just takes the easy to use service and wraps it up in a nice and quick way to allow for quicker script writing.

## Set up:
1. Get an account at: https://pushover.net/ (This is the "Dashboard" URL once signed in)
2. Copy `example.env` and rename it to `.env`
3. Grab the "User Key" and add it to the designated place (`USER_KEY`) in the `.env`, found in the root of the project directory (`pushover/`) 
4. Next create your application through: https://pushover.net/apps/build
5. Grab the "API Token/Key" (we'll call it a "API Token" because the POST calls it a Token so therefore it is a **TOKEN**). Add the **API Token** to the designated place (`API_TOKEN`) in the `.env`
6. Finally run: `pip install -r requirements.txt`
7. ***DON'T FORGET TO ADD A DEVICE AND INSTALL THE APP ON YOUR PHONE OR HAVE THE BROWSER REGISTERED!*** This can be done through the Dashboard.

## Usage and Limitations:
Once you have completed the set up, you should be ready to use the module. There are some limitations the PushOver Push Notification API. These limitations are actually also handled within the python module itself, as validation, to help avoid users of this module from wasting API Calls and wasting their time. Before using the module make sure to give a quick glance to the limitations: https://pushover.net/api#limits.

None of the limitations are particularly major. Mainly max length restrictions on URLs and Text, and then Byte Size limits on Images.

## Usage
```python
from simple_pushover import PushoverAPI

# first create a PushoverAPI instance
api = PushoverAPI()
# To send a message (under 1024 Characters...) You can use the simple_send_push or the more featureful send_push.
# Really only the message kwarg is required.
api.simple_send_push(message="Hello World")

# You can also add the priority kwarg to set the priority level (-2 thru 2). I.E. priority=1 sends a message with a High Priority. It should be noted that the default is 0 which is normal priority
api.simple_send_push(message="Hello World", priority=1)

# For more complex Push notifications you can use:
api.send_push(
    title="Test Title",
    message="This is an example of a more complex push notification.",
    url="https://example.com/",
    url_title="Link Display Title",
    attachment="path/to_img.png",
    priority=1
)
# Once again the only required kwarg is message. However If you pass the kwarg url_title, you must also pass a URL.
```

### Future Enhancements:
I may add some other minor pieces to the module to help with other APIs that PushOver offers **(** *maybe once I have a need for them :^)* **)**. The Push Notification still has some touch ups needed which can be found below...

#### TO DO:
- Add filetype validation to the image attachments... Technically their API only handles images as attachments according to their API. I forgot to add that check, ***DOH!***
- Add HTML parsing options