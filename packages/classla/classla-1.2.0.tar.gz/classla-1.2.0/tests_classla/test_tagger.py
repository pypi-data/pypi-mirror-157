"""
Basic testing of part of speech tagging
"""

import classla
import classla.models.tagger as trainer

from tests_classla import *

with open('test_data/slovenian.raw') as f:
    SL_DOC = f.read()

with open('test_data/slovenian.tagger') as f:
    SL_DOC_GOLD = f.read()


def test_part_of_speech():
    nlp = classla.Pipeline(**{'processors': 'tokenize,pos', 'dir': TEST_MODELS_DIR, 'lang': 'sl'})
    doc = nlp(SL_DOC)
    # with open('test_data/slovenian.tagger', 'w') as f:
    #     f.write('\n\n'.join([sent.tokens_string() for sent in doc.sentences]))
    assert SL_DOC_GOLD == '\n\n'.join([sent.tokens_string() for sent in doc.sentences])


def test_parser_trainer():
    trainer.main(args=['--save_dir', 'test_data/train/data', '--save_name', 'tagger.pt', '--train_file', 'test_data/train/tagger_lemmatizer_parser_example.conll',
                       '--eval_file', 'test_data/train/tagger_lemmatizer_parser_example.conll', '--output_file', 'test_data/train/data/tagger', '--gold_file', 'test_data/train/tagger_lemmatizer_parser_example.conll', '--shorthand', 'sl_ssj',
                       '--mode', 'train', '--pretrain_file', 'classla_test/models/sl/pretrain/standard.pt', '--max_steps', '100', '--inflectional_lexicon_path', 'test_data/train/sloleks_example.tbl'])
