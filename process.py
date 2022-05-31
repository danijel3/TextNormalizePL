from token_methods import tokenize, group_classify, verbalize
from token_types import grp_tok2str, grp_verb2str, TokenGroupClass

lines = []
with open('sample.txt') as f:
    for l in f:
        tok = tokenize(l.strip())
        grp = group_classify(tok)
        verbalize(grp)
        lines.append(grp)

with open('output.txt', 'w') as f:
    for l in lines:
        f.write(grp_tok2str(l) + '\n')
        f.write(grp_verb2str(l) + '\n')
