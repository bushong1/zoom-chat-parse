import re
import unittest
from io import StringIO

# Global var to define debug
DEBUG = False

class Message:
    def __init__(self, timestamp, name, content):
        self.timestamp = timestamp
        self.name = name
        self.content = content
        self.replies = []
        self.emojis = {}

    def add_reply(self, reply):
        self.replies.append(reply)
    
    def add_emoji(self, emoji):
        if emoji in self.emojis:
            self.emojis[emoji] += 1
        else:
            self.emojis[emoji] = 1
    def remove_emoji(self, emoji):
        if emoji in self.emojis:
            if self.emojis[emoji] > 1:
                self.emojis[emoji] -= 1
            else:
                del self.emojis[emoji]

    def format(self):
        if len(self.emojis) > 0:
            emoji_counts = ", ".join([f"{emoji}x{count}" for emoji, count in self.emojis.items()])
            emoji_string = f" [{emoji_counts}]"
        else:
            emoji_string = ""
        return f"{self.timestamp} {self.name}{emoji_string}: {self.content}"
    def display(self, indent=""):
        print(self.format())
        for reply in self.replies:
            print(indent + reply.format())

def is_emoji_related(line):
    patterns = [
        ": Reacted to ",
        ": Removed a ",
        ": remove ",
        ": add "
    ]
    return any(pattern in line for pattern in patterns)

def is_reply(line):
    return "Replying to " in line

def extract_key_content(content):
    # Extract the content between "Replying to " and the next double quote
    reply_match = re.search(r'Replying to "(.*)\.?\.?\.?"', content)
    react_match = re.search(r'Reacted to "(.*)\.?\.?\.?"', content)
    react_remove_match = re.search(r'Removed a .* reaction from "(.*)\.?\.?\.?"', content)
    if reply_match:
        return reply_match.group(1).strip()
    elif react_match:
        return react_match.group(1).strip()
    elif react_remove_match:
        return react_remove_match.group(1).strip()
    else:
        # if no match, return first 20 characters of content
        try:
            timestamp, rest = content.split("From", 1)
        except ValueError:
            rest = content
        try:
            name, message = rest.split(" to Everyone: ", 1)
        except ValueError:
            message = content
        if len(message) > 20:
            return f"{message[:20]}...".strip()
        else:
            return message.strip()



# Define the function to condense messages and store in a variable instead of writing to a file
def condense_messages_to_var(input_path):
    condensed_messages = []
    with open(input_path, 'r') as infile:
        current_message = None
        
        for line in infile:
            # Strip line and remove extra spaces
            stripped_line = line.strip()
            stripped_line = stripped_line.replace("\t", " ").replace("  ", " ")
            
            # Check if line starts with a timestamp pattern
            if stripped_line and len(stripped_line) > 8 and stripped_line[2] == ':' and stripped_line[5] == ':':
                # If we've accumulated a message, add it to the list and start a new one
                if current_message:
                    condensed_messages.append(current_message)
                current_message = stripped_line
            else:
                # Append line to current message
                if current_message:
                    current_message += " " + stripped_line
        
        # Add the last message if it exists
        if current_message:
            condensed_messages.append(current_message)
    
    return condensed_messages

