class JackTokenizer:
    keywords = {
        "class", "constructor", "function", "method", "field", "static",
        "var", "int", "char", "boolean", "void", "true", "false",
        "null", "this", "let", "do", "if", "else", "while", "return",
        "coroutine", "task", "yield", "finish"
    }

    symbols = {
        '{', '}', '(', ')', '[', ']', '.', ',', ';',
        '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'
    }

    def __init__(self, inputFile, stream):
        self.inputFile = inputFile
        self.stream = stream
        self.currentToken = None

    def hasMoreTokens(self):
        pos = self.stream.tell()
        char = self.stream.read(1)
        self.stream.seek(pos)
        return char != ''

    def advance(self):
        # Read a full token
        reading = True
        token = ""
        while reading:
            pos = self.stream.tell()
            char = self.stream.read(1)
            if char == '':  # End of file
                token += char
                self.currentToken = token
                break
            elif char == " " or char == "\n" or char == "\t":
                if token:
                    self.currentToken = token
                    break
                else:
                    continue
            elif char == '/':  # Possible start of comment
                if token:
                    self.currentToken = token
                    self.stream.seek(pos)  # Put back the '/' for next token
                    reading = False
                    break
                next_char = self.stream.read(1)
                if next_char == '/':  # Single-line comment
                    while char != '\n' and char != '':
                        char = self.stream.read(1)
                    continue
                elif next_char == '*':  # Multi-line comment
                    prev_char = ''
                    while True:
                        char = self.stream.read(1)
                        if char == '' or (prev_char == '*' and char == '/'):
                            break
                        prev_char = char
                    continue
                else:  # Just a division symbol
                    self.stream.seek(pos)
                    self.stream.read(1)  # consume '/'
                    self.currentToken = '/'
                    reading = False
                    break
            elif char in self.symbols:
                if token:
                    self.currentToken = token
                    self.stream.seek(pos)  # Put back the symbol for next token
                else:
                    self.currentToken = char
                break
            elif char == '"':  # Start of string constant
                if token:
                    self.currentToken = token
                    self.stream.seek(pos)  # Put back the quote for next token
                    break
                else:
                    token += char
                    while True:
                        char = self.stream.read(1)
                        if char == '':  # End of file
                            token += char
                            self.currentToken = token
                            reading = False
                            break
                        token += char
                        if char == '"':  # End of string constant
                            self.currentToken = token
                            reading = False
                            break

            token += char

    def tokenType(self):
        if self.currentToken in self.keywords:
            return "KEYWORD"
        elif self.currentToken in self.symbols:
            return "SYMBOL"
        elif self.currentToken.isdigit():
            return "INT_CONST"
        elif (self.currentToken.startswith('"') and
              self.currentToken.endswith('"')):
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    # For different types (keyword, symbol, identifier, intVal, stringVal)

    def keyWord(self):
        if self.tokenType() == "KEYWORD":
            return self.currentToken

    def symbol(self):
        if self.tokenType() == "SYMBOL":
            return self.currentToken

    def identifier(self):
        if self.tokenType() == "IDENTIFIER":
            return self.currentToken

    def intVal(self):
        if self.tokenType() == "INT_CONST":
            return int(self.currentToken)

    def stringVal(self):
        if self.tokenType() == "STRING_CONST":
            return self.currentToken[1:-1]
