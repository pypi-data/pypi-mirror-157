
from ._common import *

# ***************************************************************************************

# namespace
class _rules:

    word = lex2.Rule("WORD",        r"[a-zA-Z]+")
    # word = lex2.Rule("WORD",        r"[^。]+")
    punc = lex2.Rule("PUNCTUATION", r"[.,!]")

    # comment = lex2.predefs.Comment([
    #     lex2.predefs.SinglelineComment(r"\/\/"),
    #     lex2.predefs.MultilineComment(r"\/\*", r"\*\/"),
    # ])


    # sl_comment = lex2.predefs.SinglelineComment()
    # ml_comment = lex2.predefs.MultilineComment()

    comment = (lex2.predefs.Comments()
                           .add_singleline_comment(r"\/\/")
                           .add_multiline_comment(r"\/\*", r"\*\/")
                           .rule(returns=True))

    RULESET = [
        punc,
        word,
        comment,
    ]

import typing as t

class Test_MultispanComment (ut.TestCase):


  # --- ATTRIBUTES SETUP --- #

    def setUp(self) -> None:

        self.options = lex2.LexerOptions()
        # self.options.newline.returnTokens = True
        # self.options.returnRule[lex2.predefs.comment] = True

        # _rules.sl_comment.returnTokens = True
        # _rules.ml_comment.returnTokens = True

        return


  # --- UNIT TESTS --- #

    def test_MultispanComment_01(self):

        self.setUp()

        # Setup
        lexer = lex2.make_lexer()(
            ruleset=_rules.RULESET,
            options=self.options,
            # textstream=lex2.file.MakeTextstream(
            #     chunkSize=10,
            #     isBuffered=True
            # )
        )
        lexer.open(
            # DIR_OF(__file__) / "data/multispan_comment_01.txt",
            dir_of(__file__) / "data/multibyte_characters_01.txt",
            buffer_size=5,
            # encoding="UTF-8",
            # encoding="shift_jis",
            convert_line_endings=True
        )

        # Token matching tests
        token: lex2.Token

        token_list = t.List[lex2.Token]

        word_tokens: token_list  = []
        punctuation_tokens: token_list = []
        comment_tokens: token_list = []

        while(1):

            try: token = lexer.get_next_token()
            except lex2.excs.EOD:
                break

            if (token.is_rule(_rules.word)):
                word_tokens.append(token)

            elif (token.is_rule(_rules.punc)):
                punctuation_tokens.append(token)

            elif (token.is_rule(_rules.comment)):
                comment_tokens.append(token)

            info = [
                "ln: {}".format(token.pos.ln +1),
                "col: {}".format(token.pos.col+1),
                token.id,
                token.data,
            ]
            # print("{: <12} {: <20} {: <20} {: <20}".format(*info))

            # if (token.data == "libero"):
            #     print("")

        # self.assertEqual( len(word_tokens)        , 33 )
        # self.assertEqual( len(punctuation_tokens) ,  6 )
        # self.assertEqual( len(comment_tokens)     ,  2 )

        # self.assertEqual( word_tokens[-1].position.ln  , 50-1 )
        # self.assertEqual( word_tokens[-1].position.col , 14-1 )

        # self.assertEqual( len(comment_tokens[0].data) ,  2126 )
        # self.assertEqual( len(comment_tokens[1].data) ,  1218 )
