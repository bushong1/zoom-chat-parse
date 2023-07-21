# zoom-chat-parse

This is a python project that will parse a zoom chat that utilize the emoji response and thread features.

## Why

Zoom released what they call the "new meeting chat experience", which offers a few neat features, including Emoji reactions and Threads in zoom chat.  This is very clean within the UI.  However, when you export the chat, it is a bloated mess with all the reactions and threads being disconnected from the original message.  This tool will convert the text files that come from saved zoom chats into something much more readable.

## Usage

python ./cleanup-zoom-chat.py my-zoom-chat.txt

## Testing

### Run the unit tests

python ./cleanup-zoom-chat.py test

### Test out a sample file

python ./cleanup-zoom-chat.py ./test-zoom-chat.txt
