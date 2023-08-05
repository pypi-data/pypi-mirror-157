"""
Basic testing of dependency parser
"""

import classla
import classla.models.parser as trainer
from classla.utils.conll import CoNLL

from tests_classla import *

with open('test_data/slovenian.raw') as f:
    SL_DOC = f.read()

with open('test_data/slovenian.parser') as f:
    SL_DOC_GOLD = f.read()


def test_parser():
    nlp = classla.Pipeline(
        **{'processors': 'tokenize,pos,lemma,depparse', 'dir': TEST_MODELS_DIR, 'lang': 'sl'})
    doc = nlp(SL_DOC)
    # with open('test_data/slovenian.parser', 'w') as f:
    #     f.write(doc.to_conll())
    assert SL_DOC_GOLD == doc.to_conll()

def test_tagger_trainer():
    trainer.main(args=['--save_dir', 'test_data/train/data', '--save_name', 'parser.pt', '--train_file', 'test_data/train/tagger_lemmatizer_parser_example.conll',
                       '--eval_file', 'test_data/train/tagger_lemmatizer_parser_example.conll', '--output_file', 'test_data/train/data/parser', '--gold_file', 'test_data/train/tagger_lemmatizer_parser_example.conll', '--shorthand', 'sl_ssj',
                       '--mode', 'train', '--pretrain_file', 'classla_test/models/sl/pretrain/standard.pt', '--max_steps', '100', '--wordvec_file', 'test_data/train/embed.sl-token.ft.sg.vec'])

