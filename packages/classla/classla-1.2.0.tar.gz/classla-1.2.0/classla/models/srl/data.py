import random
import logging
import torch

from classla.models.common.data import get_long_tensor, sort_all
from classla.models.common.vocab import PAD_ID
from classla.models.lemma.vocab import Vocab
from classla.models.pos.vocab import WordVocab
from classla.models.srl.vocab import MultiVocab
from classla.models.common.doc import *

logger = logging.getLogger('classla')

class DataLoader:
    def __init__(self, doc, batch_size, args, pretrain=None, vocab=None, evaluation=False, preprocess_tags=True):
        self.batch_size = batch_size
        self.args = args
        self.eval = evaluation
        self.shuffled = not self.eval
        self.doc = doc
        self.preprocess_tags = preprocess_tags

        data = self.load_doc(self.doc)
        self.srls = [[w[5] for w in sent] for sent in data]

        # handle vocab
        self.pretrain = pretrain
        if vocab is None:
            self.vocab = self.init_vocab(data)
        else:
            self.vocab = vocab

        # filter and sample data
        if args.get('sample_train', 1.0) < 1.0 and not self.eval:
            keep = int(args['sample_train'] * len(data))
            data = random.sample(data, keep)
            logger.debug("Subsample training set with rate {:g}".format(args['sample_train']))

        # data = self.preprocess(data, self.vocab, args)
        data = self.preprocess(data, self.vocab, self.pretrain, args)
        # shuffle for training
        if self.shuffled:
            random.shuffle(data)
        self.num_examples = len(data)

        # chunk into batches
        self.data = self.chunk_batches(data)
        logger.debug("{} batches created.".format(len(self.data)))

    def init_vocab(self, data):
        assert self.eval == False  # for eval vocab must exist
        wordvocab = WordVocab(data, self.args['shorthand'], cutoff=5, lower=True)
        pos_data = [w[1] for s in data for w in s]
        xposvocab = Vocab(pos_data, self.args['lang'])
        lemmavocab = WordVocab(data, self.args['shorthand'], cutoff=5, idx=2, lower=True)
        deprelvocab = WordVocab(data, self.args['shorthand'], idx=4)
        srlvocab = WordVocab(data, self.args['shorthand'], idx=5)
        vocab = MultiVocab({'word': wordvocab,
                            'xpos': xposvocab,
                            'lemma': lemmavocab,
                            'deprel': deprelvocab,
                            'srl': srlvocab
                            })
        return vocab

    def preprocess(self, data, vocab, pretrain, args):
        processed = []
        for sent in data:
            processed_sent = [vocab['word'].map([w[0] for w in sent])]
            processed_sent += [vocab['deprel'].map([w[4] for w in sent])]
            # Head word
            processed_sent += [vocab['word'].map([sent[w[3]-1][0] if w[3] > 0 else '<ROOT>' for w in sent])]
            processed_sent += [vocab['xpos'].map([w[1] for w in sent])]
            processed_sent += [vocab['lemma'].map([w[2] for w in sent])]
            # head lemma
            processed_sent += [vocab['lemma'].map([sent[w[3]-1][2] if w[3] > 0 else '<ROOT>' for w in sent])]
            # head xpos
            processed_sent += [vocab['xpos'].map([sent[w[3]-1][1] if w[3] > 0 else '<UNK>' for w in sent])]

            # pretrain word encodings
            processed_sent += [pretrain.vocab.map([w[0] for w in sent])]
            processed_sent += [pretrain.vocab.map([sent[w[3]-1][0] if w[3] > 0 else '<ROOT>' for w in sent])]

            processed_sent += [vocab['srl'].map([w[5] for w in sent])]

            processed.append(processed_sent)
        return processed

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        """ Get a batch with index. """
        if not isinstance(key, int):
            raise TypeError
        if key < 0 or key >= len(self.data):
            raise IndexError
        batch = self.data[key]
        batch_size = len(batch)
        batch = list(zip(*batch))
        assert len(batch) == 10 # words: List[List[int]], chars: List[List[List[int]]], tags: List[List[int]]

        # sort sentences by lens for easy RNN operations
        lens = [len(x) for x in batch[0]]
        batch, orig_idx = sort_all(batch, lens)

        # convert to tensors
        words = batch[0]
        words = get_long_tensor(words, batch_size)
        words_mask = torch.eq(words, PAD_ID)

        deprel = get_long_tensor(batch[1], batch_size)

        head_words = get_long_tensor(batch[2], batch_size)

        xpos = get_long_tensor(batch[3], batch_size)
        lemma = get_long_tensor(batch[4], batch_size)
        head_lemma = get_long_tensor(batch[5], batch_size)
        sentlens = [len(x) for x in batch[0]]
        head_xpos = get_long_tensor(batch[6], batch_size)

        pretrained = get_long_tensor(batch[7], batch_size)
        head_pretrained = get_long_tensor(batch[8], batch_size)

        srl = get_long_tensor(batch[9], batch_size)

        return words, words_mask, deprel, head_words, xpos, lemma, head_lemma, head_xpos, pretrained, head_pretrained, srl, orig_idx, sentlens

    def __iter__(self):
        for i in range(self.__len__()):
            yield self.__getitem__(i)

    def load_doc(self, doc):
        # data = doc.get([TEXT, NER], as_sentences=True, from_token=True)
        data = doc.get([TEXT, XPOS, LEMMA, HEAD, DEPREL, SRL], as_sentences=True)
        data = self.resolve_none(data)
        return data

    def resolve_none(self, data):
        # replace None to '_'
        for sent_idx in range(len(data)):
            for tok_idx in range(len(data[sent_idx])):
                for feat_idx in range(len(data[sent_idx][tok_idx])):
                    if data[sent_idx][tok_idx][feat_idx] is None:
                        data[sent_idx][tok_idx][feat_idx] = '_'
        return data

    def reshuffle(self):
        data = [y for x in self.data for y in x]
        random.shuffle(data)
        self.data = self.chunk_batches(data)

    def chunk_batches(self, data):
        data = [data[i:i+self.batch_size] for i in range(0, len(data), self.batch_size)]
        return data

