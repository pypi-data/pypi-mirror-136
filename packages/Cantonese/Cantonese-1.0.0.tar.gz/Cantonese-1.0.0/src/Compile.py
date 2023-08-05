class Compile(object):
    def __init__(self, ast, target, path) -> None:
        self.ast = ast
        self.target = target
        self.path = path
        self.TO_JS_CODE = ""
        self.TO_C_CODE = ""
        self.TO_ASM_CODE = ""

        if self.target == "js":
            self.run_js(self.ast)

        if self.target == "c":
            self.run_c(self.ast)
    
        if self.target == "asm":
            self.run_asm(self.ast)

    def ret(self):
        if self.target == "js":
            return self.TO_JS_CODE, self.path[ : len(self.path) - len('cantonese')] + 'js'

        if self.target == "c":
            return self.TO_C_CODE, self.path[ : len(self.path) - len('cantonese')] + 'c'

        if self.target == "asm":
            return self.TO_ASM_CODE, self.path[ : len(self.path) - len('cantonese')] + 'S'

    # TODO
    def eval_expr(self, expr):
        return expr

    def run_asm(self, Nodes : list, label = '', path = '') -> None:
        for node in Nodes:
            pass

    def run_c(self, Nodes : list, label = '', path = '') -> None:
        for node in Nodes:
            if node[0] == "node_print":
                pass
    
    def run_js(self, Nodes : list, label = '', path = '', in_web = False) -> None:
        for node in Nodes:
            if node[0] == "node_print":
                if in_web:
                    self.TO_JS_CODE += "alert(" + self.eval_expr(node[1][1]) + ");\n"
                else:
                    self.TO_JS_CODE += "console.log(" + self.eval_expr(node[1][1]) + ");\n"
            
            if node[0] == "node_exit":
                self.TO_JS_CODE += "process.exit();\n"

            if node[0] == "node_let":
                self.TO_JS_CODE += node[1][1] + " = " + self.eval_expr(node[2][1]) + ";\n"

            if node[0] == "node_if":
                self.TO_JS_CODE += "if (" + self.eval_expr(node[1][1]) + ") {\n"
                self.run_js(node[2])
                self.TO_JS_CODE += "}"
            
            if node[0] == "node_elif":
                self.TO_JS_CODE += "else if (" + self.eval_expr(node[1][1]) + ") {\n"
                self.run_js(node[2])
                self.TO_JS_CODE += "}"

            if node[0] == "node_else":
                self.TO_JS_CODE += "else{"
                self.run_js(node[1])
                self.TO_JS_CODE += "}"

            if node[0] == "node_call":
                self.TO_JS_CODE += node[1][1] + ";\n"

            if node[0] == "node_fundef":
                if node[2] == 'None':
                    self.TO_JS_CODE += "function " + node[1][1] + "() {\n"
                    self.run_js(node[3])
                    self.TO_JS_CODE += "}\n"
                else:
                    self.TO_JS_CODE += "function " + node[1][1] + "(" + node[2][1] + ") {\n"
                    self.run_js(node[3])
                    self.TO_JS_CODE += "}\n"