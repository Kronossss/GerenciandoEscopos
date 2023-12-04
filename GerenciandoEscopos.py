# Importa os módulos necessários
import logging
import re

# Classe para representar símbolos na tabela de símbolos
class Symbolos:
    def __init__(self, lexeme, tipo, value=None):
        self.lexeme = lexeme.strip()
        self.tipo = tipo
        self.value = value

# Classe para representar a tabela de símbolos
class TabelaSimbolos:
    def __init__(self):
        self.Simbolos = {}
    # Adiciona um símbolo à tabela de símbolos
    def add_Symbolos(self, Symbolos):
        self.Simbolos[Symbolos.lexeme] = Symbolos

# Classe que implementa o analisador semântico
class AnalisadorSemanticoo:
    def __init__(self):
        # Inicializa a tabela de símbolos com uma tabela vazia
        self.tabelas_simbolos = [TabelaSimbolos()]
        self.tipos_validos = {'NUMERO': (int, float), 'CADEIA': str}
    # Executa uma lista de instruções
    def execute_instructions(self, instructions):
        for instruction in instructions:
            self.execute_instruction(instruction)
    # Executa uma instrução
    def execute_instruction(self, instruction):
        # Se a instrução é uma lista, executa cada sub-instrução
        if isinstance(instruction, list):
            for sub_instruction in instruction:
                self.execute_instruction(sub_instruction)
        else:
            instrucao = instruction["instrucao"]
            # Verifica o tipo de instrução e executa a lógica correspondente
            if instrucao == "BLOCO":
                nome_bloco = instruction.get("nome_bloco", "Sem Nome")
                print(f"Entrando no bloco: {nome_bloco}")
                self.tabelas_simbolos.append(TabelaSimbolos())
            elif instrucao == "FIM":
                self.tabelas_simbolos.pop()
                nome_bloco = instruction.get("nome_bloco", "Sem Nome")
                print(f"Saindo do bloco: {nome_bloco}")
            elif instrucao == "PRINT":
                self.processo_print(instruction["lexema"].strip())
            elif instrucao in ["ATRIBUICAO", "DECLARACAO"]:
                lexema = instruction['lexema']
                lexema = re.sub(r'^(NUMERO|CADEIA)\s*', '', lexema).strip()
                instruction['lexema'] = lexema
                self.add_variavel(instruction)
            else:
                print(f"[ERRO: Instrução inválida '{instrucao}")

    # Adiciona uma variável à tabela de símbolos
    def add_variavel(self, instruction):
        lexeme = instruction["lexema"].strip()
        tipo_declarado = instruction.get("tipo_declarado")
        value = self.valor_proceso(instruction.get("valor"))

        scopo_atual = self.tabelas_simbolos[-1]
        # Se a variável já existe, atualiza seu valor; caso contrário, adiciona à tabela de símbolos
        if lexeme in scopo_atual.Simbolos:
            self.atualizar_valor_variavel(lexeme, value)
        else:
            tipo_to_use = tipo_declarado or self.infer_tipo(value)
            new_Symbolos = Symbolos(lexeme, tipo_to_use, value)
            scopo_atual.add_Symbolos(new_Symbolos)

    # Atualiza o valor de uma variável na tabela de símbolos
    def atualizar_valor_variavel(self, lexeme, new_value):
        for table in reversed(self.tabelas_simbolos):
            if lexeme in table.Simbolos:
                # Verifica se a atribuição é válida em relação ao tipo da variável
                if isinstance(new_value, self.tipos_validos[table.Simbolos[lexeme].tipo]):
                    table.Simbolos[lexeme].value = new_value
                    return
                else:
                    logging.error(f"Error de tipo: Atribuição inválida para variável `{lexeme}`")
                    return

        logging.error(f"Error: Variável `{lexeme}` não declarada.")

    # Processa o valor da variável
    def valor_proceso(self, value):
        if value is None:
            return None
        # Converte valores de string para int, float ou mantém como string
        return value.strip('"') if value.startswith('"') and value.endswith('"') else \
               int(value) if value.lstrip('-+').isdigit() else \
               float(value) if '.' in value or value.lstrip('-+').replace('.', '', 1).isdigit() else \
               self.pega_valor_variavel(value.strip())

    # Obtém o valor de uma variável na tabela de símbolos
    def pega_valor_variavel(self, lexeme):
        for table in reversed(self.tabelas_simbolos):
            if lexeme in table.Simbolos and table.Simbolos[lexeme].value is not None:
                return table.Simbolos[lexeme].value
        return None

    # Inferir o tipo da variável com base no valor
    def infer_tipo(self, value):
        for tipo_name, tipos_validos in self.tipos_validos.items():
            if isinstance(value, tipos_validos):
                return tipo_name
        return None

    # Processa a instrução PRINT
    def processo_print(self, lexeme):
        variavel_tipo = self.get_variavel_tipo(lexeme)
        variavel_value = self.pega_valor_variavel(lexeme)

        if variavel_tipo is not None:
            print(f"PRINT <{lexeme}>:\n   Tipo: {variavel_tipo}\n   Valor: {variavel_value}")
        else:
            logging.error(f"Error: Variável `{lexeme}` não declarada.")

    # Retorna o tipo de uma variável
    def get_variavel_tipo(self, lexeme):
        for table in reversed(self.tabelas_simbolos):
            if lexeme in table.Simbolos:
                return table.Simbolos[lexeme].tipo
        return None

