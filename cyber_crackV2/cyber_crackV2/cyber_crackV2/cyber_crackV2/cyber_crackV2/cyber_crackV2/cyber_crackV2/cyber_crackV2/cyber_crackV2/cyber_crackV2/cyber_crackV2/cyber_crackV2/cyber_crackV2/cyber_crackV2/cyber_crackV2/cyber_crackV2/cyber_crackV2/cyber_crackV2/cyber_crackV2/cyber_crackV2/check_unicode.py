import tokenize
import io

def find_unicode_issues(filename):
    with open(filename, 'rb') as f:
        tokens = tokenize.tokenize(f.readline)
        for token in tokens:
            if token.type == tokenize.STRING or token.type == tokenize.NAME or token.type == tokenize.OP:
                try:
                    # Decode the token string to check for problematic chars
                    token_str = token.string
                    for i, char in enumerate(token_str):
                        if ord(char) > 127:
                            print(f"Found non-ASCII character at line {token.start[0]}, col {token.start[1] + i}: {char} (U+{ord(char):04X})")
                except:
                    continue

# Check the file
find_unicode_issues('frontend/telegram_bot.py')