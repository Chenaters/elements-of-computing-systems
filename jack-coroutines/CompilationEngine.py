from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable 
from VMWriter import VMWriter


class CompilationEngine:
    def __init__(self, input_path, output_path):
        self.tokenizer = JackTokenizer(input_path, open(input_path, 'r'))
        self.output_file = open(output_path + ".xml", 'w')
        self.vm_writer = VMWriter(output_path + ".vm")
        self.class_symbol_table = SymbolTable()
        self.subroutine_symbol_table = SymbolTable()
        self.current_class_name = None
        self.current_subroutine_name = None
        self.current_subroutine_kind = None
        self.label_counter = 0
        self.current_class_is_coroutine = False
        self.current_task_resume_labels = []
        self.current_task_done_label = None

    
    def compileClass(self):
        self.tokenizer.advance()  # 'coroutine' or 'class'
        self.output_file.write("<class>\n")
        self.current_class_is_coroutine = False
        if self.tokenizer.currentToken == 'coroutine':
            self.current_class_is_coroutine = True
            self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                                   " </keyword>\n")
            self.tokenizer.advance()  # 'class'
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'class'
        self.tokenizer.advance()  # class name
        self.current_class_name = self.tokenizer.identifier()
        self.output_file.write("<identifier> " + self.tokenizer.identifier() +
                               " </identifier>\n")
        self.tokenizer.advance()  # '{'
        self.output_file.write("<symbol> { </symbol>\n")
        if self.current_class_is_coroutine:
            # Internal coroutine bookkeeping fields, persisted per instance.
            self._define_class_symbol('__state', 'int', 'field')
            self._define_class_symbol('__finished', 'boolean', 'field')

        self.tokenizer.advance()  # 'static' or 'field' or subroutine
        while self.tokenizer.currentToken in ['static', 'field']:
            self.compileClassVarDec()  # Compile class variable declarations
            self.tokenizer.advance()  # 'static' or 'field' or subroutine

        while self.tokenizer.currentToken in ['constructor',
                                              'function',
                                              'method',
                                              'task']:
            self.compileSubroutineDec()  # Compile subroutine declarations
            self.tokenizer.advance()  # 'static' or 'field' or subroutine

        self.tokenizer.advance()  # '}'
        self.output_file.write("<symbol> } </symbol>\n")
        self.tokenizer.advance()  # 'class'
        self.output_file.write("</class>\n")
        self.vm_writer.close()
        self.output_file.close()

    def _write_identifier(self):
        identifier = self.tokenizer.identifier()
        self.output_file.write("<identifier> " + identifier + " </identifier>\n")
        return identifier

    def _define_class_symbol(self, name, symbol_type, kind):
        if kind not in ['static', 'field']:
            raise ValueError("Class symbol kind must be 'static' or 'field'.")
        self.class_symbol_table.define(name, symbol_type, kind)

    def _define_subroutine_symbol(self, name, symbol_type, kind):
        if kind not in ['arg', 'var']:
            raise ValueError("Subroutine symbol kind must be 'arg' or 'var'.")
        self.subroutine_symbol_table.define(name, symbol_type, kind)

    def _new_label(self, prefix):
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label

    def _is_coroutine_task(self):
        return self.current_class_is_coroutine and self.current_subroutine_kind == 'task'

    def _coroutine_field_index(self, field_name):
        kind, _, index = self._resolve_symbol(field_name)
        if kind != 'field' or index is None:
            raise ValueError(f"Missing internal coroutine field '{field_name}'")
        return index

    def _emit_task_dispatch(self):
        state_index = self._coroutine_field_index('__state')
        finished_index = self._coroutine_field_index('__finished')
        task_start_label = self._new_label(f"{self.current_class_name}${self.current_subroutine_name}$start$")

        self.vm_writer.writePush('this', finished_index)
        self.vm_writer.writeIf(self.current_task_done_label)

        for state_value, resume_label in enumerate(self.current_task_resume_labels, start=1):
            self.vm_writer.writePush('this', state_index)
            self.vm_writer.writePush('constant', state_value)
            self.vm_writer.writeArithmetic('eq')
            self.vm_writer.writeIf(resume_label)

        self.vm_writer.writePush('this', state_index)
        self.vm_writer.writePush('constant', 0)
        self.vm_writer.writeArithmetic('eq')
        self.vm_writer.writeIf(task_start_label)
        self.vm_writer.writeGoto(self.current_task_done_label)
        self.vm_writer.writeLabel(task_start_label)


    def compileClassVarDec(self):
        self.output_file.write("<classVarDec>\n")
        var_kind = self.tokenizer.keyWord()
        self.output_file.write("<keyword> " + var_kind +
                               " </keyword>\n")  # 'static' or 'field'
        self.tokenizer.advance()  # variable type
        if self.tokenizer.tokenType() == "KEYWORD":
            var_type = self.tokenizer.keyWord()
            self.output_file.write("<keyword> " + var_type +
                                   " </keyword>\n")  # variable type
        else:
            var_type = self.tokenizer.identifier()
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")  # variable type
        self.tokenizer.advance()  # variable name
        var_name = self._write_identifier()  # variable name
        self._define_class_symbol(var_name, var_type, var_kind)
        self.tokenizer.advance()  # ',' or ';'
        while self.tokenizer.currentToken == ',':
            self.output_file.write("<symbol> , </symbol>\n")
            self.tokenizer.advance()  # variable name
            var_name = self._write_identifier()  # variable name
            self._define_class_symbol(var_name, var_type, var_kind)
            self.tokenizer.advance()  # ',' or ';'
        self.output_file.write("<symbol> ; </symbol>\n")
        self.output_file.write("</classVarDec>\n")

    def compileSubroutineDec(self):
        self.subroutine_symbol_table.reset() # Reset method-level symbol table for new subroutine
        self.output_file.write("<subroutineDec>\n")
        self.current_subroutine_kind = self.tokenizer.keyWord()
        if self.current_subroutine_kind in ['method', 'task']:
            self._define_subroutine_symbol('this', self.current_class_name, 'arg')
        self.output_file.write(
            "<keyword> " +
            self.tokenizer.keyWord() +
            " </keyword>\n")  # 'constructor' or 'function' or 'method' or 'task'
        if self.tokenizer.currentToken == 'constructor':
            self.tokenizer.advance()  # 'constructor'
            self._write_identifier()  # class type
            self.tokenizer.advance()  # subroutine name
        elif self.tokenizer.currentToken == 'task':
            self.tokenizer.advance()  # subroutine name
        else:
            self.tokenizer.advance()  # 'void' or return type
            if self.tokenizer.tokenType() == "KEYWORD":
                self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                                       " </keyword>\n")  # 'void' or return type
            else:
                self._write_identifier()  # class return type
            self.tokenizer.advance()  # subroutine name
        self.current_subroutine_name = self._write_identifier()  # subroutine name
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
        if self.tokenizer.tokenType() == "KEYWORD":
            param_type = self.tokenizer.keyWord()
            self.output_file.write("<keyword> " + param_type +
                                   " </keyword>\n")  # parameter type
        else:
            param_type = self.tokenizer.identifier()
            self._write_identifier()  # parameter type
        self.tokenizer.advance()  # parameter name
        param_name = self._write_identifier()  # parameter name
        self._define_subroutine_symbol(param_name, param_type, 'arg')
        self.tokenizer.advance()  # ',' or ')'
        while self.tokenizer.currentToken == ',':
            self.output_file.write("<symbol> , </symbol>\n")
            self.tokenizer.advance()  # parameter type
            if self.tokenizer.tokenType() == "KEYWORD":
                param_type = self.tokenizer.keyWord()
                self.output_file.write("<keyword> " + param_type +
                                       " </keyword>\n")  # parameter type
            else:
                param_type = self.tokenizer.identifier()
                self._write_identifier()  # parameter type
            self.tokenizer.advance()  # parameter name
            param_name = self._write_identifier()  # parameter name
            self._define_subroutine_symbol(param_name, param_type, 'arg')
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

        function_name = self.current_class_name + '.' + self.current_subroutine_name
        n_locals = self.subroutine_symbol_table.varCount('var')
        self.vm_writer.writeFunction(function_name, n_locals)

        if self.current_subroutine_kind == 'constructor':
            n_fields = self.class_symbol_table.varCount('field')
            self.vm_writer.writePush('constant', n_fields)
            self.vm_writer.writeCall('Memory.alloc', 1)
            self.vm_writer.writePop('pointer', 0)
            if self.current_class_is_coroutine:
                state_index = self._coroutine_field_index('__state')
                finished_index = self._coroutine_field_index('__finished')
                self.vm_writer.writePush('constant', 0)
                self.vm_writer.writePop('this', state_index)
                self.vm_writer.writePush('constant', 0)
                self.vm_writer.writePop('this', finished_index)
        elif self.current_subroutine_kind in ['method', 'task']:
            self.vm_writer.writePush('argument', 0)
            self.vm_writer.writePop('pointer', 0)

        task_buffered_lines = None
        if self._is_coroutine_task():
            self.current_task_resume_labels = []
            self.current_task_done_label = self._new_label(
                f"{self.current_class_name}${self.current_subroutine_name}$done$"
            )
            self.vm_writer.beginBuffer()

        # Currently statements or }
        if self.tokenizer.currentToken != '}':
            self.compileStatements()  # Compile statements

        if self._is_coroutine_task():
            task_buffered_lines = self.vm_writer.endBuffer()
            self._emit_task_dispatch()
            self.vm_writer.writeBuffered(task_buffered_lines)
            self.vm_writer.writePush('constant', 0)
            self.vm_writer.writeReturn()
            self.vm_writer.writeLabel(self.current_task_done_label)
            self.vm_writer.writePush('constant', 0)
            self.vm_writer.writeReturn()
            self.current_task_resume_labels = []
            self.current_task_done_label = None

        # Now current token should be '}'
        self.output_file.write("<symbol> } </symbol>\n")
        self.output_file.write("</subroutineBody>\n")

    def compileVarDec(self):
        self.output_file.write("<varDec>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'var'
        self.tokenizer.advance()  # ('int', 'char', 'boolean' or class name)
        if self.tokenizer.tokenType() == "KEYWORD":
            var_type = self.tokenizer.keyWord()
            self.output_file.write("<keyword> " + var_type +
                                   " </keyword>\n")  # variable type
        else:
            var_type = self.tokenizer.identifier()
            self._write_identifier()  # variable type (class name)
        self.tokenizer.advance()  # variable name
        var_name = self._write_identifier()  # variable name
        self._define_subroutine_symbol(var_name, var_type, 'var')
        self.tokenizer.advance()  # ',' or ';'
        while self.tokenizer.currentToken == ',':
            self.output_file.write("<symbol> , </symbol>\n")
            self.tokenizer.advance()  # variable name
            var_name = self._write_identifier()  # variable name
            self._define_subroutine_symbol(var_name, var_type, 'var')
            self.tokenizer.advance()  # ',' or ';'
        self.output_file.write("<symbol> ; </symbol>\n")
        self.output_file.write("</varDec>\n")

    def compileStatements(self):
        self.output_file.write("<statements>\n")
        while self.tokenizer.currentToken in [
                'let', 'if', 'while', 'do', 'return', 'yield', 'finish']:
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
            elif self.tokenizer.currentToken == 'yield':
                self.compileYield()
            elif self.tokenizer.currentToken == 'finish':
                self.compileFinish()
        self.output_file.write("</statements>\n")

    def compileYield(self):
        self.output_file.write("<yieldStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'yield'
        self.tokenizer.advance()  # ';'
        self.output_file.write("<symbol> ; </symbol>\n")
        if self._is_coroutine_task():
            state_index = self._coroutine_field_index('__state')
            next_state = len(self.current_task_resume_labels) + 1
            resume_label = self._new_label(
                f"{self.current_class_name}${self.current_subroutine_name}$resume$"
            )
            self.current_task_resume_labels.append(resume_label)
            self.vm_writer.writePush('constant', next_state)
            self.vm_writer.writePop('this', state_index)
            self.vm_writer.writePush('constant', 0)
            self.vm_writer.writeReturn()
            self.vm_writer.writeLabel(resume_label)
        else:
            self.vm_writer.writePush('constant', 0)
            self.vm_writer.writeReturn()
        self.output_file.write("</yieldStatement>\n")
        self.tokenizer.advance()  # Next statement or '}'

    def compileFinish(self):
        self.output_file.write("<finishStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'finish'
        self.tokenizer.advance()  # ';'
        self.output_file.write("<symbol> ; </symbol>\n")
        if self._is_coroutine_task():
            state_index = self._coroutine_field_index('__state')
            finished_index = self._coroutine_field_index('__finished')
            self.vm_writer.writePush('constant', 1)
            self.vm_writer.writePop('this', finished_index)
            self.vm_writer.writePush('constant', 0)
            self.vm_writer.writePop('this', state_index)
        self.vm_writer.writePush('constant', 0)
        self.vm_writer.writeReturn()
        self.output_file.write("</finishStatement>\n")
        self.tokenizer.advance()  # Next statement or '}'

    def _compile_subroutine_call(self, identifier_name):
        n_args = 0
        if self.tokenizer.currentToken == '(':
            self.output_file.write("<symbol> ( </symbol>\n")
            self.vm_writer.writePush('pointer', 0)
            n_args = 1
            self.tokenizer.advance()  # expression list or ')'
            n_args += self.compileExpressionList()
            self.output_file.write("<symbol> ) </symbol>\n")
            self.tokenizer.advance()  # token after ')'
            call_name = self.current_class_name + '.' + identifier_name
        else:
            self.output_file.write("<symbol> . </symbol>\n")
            self.tokenizer.advance()  # subroutine name
            subroutine_name = self.tokenizer.identifier()
            self.output_file.write(
                "<identifier> " +
                subroutine_name +
                " </identifier>\n")
            self.tokenizer.advance()  # '('
            self.output_file.write("<symbol> ( </symbol>\n")

            kind, symbol_type, _ = self._resolve_symbol(identifier_name)
            if kind is not None:
                self._push_identifier_value(identifier_name)
                call_name = symbol_type + '.' + subroutine_name
                n_args = 1
            else:
                call_name = identifier_name + '.' + subroutine_name

            self.tokenizer.advance()  # expression list or ')'
            n_args += self.compileExpressionList()
            self.output_file.write("<symbol> ) </symbol>\n")
            self.tokenizer.advance()  # token after ')'

        self.vm_writer.writeCall(call_name, n_args)

    def compileDo(self):
        self.output_file.write("<doStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'do'
        self.tokenizer.advance()  # subroutine call
        call_base_name = self.tokenizer.identifier()
        self.output_file.write("<identifier> " + call_base_name +
                               " </identifier>\n")  # subroutine call
        self.tokenizer.advance()  # '. or '('
        self._compile_subroutine_call(call_base_name)
        self.vm_writer.writePop('temp', 0)
        self.output_file.write("<symbol> ; </symbol>\n")  # ';'
        self.output_file.write("</doStatement>\n")
        self.tokenizer.advance()  # Next statement or '}'

    def compileLet(self):
        self.output_file.write("<letStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'let'
        self.tokenizer.advance()  # variable name
        variable_name = self.tokenizer.identifier()
        self.output_file.write("<identifier> " + variable_name +
                               " </identifier>\n")  # variable name
        self.tokenizer.advance()  # '=' or '['
        is_array_assignment = False
        if self.tokenizer.currentToken == '[':
            is_array_assignment = True
            self.output_file.write("<symbol> [ </symbol>\n")
            self.tokenizer.advance()  # array index expression
            self.compileExpression()  # Compile array index expression
            self._push_identifier_value(variable_name)
            self.vm_writer.writeArithmetic('add')
            # self.tokenizer.advance()  # ']'
            self.output_file.write("<symbol> ] </symbol>\n")
            self.tokenizer.advance()  # '='
        self.output_file.write("<symbol> = </symbol>\n")
        self.tokenizer.advance()  # expression
        self.compileExpression()  # Compile right-hand side expression
        if is_array_assignment:
            self.vm_writer.writePop('temp', 0)
            self.vm_writer.writePop('pointer', 1)
            self.vm_writer.writePush('temp', 0)
            self.vm_writer.writePop('that', 0)
        else:
            kind, _, index = self._resolve_symbol(variable_name)
            segment = self._segment_for_kind(kind)
            if segment is None or index is None:
                raise ValueError(f"Unknown variable '{variable_name}'")
            self.vm_writer.writePop(segment, index)
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
        self.vm_writer.writeArithmetic('not')
        end_label = self._new_label(f"{self.current_class_name}_")
        false_label = self._new_label(f"{self.current_class_name}_")
        self.vm_writer.writeIf(false_label)
        # self.tokenizer.advance()  # ')'
        self.output_file.write("<symbol> ) </symbol>\n")
        self.tokenizer.advance()  # '{'
        self.output_file.write("<symbol> { </symbol>\n")
        self.tokenizer.advance()  # statements or '}'
        self.compileStatements()  # Compile 'if' block statements
        self.vm_writer.writeGoto(end_label)
        # self.tokenizer.advance()  # '}'
        self.output_file.write("<symbol> } </symbol>\n")
        # Check for optional 'else' block
        self.tokenizer.advance()  # 'else' or next statement
        self.vm_writer.writeLabel(false_label)
        if self.tokenizer.currentToken == 'else':
            self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                                   " </keyword>\n")  # 'else'
            self.tokenizer.advance()  # '{'
            self.output_file.write("<symbol> { </symbol>\n")
            self.tokenizer.advance()  # first token in else block
            self.compileStatements()  # Compile 'else' block statements
            self.output_file.write("<symbol> } </symbol>\n")
            self.tokenizer.advance()  # Next statement or '}'
        self.vm_writer.writeLabel(end_label)
        self.output_file.write("</ifStatement>\n")

    def compileWhile(self):
        self.output_file.write("<whileStatement>\n")
        self.output_file.write("<keyword> " + self.tokenizer.keyWord() +
                               " </keyword>\n")  # 'while'
        start_label = self._new_label(f"{self.current_class_name}_")
        end_label = self._new_label(f"{self.current_class_name}_")
        self.vm_writer.writeLabel(start_label)
        self.tokenizer.advance()  # '('
        self.output_file.write("<symbol> ( </symbol>\n")
        self.tokenizer.advance()  # condition expression
        self.compileExpression()  # Compile condition expression
        self.vm_writer.writeArithmetic('not')
        self.vm_writer.writeIf(end_label)
        self.output_file.write("<symbol> ) </symbol>\n")
        self.tokenizer.advance()  # '{'
        self.output_file.write("<symbol> { </symbol>\n")
        self.tokenizer.advance()  # statements or '}'
        self.compileStatements()  # Compile 'while' block statements
        self.vm_writer.writeGoto(start_label)
        self.vm_writer.writeLabel(end_label)
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
        else:
            self.vm_writer.writePush('constant', 0)
        self.vm_writer.writeReturn()
        self.output_file.write("<symbol> ; </symbol>\n")  # ';'
        self.output_file.write("</returnStatement>\n")
        self.tokenizer.advance()  # Next statement or '}'

    def compileExpression(self):
        self.output_file.write("<expression>\n")
        self.compileTerm()  # Compile first term
        while self.tokenizer.currentToken in [
                '+', '-', '*', '/', '&', '|', '<', '>', '=']:
            operator = self.tokenizer.currentToken
            self.output_file.write(
                "<symbol> " +
                self._xml_symbol(operator) +
                " </symbol>\n")  # operator
            self.tokenizer.advance()  # next term
            self.compileTerm()  # Compile next term
            self._write_binary_operator_vm(operator)
            
        self.output_file.write("</expression>\n")

    def _xml_symbol(self, symbol):
        if symbol == '<':
            return '&lt;'
        if symbol == '>':
            return '&gt;'
        if symbol == '&':
            return '&amp;'
        return symbol

    def _segment_for_kind(self, kind):
        if kind == 'static':
            return 'static'
        if kind == 'field':
            return 'this'
        if kind == 'arg':
            return 'argument'
        if kind == 'var':
            return 'local'
        return None

    def _resolve_symbol(self, name): # Determine and find the symbol in subroutine or class symbol table
        kind = self.subroutine_symbol_table.kindOf(name)
        symbol_type = self.subroutine_symbol_table.typeOf(name)
        index = self.subroutine_symbol_table.indexOf(name)
        if kind is None:
            kind = self.class_symbol_table.kindOf(name)
            symbol_type = self.class_symbol_table.typeOf(name)
            index = self.class_symbol_table.indexOf(name)
        return kind, symbol_type, index

    def _push_identifier_value(self, name):
        kind, _, index = self._resolve_symbol(name)
        segment = self._segment_for_kind(kind)
        if segment is None or index is None:
            raise ValueError(f"Unknown identifier '{name}'")
        self.vm_writer.writePush(segment, index)

    def _write_binary_operator_vm(self, operator):
        if operator == '+':
            self.vm_writer.writeArithmetic('add')
        elif operator == '-':
            self.vm_writer.writeArithmetic('sub')
        elif operator == '&':
            self.vm_writer.writeArithmetic('and')
        elif operator == '|':
            self.vm_writer.writeArithmetic('or')
        elif operator == '<':
            self.vm_writer.writeArithmetic('lt')
        elif operator == '>':
            self.vm_writer.writeArithmetic('gt')
        elif operator == '=':
            self.vm_writer.writeArithmetic('eq')
        elif operator == '*':
            self.vm_writer.writeCall('Math.multiply', 2)
        elif operator == '/':
            self.vm_writer.writeCall('Math.divide', 2)

    def _write_unary_operator_vm(self, operator):
        if operator == '-':
            self.vm_writer.writeArithmetic('neg')
        elif operator == '~':
            self.vm_writer.writeArithmetic('not')

    def compileTerm(self):
        self.output_file.write("<term>\n")

        token_type = self.tokenizer.tokenType()
        token = self.tokenizer.currentToken
        if token_type == "STRING_CONST":  # String constant
            self.output_file.write(
                "<stringConstant> " +
                self.tokenizer.stringVal() +
                " </stringConstant>\n")
            # VM code to create string object and append characters
            self.vm_writer.writePush("constant", len(self.tokenizer.stringVal()))
            self.vm_writer.writeCall("String.new", 1)
            for char in self.tokenizer.stringVal():
                self.vm_writer.writePush("constant", ord(char))
                self.vm_writer.writeCall("String.appendChar", 2)

            self.tokenizer.advance()

        elif token_type == "INT_CONST":  # Integer constant
            self.output_file.write("<integerConstant> " +
                                   str(self.tokenizer.intVal()) +
                                   " </integerConstant>\n")
            self.vm_writer.writePush("constant", self.tokenizer.intVal())
            self.tokenizer.advance()
        elif token_type == "KEYWORD" and token in ['true', 'false', 'null', 'this']:
            self.output_file.write("<keyword> " + self.tokenizer.keyWord() + " </keyword>\n")
            if token == 'true':
                self.vm_writer.writePush('constant', 1)
                self.vm_writer.writeArithmetic('neg')
            elif token in ['false', 'null']:
                self.vm_writer.writePush('constant', 0)
            else:  # this
                self.vm_writer.writePush('pointer', 0)
            self.tokenizer.advance()
        # varname, varname[expression], subroutineCall
        elif token_type == "IDENTIFIER":
            # Write the identifier first.
            self.output_file.write(
                "<identifier> " +
                self.tokenizer.identifier() +
                " </identifier>\n")
            identifier_name = self.tokenizer.identifier()
            self.tokenizer.advance()

            if self.tokenizer.currentToken == '[':  # array entry
                self.output_file.write("<symbol> [ </symbol>\n")
                self.tokenizer.advance()  # expression
                self.compileExpression()
                self._push_identifier_value(identifier_name)
                self.vm_writer.writeArithmetic('add')
                self.vm_writer.writePop('pointer', 1)
                self.vm_writer.writePush('that', 0)
                self.output_file.write("<symbol> ] </symbol>\n")
                self.tokenizer.advance()  # token after ']'
            elif self.tokenizer.currentToken == '(':  # subroutine call
                self.output_file.write("<symbol> ( </symbol>\n")
                self.vm_writer.writePush('pointer', 0)
                self.tokenizer.advance()  # expression list or ')'
                n_args = 1 + self.compileExpressionList()
                self.output_file.write("<symbol> ) </symbol>\n")
                self.tokenizer.advance()  # token after ')'
                self.vm_writer.writeCall(self.current_class_name + '.' + identifier_name, n_args)
            elif self.tokenizer.currentToken == '.':  # subroutine call
                self.output_file.write("<symbol> . </symbol>\n")
                self.tokenizer.advance()  # subroutine name
                subroutine_name = self.tokenizer.identifier()
                self.output_file.write(
                    "<identifier> " +
                    subroutine_name +
                    " </identifier>\n")
                self.tokenizer.advance()  # '('
                self.output_file.write("<symbol> ( </symbol>\n")

                kind, symbol_type, _ = self._resolve_symbol(identifier_name)
                if kind is not None:
                    self._push_identifier_value(identifier_name)
                    call_name = symbol_type + '.' + subroutine_name
                    n_args = 1
                else:
                    call_name = identifier_name + '.' + subroutine_name
                    n_args = 0

                self.tokenizer.advance()  # expression list or ')'
                n_args += self.compileExpressionList()
                self.output_file.write("<symbol> ) </symbol>\n")
                self.tokenizer.advance()  # token after ')'
                self.vm_writer.writeCall(call_name, n_args)
            else:
                self._push_identifier_value(identifier_name)
        elif token == '(':  # expression in parentheses 
            self.output_file.write("<symbol> ( </symbol>\n")
            self.tokenizer.advance()  # expression
            self.compileExpression()
            self.output_file.write("<symbol> ) </symbol>\n")
            self.tokenizer.advance()  # token after ')'
        elif token in ['-', '~']:  # unary operator and term
            unary_operator = token
            self.output_file.write(
                "<symbol> " +
                self._xml_symbol(unary_operator) +
                " </symbol>\n")
            self.tokenizer.advance()  # unary term
            self.compileTerm()
            self._write_unary_operator_vm(unary_operator)
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
            return 0
        self.output_file.write("<expressionList>\n")
        expression_count = 0
        self.compileExpression()  # Compile expression
        expression_count += 1
        while self.tokenizer.currentToken != ')':
            if self.tokenizer.currentToken == ',':
                self.output_file.write("<symbol> , </symbol>\n")
                self.tokenizer.advance()  # next expression
                self.compileExpression()  # Compile next expression
                expression_count += 1
            else:
                break
        self.output_file.write("</expressionList>\n")  # Empty expression list
        return expression_count