# Classe para o processador semântico
class ProcesadorSemantico:
     # Processa o código de um arquivo
    def processo_code_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        return self.processo_code(content)

    # Processa o código fornecido
    def processo_code(self, code):
        instructions = []
        for line in code.splitlines():
            if line.strip():
                instruction = self.linha_proceso(line)
                if instruction:
                    instructions.append(instruction)
        return instructions

    # Processa uma linha de código
    def linha_proceso(self, line):
        parts = line.split(maxsplit=1)
        instruction_tipo = parts[0]
        # Identifica blocos, marcações de fim, atribuições, declarações e impressões
        if instruction_tipo == "BLOCO" or instruction_tipo == "FIM":
            return {"instrucao": instruction_tipo, "nome_bloco": parts[1].strip()}

        if "=" in line:
            return self.proceso_atribuicao(line)

        if instruction_tipo in {"NUMERO", "CADEIA"}:
            return self.proceso_declaracao(line)

        if instruction_tipo == "PRINT":
            return {"instrucao": instruction_tipo, "lexema": parts[1].strip()}

    # Processa uma instrução de atribuição
    def proceso_atribuicao(self, line):
        declarations = line.split(",")
        instructions = []

        for declaration in declarations:
            lexeme, *rest = [part.strip() for part in declaration.split("=")]
            value = '='.join(rest) if rest else None
            instructions.append({"instrucao": "ATRIBUICAO", "lexema": lexeme, "valor": value})

        return instructions

    # Processa uma instrução de declaração
    def proceso_declaracao(self, line):
        parts = line.split(maxsplit=1)
        tipo_declarado = parts[0]
        declarations = parts[1].split(",")

        instructions = []
        for declaration in declarations:
            lexeme, *rest = [part.strip() for part in declaration.split("=")]
            value = '='.join(rest) if rest else None
            instructions.append({"instrucao": "DECLARACAO", "lexema": lexeme, "tipo_declarado": tipo_declarado, "valor": value})

        return instructions if len(instructions) > 1 else instructions[0]

# Função principal
def main():
    Procesador = ProcesadorSemantico()
    analisador = AnalisadorSemanticoo()
     # Define o arquivo de código
    code_file = "arquivo.txt"
    instructions = Procesador.processo_code_from_file(code_file)
    # Executa as instruções
    analisador.execute_instructions(instructions)

# Execução do programa
if __name__ == "__main__":
    main()
