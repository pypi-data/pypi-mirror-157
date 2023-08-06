
import sys, os
sys.path.append(os.path.join(sys.path[0],'..',))

import lex2 as _lex2

# Pretend this is a namespace
class _rules :

    opmComment = (_lex2.predefs.Comments()
                               .add_singleline_comment(r"//")
                               .rule())

    opmVoiceIdentifier = _lex2.Rule(
        "VOICE_IDENTIFIER",
        r"\@\:[0-9]{1,3}.*"
    )

    opmVoiceName = _lex2.Rule(
        "VOICE_NAME",
        r".*"
    )

    opmParamIdentifier = _lex2.Rule(
        "IDENTIFIER",
        # r"[A-Za-z][A-Za-z0-9_]+\:"
        r"(LFO|CH|[MC][12])\:"
    )

    opmNumber = _lex2.Rule(
        "NUMBER",
        r"[0-9]+"
    )

    r1 = [opmNumber, opmParamIdentifier, opmVoiceIdentifier, opmComment]
    r2 = [opmVoiceName]



def parse(fp: str):

    parser = _lex2.make_lexer()()

    parser.open(fp)

    parser.clear_rulesets()
    parser.push_ruleset(_rules.r1)

    # parser.GetHFlags().comment = _lexer2.HFlag.HANDLE_AND_RETURN
    # parser.GetHFlags().newline = _lexer2.HFlag.HANDLE_AND_RETURN

    i=0

    while(1):

        try: token = parser.get_next_token()
        except _lex2.excs.EOD:
            break

        # if (i==8989):
        #     print("ding")

        # if (token.IsRule(_lexer2.predefs.newline)):
        #     print("")
        # else:
        # print (token.data, end="")

        # if (token.is_rule(_rules.opmVoiceIdentifier)):
        #     # token = parser.GetNextToken()
        #     parser.push_ruleset(_rules.r2)

        # if (token.is_rule(_rules.opmVoiceName)):
        #     parser.pop_ruleset()


        info = [
            "ln: {}".format(token.pos.ln +1),
            "col: {}".format(token.pos.col+1),
            token.id,
            token.data,
        ]
        print("{: <12} {: <20} {: <20} {: <20}".format(*info))




        # if (token.data == ""):
        #     print("")

        # i+=1

    parser.close()
    return


def main() -> int:

    for i in range(100):

        print(i)
        # Parse(r"D:\Programming\Python3\liblexer2-python3\src\001_GRANDPNO2.opm")
        parse(r"D:\Programming\Python3\liblexer2-python3\src\distgit.opm")

    return 0




if __name__=="__main__":
    exit(main())
