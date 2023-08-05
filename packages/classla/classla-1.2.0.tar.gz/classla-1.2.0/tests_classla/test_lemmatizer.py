"""
Basic testing of lemmatization
"""

import classla
import classla.models.lemmatizer as trainer

from tests_classla import *

with open('test_data/slovenian.raw') as f:
    SL_DOC = f.read()

with open('test_data/slovenian.lemmatizer') as f:
    SL_DOC_LEMMATIZER_MODEL_GOLD = f.read()


SL_DOC_SMALL = "France Prešeren se je rodil v vrbi."

SL_DOC_IDENTITY_GOLD = """
<Token id=1;words=[<Word id=1;text=France;lemma=France>]>
<Token id=2;words=[<Word id=2;text=Prešeren;lemma=Prešeren>]>
<Token id=3;words=[<Word id=3;text=se;lemma=se>]>
<Token id=4;words=[<Word id=4;text=je;lemma=je>]>
<Token id=5;words=[<Word id=5;text=rodil;lemma=rodil>]>
<Token id=6;words=[<Word id=6;text=v;lemma=v>]>
<Token id=7;words=[<Word id=7;text=vrbi;lemma=vrbi>]>
<Token id=8;words=[<Word id=8;text=.;lemma=.>]>
""".strip()


def test_identity_lemmatizer():
    nlp = classla.Pipeline(**{'processors': 'tokenize,lemma', 'dir': TEST_MODELS_DIR, 'lang': 'sl',
                                  'lemma_use_identity': True})
    doc = nlp(SL_DOC_SMALL)
    assert SL_DOC_IDENTITY_GOLD == '\n\n'.join([sent.tokens_string() for sent in doc.sentences])


def test_full_lemmatizer():
    nlp = classla.Pipeline(**{'processors': 'tokenize,pos,lemma', 'dir': TEST_MODELS_DIR, 'lang': 'sl'})
    doc = nlp(SL_DOC)
    # with open('test_data/slovenian.lemmatizer', 'w') as f:
    #     f.write('\n\n'.join([sent.tokens_string() for sent in doc.sentences]))
    assert SL_DOC_LEMMATIZER_MODEL_GOLD == '\n\n'.join([sent.tokens_string() for sent in doc.sentences])


def test_lemmatizer_sloleks_trainer():
    trainer.main(args=['--model_dir', 'test_data/train/data', '--model_file', 'ssj500k+Sloleks.pt', '--train_file', 'test_data/train/tagger_lemmatizer_parser_example.conll',
                       '--eval_file', 'test_data/train/tagger_lemmatizer_parser_example.conll', '--output_file', 'test_data/train/data/lemmatizer', '--gold_file', 'test_data/train/tagger_lemmatizer_parser_example.conll',
                       '--mode', 'train', '--num_epoch', '1', '--decay_epoch', '20',  '--pos', '--pos_model_path', 'classla_test/models/sl/pos/standard.pt'])

def test_lemmatizer_trainer():
    trainer.main(args=['--model_dir', 'test_data/train/data', '--model_file', 'ssj500k+Sloleks.pt', '--train_file', 'test_data/train/tagger_lemmatizer_parser_example.conll',
                       '--eval_file', 'test_data/train/tagger_lemmatizer_parser_example.conll', '--output_file', 'test_data/train/data/lemmatizer', '--gold_file', 'test_data/train/tagger_lemmatizer_parser_example.conll',
                       '--mode', 'train', '--num_epoch', '1', '--decay_epoch', '20',  '--pos', '--external_dict', 'test_data/train/external_dict_example.tsv'])
