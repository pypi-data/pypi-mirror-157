"""
Processor for performing named entity tagging.
"""
import logging

from classla.models.common import doc
from classla.models.common.utils import unsort
from classla.models.srl.data import DataLoader
from classla.models.srl.trainer import Trainer
from classla.pipeline._constants import *
from classla.pipeline.processor import UDProcessor, register_processor

from classla.models.common.pretrain import Pretrain

logger = logging.getLogger('classla')


@register_processor(name=SRL)
class SRLProcessor(UDProcessor):

    # set of processor requirements this processor fulfills
    PROVIDES_DEFAULT = set([SRL])
    # set of processor requirements for this processor
    REQUIRES_DEFAULT = set([TOKENIZE, POS, LEMMA, DEPPARSE])

    def _set_up_model(self, config, use_gpu):
        # get pretrained word vectors
        self._pretrain = Pretrain(config['pretrain_path']) if 'pretrain_path' in config else None

        arg = {}

        # set up trainer
        self._trainer = Trainer(args=arg, pretrain=self.pretrain, model_file=config['model_path'], use_cuda=use_gpu)

    def predetermined_punctuations(self, seq):
        """ Determine if punctuation is already assigned by tokenizer. """
        return [pos if pos[0] is not None else False for pos in seq]

    def process(self, document):
        batch = DataLoader(document, self.config['batch_size'], self.config, self.pretrain, vocab=self.vocab, evaluation=True)
        preds = []
        for i, b in enumerate(batch):
            preds += self.trainer.predict(b)
        batch.doc.set([doc.SRL], [y for x in preds for y in x], to_token=True)
        return batch.doc
