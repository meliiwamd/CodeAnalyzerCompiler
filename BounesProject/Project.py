from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter

from Gen.JavaLexer import JavaLexer
from Gen.JavaParserLabeled import JavaParserLabeled
from Gen.JavaParserLabeledListener import JavaParserLabeledListener

import argparse
import os


class RefactoringListener(JavaParserLabeledListener):
    def __init__(self):
        self.Classes = []
        self.EachMethod = []
        self.EachField = []

        self.Public = 0
        self.Privates = 0

        self.InClass = False

    def enterClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        self.InClass = True

    def exitClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        Result = '-Class name: ' + ctx.IDENTIFIER().getText() + ',  ' + str(len(self.EachMethod)) + \
                 ' Methods: '

        for X in self.EachMethod:
            Result += X + ', '
        Result += str(len(self.EachField)) + ' Fields: '

        for X in self.EachField:
            Result += X + ', '
        Result += ' *' + 'Number of public fields: ' + str(self.Public) + \
                  ' *' + 'Number of private fields: ' + str(self.Privates)
        self.Classes.append(Result)

        self.EachMethod = []
        self.EachField = []
        self.Public = 0
        self.Privates = 0
        self.InClass = False

    def exitFieldDeclaration(self, ctx: JavaParserLabeled.FieldDeclarationContext):
        Parent = ctx.parentCtx.parentCtx
        if self.InClass is True:
            if Parent.modifier()[0].classOrInterfaceModifier().getText() == 'public':
                self.Public += 1
            elif Parent.modifier()[0].classOrInterfaceModifier().getText() == 'private':
                self.Privates += 1
            Result = ctx.variableDeclarators().variableDeclarator(0).variableDeclaratorId().IDENTIFIER().getText()

            self.EachField.append(Result)

    def enterMethodDeclaration(self, ctx: JavaParserLabeled.MethodDeclarationContext):
        if self.InClass is True:
            self.EachMethod.append(ctx.IDENTIFIER().getText())


def main(args):
    # Step 1: Load input source into stream
    stream = FileStream(args.file, encoding='utf8')

    # Step 2: Create an instance of AssignmentStLexer
    Lexer = JavaLexer(stream)

    # Step 3: Convert the input source into a list of tokens
    TokenStream = CommonTokenStream(Lexer)

    # Step 4: Create an instance of the AssignmentStParser
    parser = JavaParserLabeled(TokenStream)

    # Step 5: Create parse tree
    ParseTree = parser.compilationUnit()

    # Step 6: Create an instance of AssignmentStListener
    walker = ParseTreeWalker()
    Refactor = RefactoringListener()

    # Step 7: Refactor those classes
    walker.walk(t=ParseTree, listener=Refactor)
    for X in Refactor.Classes:
        print(X)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '-n', '--file',
        help='Input source', default=r'Test.java')
    args = argparser.parse_args()
    main(args)