def parse_messages(data):
    messages = []
    message_map = {}  # Used to map key content to the corresponding Message object for replies
    all_messages = {} # Used to map key content to the corresponding Message object for all messages
    last_message = None

    for line in data:
        stripped_line = line.strip()
        DEBUG and print(f"1: {line} -> {stripped_line}")

        # Skip emoji reactions and direct messages
        if is_emoji_related(stripped_line) or "(Direct Message)" in stripped_line:
            DEBUG and print(f"****** Skipping {stripped_line}")
            # parse reaction
            try:
                if "Reacted to" in stripped_line:
                    react_reacted = re.search(r'Reacted to "(.*?)" with (.)', stripped_line)
                    extracted_key = extract_key_content(stripped_line)
                    DEBUG and print(f"****** Parsing reaction: {react_reacted.group(2)}")
                    DEBUG and print(f"****** adding emoji to {all_messages[extracted_key].format()}")
                    all_messages[extracted_key].add_emoji(react_reacted.group(2))
                    DEBUG and print(f"****** extracted_key = {extracted_key}")
                    DEBUG and print(f"****** Added emoji to {all_messages[extracted_key].format()}")
                elif "Removed a" in stripped_line:
                    react_removed = re.search(r'Removed a (.).* reaction from "(.*?)"', stripped_line)
                    extracted_key = extract_key_content(stripped_line)
                    extracted_emoji = react_removed.group(1)
                    DEBUG and print(f"****** Parsing remove reaction: {extracted_emoji}")
                    all_messages[extracted_key].remove_emoji(extracted_emoji)
                elif "remove" in stripped_line:
                    react_remove = re.search(r'remove (.)', stripped_line)
                    DEBUG and print(f"****** Parsing remove reaction: {react_remove.group(1)}")
                    if last_message:
                        last_message.remove_emoji(react_remove.group(1))
                elif "add" in stripped_line:
                    react_add = re.search(r'add (.)', stripped_line)
                    DEBUG and print(f"****** Parsing add reaction: {react_add.group(1)}")
                    if last_message:
                        last_message.add_emoji(react_add.group(1))
                        DEBUG and print(f"****** Added emoji to {last_message.format()}")
                continue
            except KeyError:
                DEBUG and print(f"****** KeyError: {stripped_line}")
                continue

        # Extract key content for replies
        key_content = extract_key_content(stripped_line)
        DEBUG and print(f"2: {stripped_line} -> {key_content}")

        # If key content is found, it's a reply. Otherwise, it's a new message.
        if is_reply(stripped_line):
            DEBUG and print(f"3: {stripped_line}")
            if key_content in message_map:
                
                base_message = message_map[key_content]
                timestamp, rest = stripped_line.split(" From ", 1)
                name, content = rest.split(" to Everyone: ", 1)
                pattern = r'Replying to "(.*?)" (.*)'
                match = re.search(pattern, content)
                reply_text = match.group(2)
                reply = Message(timestamp, name, reply_text)
                last_message = reply
                base_message.add_reply(reply)
                reply_key = extract_key_content(reply_text)
                DEBUG and print(f"3.25: reply_key = {reply_key}")
                all_messages[reply_key] = reply
                DEBUG and print(f"3.5: Reply [{timestamp} {name}: {reply_text}] added to message [{key_content}]")
                DEBUG and print(f"  replies: {message.replies}")
            else:
                # reply not found in map
                DEBUG and print(f"****** ###### Reply not found in map: {stripped_line} -> {key_content}")
        else:
            #Conditionally print based on debug flag
            DEBUG and print(f"4: {stripped_line}")
            timestamp, rest = stripped_line.split(" From ", 1)
            name, content = rest.split(" to Everyone: ", 1)
            message = Message(timestamp, name, content)
            messages.append(message)
            last_message = message
            DEBUG and print(f"  Added message: {message.content}")
            message_map[key_content] = message
            all_messages[key_content] = message
            DEBUG and print(f"  Current message_map: {message_map}")

    return messages

