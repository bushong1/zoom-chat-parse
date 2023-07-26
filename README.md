# zoom-chat-parse

This is a python project that will parse a zoom chat that utilize the emoji response and thread features.

## Why

Zoom released what they call the "new meeting chat experience", which offers a few neat features, including Emoji reactions and Threads in zoom chat.  This is very clean within the UI.  However, when you export the chat, it is a bloated mess with all the reactions and threads being disconnected from the original message.  This tool will convert the text files that come from saved zoom chats into something much more readable.

## Usage

```sh
python ./cleanup-zoom-chat.py my-zoom-chat.txt
```

## Design Considerations

### Removing DMs

In the context of cleaning up a zoom chat, most of the time I'm doing this it's so I can share the meeting output with others.  In that context, I don't think it's appropriate to include DMs

### Consolidating emoji sequences

[Emoji ZJW Sequences](https://blog.emojipedia.org/emoji-zwj-sequences-three-letters-many-possibilities/) are methods of combining emojis to make a single emoji display.  There are many layers of combined emojis, and often times, especially on shell, this can result in smushed output.  For the context of recapping a zoom meeting, I made the decision to only parse the first emoji in a reaction, and add that to the total.  This has the undesirable consequence of removing skin-tone, color (such as in hearts), or even changing the context of the emoji entirely.  For now, I'm considering this an acceptable pain of emojis until I can get something that displays ZJW Sequences on shell better.

### Single Line

In chat it's possible to send messages with multiple lines.  Due to the... annoying nature of zoom's saved chats, this became fairly burdensome when parsing and displaying original messages + tabbed-in replies.  As such, I decided to simply join all messages to a single line, and then begin processing them at a later step.  I'm willing to accept PRs on this to improve functionality.

## Testing

### Run the unit tests

```sh
python ./cleanup-zoom-chat.py test
```

### Test out a sample file

### Debugging

If your file is breaking for some reason, you can enable debugging mode to get more output while parsing.  Alternately, feel free to submit an issue on GitHub

```sh
export DEBUG=true
python ./cleanup-zoom-chat.py ./my-zoom-chat.txt
```

## Example

```sh
python ./cleanup-zoom-chat.py ./test-zoom-chat.txt
```

Orginal file

```
10:01:00 From  John Doe  to  Everyone:
  Good morning folks
10:01:01 From  Frank Brank  to  Everyone:
  add 👍🏻
10:01:02 From  Evan Bevan  to  Everyone:
  add 👍
10:01:03 From  Frank Brank  to  Everyone:
  add 👍
10:01:04 From  Alice Balice  to  Everyone:
  add 🍪
10:01:10 From  Alice Balice  to  Everyone:
  Replying to "Good morning folks" Hi John
10:01:20 From  Jane Smith  to  Everyone:
  Replying to "Good morning folks" Hello there, John!
10:01:31 From  Frank Brank  to  Everyone:
  add ☝️
10:01:32 From  Evan Bevan  to  Everyone:
  add 💯
10:01:33 From  Frank Brank  to  Everyone:
  remove ☝️
10:02:00 From  Jack Doe  to  Everyone:
  Hello world, this message is longer than 20 characters!
10:02:10 From  Diane Smith  to  Everyone:
  Replying to "Hello world, this me..." Hello there, Jack!
10:03:00 From  John Doe to Open Mike(Direct Message):
  Please mute
10:04:06 From  Charlie Barlie (she/her)  to  Everyone:
  Reacted to "Good morning folks" with 👋
10:04:07 From  Alice Balice  to  Everyone:
  Removed a 🍪 reaction from "Good morning folks"
```

Cleaned up:

```
10:01:00 John Doe [👍x3, 👋x1]: Good morning folks
  10:01:10 Alice Balice: Hi John
  10:01:20 Jane Smith [💯x1]: Hello there, John!
10:02:00 Jack Doe: Hello world, this message is longer than 20 characters!
  10:02:10 Diane Smith: Hello there, Jack!
```

