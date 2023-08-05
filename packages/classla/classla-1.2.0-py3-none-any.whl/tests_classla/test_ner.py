"""
Basic testing of part of speech tagging
"""

import classla
import classla.models.ner_tagger as trainer

from tests_classla import *

with open('test_data/slovenian.raw') as f:
    SL_DOC = f.read()

with open('test_data/slovenian.ner') as f:
    SL_DOC_GOLD = f.read()


def test_ner():
    nlp = classla.Pipeline(**{'processors': 'tokenize,ner', 'dir': TEST_MODELS_DIR, 'lang': 'sl'})
    doc = nlp(SL_DOC)
    # with open('test_data/slovenian.ner', 'w') as f:
    #     f.write(doc.to_conll())
    assert SL_DOC_GOLD == doc.to_conll()


def test_ner_trainer():
    trainer.main(args=['--save_dir', 'test_data/train/data', '--save_name', 'ner.pt', '--train_file', 'test_data/train/ner_example.conll',
                       '--eval_file', 'test_data/train/ner_example.conll', '--shorthand', 'sl_ssj',
                       '--mode', 'train', '--max_steps', '500', '--scheme', 'bio', '--batch_size', '128',
                       '--wordvec_file', 'test_data/train/embed.sl.small'])