class TestMessageParsing(unittest.TestCase):
    def setUp(self):
        self.sample_data = [
            "10:01:00 From John Doe to Everyone: Good morning folks",  # Message 1
            "10:04:30 From Frank Brank to Everyone: add 👍🏻",    # Reaction 2
            "10:05:00 From Evan Bevan to Everyone: add 👍",     # Reaction 3
            "10:06:00 From Frank Brank to Everyone: add 👍", # Reaction 4
            "10:06:00 From Alice Balice to Everyone: add 🍪",
            "10:02:00 From Alice AP SWE to Everyone: Replying to \"Good morning folks\" Hi John", # M1 Reply 1
            "10:03:00 From Jane Smith to Everyone: Replying to \"Good morning folks\" Hello there, John!", # M1 Reply 2
            "10:04:00 From Charlie (she/her) to Everyone: Reacted to \"Good morning folks\" with 👋", # Reaction 1
            "10:04:30 From Frank Brank to Everyone: add ☝️",    # Reaction 2
            "10:05:00 From Evan Bevan to Everyone: add 💯",     # Reaction 3
            "10:06:00 From Frank Brank to Everyone: remove ☝️", # Reaction 4
            "10:07:00 From Jack Doe to Everyone: Hello world, this message is longer than 20 characters!", # Message 2
            "10:08:00 From Diane Smith to Everyone: Replying to \"Hello world, this me...\" Hello there, Jack!", # M1 Reply 2
            "10:09:00 From John Doe to Open Mike(Direct Message): Please mute", # DM 1
            "10:06:00 From Alice Balice to Everyone: Removed a 🍪 reaction from \"Good morning folks\"",
        ]

    def test_basic_message_parsing(self):
        result = parse_messages(self.sample_data)
        self.assertEqual(result[0].content, "Good morning folks")

    def test_basic_message_parsing_longer(self):
        result = parse_messages(self.sample_data)
        self.assertEqual(result[1].content, "Hello world, this message is longer than 20 characters!")

    def test_emoji_message_removal(self):
        result = parse_messages(self.sample_data)
        self.assertNotIn("☝️", result[0].replies[1].format())

    def test_emoji_message_distant_removal(self):
        result = parse_messages(self.sample_data)
        self.assertNotIn("🍪", result[0].format())

    def test_consolidate_emoji(self):
        result = parse_messages(self.sample_data)
        self.assertIn("👍x3", result[0].format())

    def test_emoji_message_addition(self):
        result = parse_messages(self.sample_data)
        self.assertIn("💯x1", result[0].replies[1].format())

    def test_emoji_message_reacted_addition(self):
        result = parse_messages(self.sample_data)
        self.assertIn("👋x1", result[0].format())

    def test_dm_message_removal(self):
        result = parse_messages(self.sample_data)
        self.assertNotIn("Please mute", [msg.content for msg in result])

    def test_reply_parsing_short_key(self):
        result = parse_messages(self.sample_data)
        formatted_results = [reply.format() for reply in result[0].replies]
        self.assertIn("10:02:00 Alice AP SWE: Hi John", formatted_results)

    def test_reply_parsing_long_key(self):
        result = parse_messages(self.sample_data)
        formatted_results = [reply.format() for reply in result[1].replies]
        self.assertIn("10:08:00 Diane Smith: Hello there, Jack!", formatted_results)

    def test_extract_key_content(self):
        # Test a typical reply
        content = "10:09:00 From Diane Smith to Everyone: Replying to \"Good morning folks\" Totally agree"
        self.assertEqual(extract_key_content(content), "Good morning folks")

    def test_extract_key_content_2(self):
        # Test a reply without trailing dots
        content = "10:09:00 From Diane Smith to Everyone: Replying to \"Good morning\" Right, no trailing dots!"
        self.assertEqual(extract_key_content(content), "Good morning")
    def test_extract_key_content_3(self):
        # Test a non-reply message
        content = "10:09:00 From Diane Smith to Everyone: Hello world!"
        self.assertEqual(extract_key_content(content), "Hello world!")
    def test_extract_key_content_4(self):
        # Test with special characters
        content = "10:09:00 From Diane Smith to Everyone: Replying to \"Hi! How's it going?\" It's going well!"
        self.assertEqual(extract_key_content(content), "Hi! How's it going?")

    def test_extract_key_content_5(self):
        content = "10:09:00 From Diane Smith to Everyone: Replying to \"Hello world, this me...\" It's going well!"
        self.assertEqual(extract_key_content(content), "Hello world, this me...")

    def test_extract_reply_key_long(self):
        content = "Hello world, this message is longer than 20 characters!"
        self.assertEqual(extract_key_content(content), "Hello world, this me...")

    def test_extract_reply_key_short(self):
        content = "Hello world!"
        self.assertEqual(extract_key_content(content), "Hello world!")

    def test_extract_reply_key_emoji(self):
        content = "10:04:00 From Charlie (she/her) to Everyone: Reacted to \"Good morning folks\" with 👋"
        self.assertEqual(extract_key_content(content), "Good morning folks")

if __name__ == "__main__":
    import sys

    # Check if we're running tests or executing script directly
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        DEBUG = False
        unittest.main(argv=sys.argv[:1])  # Run tests
    else:
        if len(sys.argv) > 1:
            input_file = sys.argv[1]
        else:
            print("No input file specified, using default 'meeting_saved_chat.txt'")
            input_file = "meeting_saved_chat.txt"
        try:
            output_data_var = condense_messages_to_var(input_file)
        except FileNotFoundError:
            DEBUG and print(f"File '{input_file}' not found.")
            exit(1)
        messages = parse_messages(output_data_var)
        for msg in messages:
            msg.display(indent="  ")
