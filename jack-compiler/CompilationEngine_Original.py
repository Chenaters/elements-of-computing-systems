from JackTokenizer import JackTokenizer


class CompilationEngine:
    def __init__(self, input_path, output_path):
        self.tokenizer = JackTokenizer(input_path, open(input_path, 'r'))
        self.output_file = open(output_path, 'w')

    def compileClass(self):
        self.tokenizer.advance()  # 'class'
        self.output_file.write("<class>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'class'
        self.tokenizer.advance()  # class name
        self.output_file.write("<identifier> " + self.tokenizer.identifier() +
                               " </identifier>\n")
        self.tokenizer.advance()  # '{'
        self.output_file.write("<symbol> { </symbol>\n")

        self.tokenizer.advance()  # 'static' or 'field' or subroutine
        while self.tokenizer.currentToken in ['static', 'field']:
            self.compileClassVarDec()  # Compile class variable declarations
            self.tokenizer.advance()  # 'static' or 'field' or subroutine

        while self.tokenizer.currentToken in ['constructor',
                                              'function',
                                              'method']:
            self.compileSubroutineDec()  # Compile subroutine declarations
            self.tokenizer.advance()  # 'static' or 'field' or subroutine

        self.tokenizer.advance()  # '}'
        self.output_file.write("<symbol> } </symbol>\n")
        self.tokenizer.advance()  # 'class'
        self.output_file.write("</class>\n")

    def compileClassVarDec(self):
        self.output_file.write("<classVarDec>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'static' or 'field'
        self.tokenizer.advance()  # variable type
        if self.tokenizer.tokenType() == "KEYWORD":
            self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                                   " </keyword>\n")  # variable type
        else:
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")  # variable type
        self.tokenizer.advance()  # variable name
        self.output_file.write("<identifier> " + self.tokenizer.identifier() +
                               " </identifier>\n")  # variable name
        self.tokenizer.advance()  # ',' or ';'
        while self.tokenizer.currentToken == ',':
            self.output_file.write("<symbol> , </symbol>\n")
            self.tokenizer.advance()  # variable name
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")  # variable name
            self.tokenizer.advance()  # ',' or ';'
        self.output_file.write("<symbol> ; </symbol>\n")
        self.output_file.write("</classVarDec>\n")

    def compileSubroutineDec(self):
        self.output_file.write("<subroutineDec>\n")
        self.output_file.write(
            "<keyword> " +
            self.tokenizer.keyWord() +
            " </keyword>\n")  # 'constructor' or 'function' or 'method'
        if self.tokenizer.currentToken == 'constructor':
            self.tokenizer.advance()  # 'constructor'
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")  # 'constructor'
        else:
            self.tokenizer.advance()  # 'void' or return type
            self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                                   " </keyword>\n")  # 'void' or return type
        self.tokenizer.advance()  # subroutine name
        self.output_file.write("<identifier> " + self.tokenizer.identifier() +
                               " </identifier>\n")  # subroutine name
        self.tokenizer.advance()  # '('
        self.output_file.write("<symbol> ( </symbol>\n")

        self.tokenizer.advance()  # parameter list or ')'
        self.compileParameterList()  # Compile parameter list
        self.output_file.write("<symbol> ) </symbol>\n")

        self.compileSubroutineBody()  # Compile subroutine body

        self.output_file.write("</subroutineDec>\n")

    def compileParameterList(self):
        self.output_file.write("<parameterList>\n")
        if self.tokenizer.currentToken == ')':
            self.output_file.write("</parameterList>\n")
            return
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # parameter type
        self.tokenizer.advance()  # parameter name
        self.output_file.write("<identifier> " + self.tokenizer.identifier() +
                               " </identifier>\n")  # parameter name
        self.tokenizer.advance()  # ',' or ')'
        while self.tokenizer.currentToken == ',':
            self.output_file.write("<symbol> , </symbol>\n")
            self.tokenizer.advance()  # parameter type
            self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                                   " </keyword>\n")  # parameter type
            self.tokenizer.advance()  # parameter name
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")  # parameter name
            self.tokenizer.advance()  # ',' or ')'
        self.output_file.write("</parameterList>\n")

    def compileSubroutineBody(self):
        self.output_file.write("<subroutineBody>\n")
        self.tokenizer.advance()  # '{'
        self.output_file.write("<symbol> { </symbol>\n")
        self.tokenizer.advance()  # 'var' or statements
        while self.tokenizer.currentToken == 'var':
            self.compileVarDec()  # Compile variable declarations
            self.tokenizer.advance()  # 'var' or statements

        # Currently statements or }
        if self.tokenizer.currentToken != '}':
            self.compileStatements()  # Compile statements
        # Now current token should be '}'
        self.output_file.write("<symbol> } </symbol>\n")
        self.output_file.write("</subroutineBody>\n")

    def compileVarDec(self):
        self.output_file.write("<varDec>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'var'
        self.tokenizer.advance()  # ('int', 'char', 'boolean' or class name)
        if self.tokenizer.tokenType() == "KEYWORD":
            self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                                   " </keyword>\n")  # variable type
        else:
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")  # variable type (class name)
        self.tokenizer.advance()  # variable name
        self.output_file.write("<identifier> " + self.tokenizer.identifier() +
                               " </identifier>\n")  # variable name
        self.tokenizer.advance()  # ',' or ';'
        while self.tokenizer.currentToken == ',':
            self.output_file.write("<symbol> , </symbol>\n")
            self.tokenizer.advance()  # variable name
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")  # variable name
            self.tokenizer.advance()  # ',' or ';'
        self.output_file.write("<symbol> ; </symbol>\n")
        self.output_file.write("</varDec>\n")

    def compileStatements(self):
        self.output_file.write("<statements>\n")
        while self.tokenizer.currentToken in [
                'let', 'if', 'while', 'do', 'return']:
            if self.tokenizer.currentToken == 'let':
                self.compileLet()
            elif self.tokenizer.currentToken == 'if':
                self.compileIf()
            elif self.tokenizer.currentToken == 'while':
                self.compileWhile()
            elif self.tokenizer.currentToken == 'do':
                self.compileDo()
            elif self.tokenizer.currentToken == 'return':
                self.compileReturn()
        self.output_file.write("</statements>\n")

    def compileDo(self):
        self.output_file.write("<doStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'do'
        self.tokenizer.advance()  # subroutine call
        self.output_file.write("<identifier> " + self.tokenizer.identifier() +
                               " </identifier>\n")  # subroutine call
        self.tokenizer.advance()  # '. or '('
        if self.tokenizer.currentToken == '.':

            self.output_file.write("<symbol> . </symbol>\n")
            self.tokenizer.advance()  # subroutine name
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")  # subroutine name
            self.tokenizer.advance()  # '('
        self.output_file.write("<symbol> ( </symbol>\n")
        self.tokenizer.advance()  # expression list or ')'
        self.compileExpressionList()  # Compile expression list
        self.output_file.write("<symbol> ) </symbol>\n")
        self.tokenizer.advance()  # ';'
        self.output_file.write("<symbol> ; </symbol>\n")  # ';'
        self.output_file.write("</doStatement>\n")
        self.tokenizer.advance()  # Next statement or '}'

    def compileLet(self):
        self.output_file.write("<letStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'let'
        self.tokenizer.advance()  # variable name
        self.output_file.write("<identifier> " + self.tokenizer.identifier() +
                               " </identifier>\n")  # variable name
        self.tokenizer.advance()  # '=' or '['
        if self.tokenizer.currentToken == '[':
            self.output_file.write("<symbol> [ </symbol>\n")
            self.tokenizer.advance()  # array index expression
            self.compileExpression()  # Compile array index expression
            # self.tokenizer.advance()  # ']'
            self.output_file.write("<symbol> ] </symbol>\n")
            self.tokenizer.advance()  # '='
        self.output_file.write("<symbol> = </symbol>\n")
        self.tokenizer.advance()  # expression
        self.compileExpression()  # Compile right-hand side expression
        # self.tokenizer.advance()  # ';'
        self.output_file.write("<symbol> ; </symbol>\n")
        self.output_file.write("</letStatement>\n")
        self.tokenizer.advance()  # Next statement or '}'

    def compileIf(self):
        self.output_file.write("<ifStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'if'
        self.tokenizer.advance()  # '('
        self.output_file.write("<symbol> ( </symbol>\n")
        self.tokenizer.advance()  # condition expression
        self.compileExpression()  # Compile condition expression
        # self.tokenizer.advance()  # ')'
        self.output_file.write("<symbol> ) </symbol>\n")
        self.tokenizer.advance()  # '{'
        self.output_file.write("<symbol> { </symbol>\n")
        self.tokenizer.advance()  # statements or '}'
        self.compileStatements()  # Compile 'if' block statements
        # self.tokenizer.advance()  # '}'
        self.output_file.write("<symbol> } </symbol>\n")
        # Check for optional 'else' block
        self.tokenizer.advance()  # 'else' or next statement
        if self.tokenizer.currentToken == 'else':
            self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                                   " </keyword>\n")  # 'else'
            self.tokenizer.advance()  # '{'
            self.output_file.write("<symbol> { </symbol>\n")
            self.tokenizer.advance()  # first token in else block
            self.compileStatements()  # Compile 'else' block statements
            self.output_file.write("<symbol> } </symbol>\n")
            self.tokenizer.advance()  # Next statement or '}'
        self.output_file.write("</ifStatement>\n")

    def compileWhile(self):
        self.output_file.write("<whileStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'while'
        self.tokenizer.advance()  # '('
        self.output_file.write("<symbol> ( </symbol>\n")
        self.tokenizer.advance()  # condition expression
        self.compileExpression()  # Compile condition expression
        # self.tokenizer.advance()  # ')'
        self.output_file.write("<symbol> ) </symbol>\n")
        self.tokenizer.advance()  # '{'
        self.output_file.write("<symbol> { </symbol>\n")
        self.tokenizer.advance()  # statements or '}'
        self.compileStatements()  # Compile 'while' block statements
        # self.tokenizer.advance()  # '}'
        self.output_file.write("<symbol> } </symbol>\n")
        self.output_file.write("</whileStatement>\n")
        self.tokenizer.advance()  # Next statement or '}'

    def compileReturn(self):
        self.output_file.write("<returnStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'return'
        self.tokenizer.advance()  # expression or ';'
        if self.tokenizer.currentToken != ';':
            self.compileExpression()  # Compile return expression
            # self.tokenizer.advance()  # ';'
        self.output_file.write("<symbol> ; </symbol>\n")  # ';'
        self.output_file.write("</returnStatement>\n")
        self.tokenizer.advance()  # Next statement or '}'

    def compileExpression(self):
        self.output_file.write("<expression>\n")
        self.compileTerm()  # Compile first term
        while self.tokenizer.currentToken in [
                '+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.output_file.write(
                "<symbol> " +
                self._xml_symbol(
                    self.tokenizer.symbol()) +
                " </symbol>\n")  # operator
            self.tokenizer.advance()  # next term
            self.compileTerm()  # Compile next term
        self.output_file.write("</expression>\n")

    def _xml_symbol(self, symbol):
        if symbol == '<':
            return '&lt;'
        if symbol == '>':
            return '&gt;'
        if symbol == '&':
            return '&amp;'
        return symbol

    def compileTerm(self):
        # A term can be an integer constant, string constant, keyword constant,
        # variable, array entry, subroutine call, or an expression in ().
        self.output_file.write("<term>\n")

        token_type = self.tokenizer.tokenType()
        token = self.tokenizer.currentToken
        if token_type == "STRING_CONST":  # String constant
            self.output_file.write(
                "<stringConstant> " +
                self.tokenizer.stringVal() +
                " </stringConstant>\n")
            self.tokenizer.advance()
        elif token_type == "INT_CONST":  # Integer constant
            self.output_file.write("<integerConstant> " +
                                   str(self.tokenizer.intVal()) +
                                   " </integerConstant>\n")
            self.tokenizer.advance()
        # varname, varname[expression], subroutineCall
        elif token_type == "IDENTIFIER":
            # Write the identifier first.
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")
            self.tokenizer.advance()

            if self.tokenizer.currentToken == '[':  # array entry
                self.output_file.write("<symbol> [ </symbol>\n")
                self.tokenizer.advance()  # expression
                self.compileExpression()
                self.output_file.write("<symbol> ] </symbol>\n")
                self.tokenizer.advance()  # token after ']'
            elif self.tokenizer.currentToken == '(':  # subroutine call
                self.output_file.write("<symbol> ( </symbol>\n")
                self.tokenizer.advance()  # expression list or ')'
                self.compileExpressionList()
                self.output_file.write("<symbol> ) </symbol>\n")
                self.tokenizer.advance()  # token after ')'
            elif self.tokenizer.currentToken == '.':  # subroutine call
                self.output_file.write("<symbol> . </symbol>\n")
                self.tokenizer.advance()  # subroutine name
                self.output_file.write(
                    "<identifier> " +
                    self.tokenizer.identifier() +
                    " </identifier>\n")
                self.tokenizer.advance()  # '('
                self.output_file.write("<symbol> ( </symbol>\n")
                self.tokenizer.advance()  # expression list or ')'
                self.compileExpressionList()
                self.output_file.write("<symbol> ) </symbol>\n")
                self.tokenizer.advance()  # token after ')'
            else:
                pass  # plain variable term; token already advanced once above
        elif token == '(':  # expression in parentheses
            self.output_file.write("<symbol> ( </symbol>\n")
            self.tokenizer.advance()  # expression
            self.compileExpression()
            self.output_file.write("<symbol> ) </symbol>\n")
            self.tokenizer.advance()  # token after ')'
        elif token in ['-', '~']:  # unary operator and term
            self.output_file.write(
                "<symbol> " +
                self._xml_symbol(
                    self.tokenizer.symbol()) +
                " </symbol>\n")
            self.tokenizer.advance()  # unary term
            self.compileTerm()
        else:    # shouldn't happen
            self.output_file.write(
                "<" +
                token_type.lower() +
                "> " +
                token +
                " </" +
                token_type.lower() +
                ">\n")
            self.tokenizer.advance()

        self.output_file.write("</term>\n")

    def compileExpressionList(self):
        if self.tokenizer.currentToken == ')':
            self.output_file.write("<expressionList>\n")
            # Empty expression list
            self.output_file.write("</expressionList>\n")
            return
        self.output_file.write("<expressionList>\n")
        self.compileExpression()  # Compile expression
        while self.tokenizer.currentToken != ')':
            if self.tokenizer.currentToken == ',':
                self.output_file.write("<symbol> , </symbol>\n")
                self.tokenizer.advance()  # next expression
                self.compileExpression()  # Compile next expression
            else:
                break
        self.output_file.write("</expressionList>\n")  # Empty expression list
