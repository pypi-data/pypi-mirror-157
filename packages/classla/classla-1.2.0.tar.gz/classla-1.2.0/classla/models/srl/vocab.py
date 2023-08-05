from collections import Counter, OrderedDict

from classla.models.common.vocab import BaseVocab, BaseMultiVocab
from classla.models.common.vocab import VOCAB_PREFIX
from classla.models.lemma.vocab import Vocab
from classla.models.pos.vocab import WordVocab


class MultiVocab(BaseMultiVocab):
    def state_dict(self):
        """ Also save a vocab name to class name mapping in state dict. """
        state = OrderedDict()
        key2class = OrderedDict()
        for k, v in self._vocabs.items():
            state[k] = v.state_dict()
            key2class[k] = type(v).__name__
        state['_key2class'] = key2class
        return state

    @classmethod
    def load_state_dict(cls, state_dict):
        class_dict = {'WordVocab': WordVocab,
                      'Vocab': Vocab}
        new = cls()
        assert '_key2class' in state_dict, "Cannot find class name mapping in state dict!"
        key2class = state_dict.pop('_key2class')
        for k,v in state_dict.items():
            classname = key2class[k]
            new[k] = class_dict[classname].load_state_dict(v)
        return new

