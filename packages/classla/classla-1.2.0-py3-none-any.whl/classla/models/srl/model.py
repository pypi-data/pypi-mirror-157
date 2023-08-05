import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_packed_sequence, pack_padded_sequence, PackedSequence

from classla.models.common.hlstm import HighwayLSTM
from classla.models.common.dropout import WordDropout


class SRLTagger(nn.Module):
    def __init__(self, args, vocab, emb_matrix=None, share_hid=False):
        super().__init__()

        self.vocab = vocab
        self.args = args
        self.share_hid = share_hid
        self.unsaved_modules = []

        def add_unsaved_module(name, module):
            self.unsaved_modules += [name]
            setattr(self, name, module)

        # input layers
        input_size = 0
        if self.args['word_emb_dim'] > 0:
            self.word_emb = nn.Embedding(len(vocab['word']), self.args['word_emb_dim'], padding_idx=0)
            input_size += self.args['word_emb_dim']
        if self.args['head_word_emb_dim'] > 0:
            self.head_word_emb = nn.Embedding(len(vocab['word']), self.args['head_word_emb_dim'], padding_idx=0)
            input_size += self.args['head_word_emb_dim']
        if self.args['lemma_emb_dim'] > 0:
            self.lemma_emb = nn.Embedding(len(vocab['lemma']), self.args['lemma_emb_dim'], padding_idx=0)
            input_size += self.args['lemma_emb_dim']
        if self.args['head_lemma_emb_dim'] > 0:
            self.head_lemma_emb = nn.Embedding(len(vocab['lemma']), self.args['head_lemma_emb_dim'], padding_idx=0)
            input_size += self.args['head_lemma_emb_dim']

        if self.args['xpos_emb_dim'] > 0:
            self.xpos_embedding = nn.Embedding(len(vocab['xpos']), self.args['xpos_emb_dim'], padding_idx=0)
            input_size += self.args['xpos_emb_dim']

        if self.args['head_xpos_emb_dim'] > 0:
            self.head_xpos_embedding = nn.Embedding(len(vocab['xpos']), self.args['head_xpos_emb_dim'], padding_idx=0)
            input_size += self.args['head_xpos_emb_dim']

        if self.args['deprel_emb_dim'] > 0:
            self.deprel_emb = nn.Embedding(len(vocab['deprel']), self.args['deprel_emb_dim'], padding_idx=0)
            input_size += self.args['deprel_emb_dim']

        if self.args['pretrain_file'] and self.args['word_emb_dim'] > 0:
            # pretrained embeddings, by default this won't be saved into model file
            add_unsaved_module('pretrained_emb', nn.Embedding.from_pretrained(torch.from_numpy(emb_matrix), freeze=True))
            self.trans_pretrained = nn.Linear(emb_matrix.shape[1], self.args['transformed_dim'], bias=False)
            input_size += self.args['transformed_dim']

        if self.args['pretrain_file'] and self.args['head_word_emb_dim'] > 0:
            # pretrained embeddings, by default this won't be saved into model file
            add_unsaved_module('head_pretrained_emb', nn.Embedding.from_pretrained(torch.from_numpy(emb_matrix), freeze=True))
            self.head_trans_pretrained = nn.Linear(emb_matrix.shape[1], self.args['transformed_dim'], bias=False)
            input_size += self.args['transformed_dim']

        # recurrent layers
        self.taggerlstm = HighwayLSTM(input_size, self.args['hidden_dim'], self.args['num_layers'], batch_first=True, bidirectional=True, dropout=self.args['dropout'], rec_dropout=self.args['rec_dropout'], highway_func=torch.tanh)
        self.drop_replacement = nn.Parameter(torch.randn(input_size) / np.sqrt(input_size))
        self.taggerlstm_h_init = nn.Parameter(torch.zeros(2 * self.args['num_layers'], 1, self.args['hidden_dim']))
        self.taggerlstm_c_init = nn.Parameter(torch.zeros(2 * self.args['num_layers'], 1, self.args['hidden_dim']))

        # classifiers
        self.srl_hid = nn.Linear(self.args['hidden_dim'] * 2, self.args['deep_biaff_hidden_dim'])
        self.srl_clf = nn.Linear(self.args['deep_biaff_hidden_dim'], len(vocab['srl']))
        self.srl_clf.weight.data.zero_()
        self.srl_clf.bias.data.zero_()

        # criterion
        self.crit = nn.CrossEntropyLoss(ignore_index=0)  # ignore padding

        self.drop = nn.Dropout(args['dropout'])
        self.worddrop = WordDropout(args['word_dropout'])

    def forward(self, words, words_mask, deprel, head_words, xpos, lemma, head_lemma, head_xpos, pretrained, head_pretrained, srl, orig_idx, sentlens, postprocessor=None):

        def pack(x):
            return pack_padded_sequence(x, sentlens, batch_first=True)

        inputs = []
        if self.args['word_emb_dim'] > 0:
            word_emb = self.word_emb(words)
            word_emb = pack(word_emb)
            inputs += [word_emb]

        if self.args['head_word_emb_dim'] > 0:
            head_word_emb = self.head_word_emb(head_words)
            head_word_emb = pack(head_word_emb)
            inputs += [head_word_emb]

        if self.args['lemma_emb_dim'] > 0:
            lemma_emb = self.lemma_emb(lemma)
            lemma_emb = pack(lemma_emb)
            inputs += [lemma_emb]

        if self.args['head_lemma_emb_dim'] > 0:
            head_lemma_emb = self.head_lemma_emb(head_lemma)
            head_lemma_emb = pack(head_lemma_emb)
            inputs += [head_lemma_emb]

        if self.args['xpos_emb_dim'] > 0:
            xpos_emb = self.xpos_embedding(xpos)
            xpos_emb = pack(xpos_emb)
            inputs += [xpos_emb]

        if self.args['head_xpos_emb_dim'] > 0:
            head_xpos_emb = self.head_xpos_embedding(head_xpos)
            head_xpos_emb = pack(head_xpos_emb)
            inputs += [head_xpos_emb]

        if self.args['deprel_emb_dim'] > 0:
            deprel_emb = self.deprel_emb(deprel)
            deprel_emb = pack(deprel_emb)
            inputs += [deprel_emb]

        if self.args['pretrain_file'] and self.args['word_emb_dim'] > 0:
            pretrained_emb = self.pretrained_emb(pretrained)
            pretrained_emb = self.trans_pretrained(pretrained_emb)
            pretrained_emb = pack(pretrained_emb)
            inputs += [pretrained_emb]

        if self.args['pretrain_file'] and self.args['head_word_emb_dim'] > 0:
            head_pretrained_emb = self.head_pretrained_emb(head_pretrained)
            head_pretrained_emb = self.head_trans_pretrained(head_pretrained_emb)
            head_pretrained_emb = pack(head_pretrained_emb)
            inputs += [head_pretrained_emb]

        def pad(x):
            if self.args['word_emb_dim'] > 0:
                return pad_packed_sequence(PackedSequence(x, word_emb.batch_sizes), batch_first=True)[0]
            else:
                return pad_packed_sequence(PackedSequence(x, head_word_emb.batch_sizes), batch_first=True)[0]

        lstm_inputs = torch.cat([x.data for x in inputs], 1)
        lstm_inputs = self.worddrop(lstm_inputs, self.drop_replacement)
        lstm_inputs = self.drop(lstm_inputs)
        lstm_inputs = PackedSequence(lstm_inputs, inputs[0].batch_sizes)

        lstm_outputs, _ = self.taggerlstm(lstm_inputs, sentlens, hx=(
        self.taggerlstm_h_init.expand(2 * self.args['num_layers'], words.size(0), self.args['hidden_dim']).contiguous(),
        self.taggerlstm_c_init.expand(2 * self.args['num_layers'], words.size(0), self.args['hidden_dim']).contiguous()))
        lstm_outputs = lstm_outputs.data

        srl_hid = F.relu(self.srl_hid(self.drop(lstm_outputs)))
        srl_pred = self.srl_clf(self.drop(srl_hid))

        preds = [pad(srl_pred).max(2)[1]]

        srl = pack(srl).data
        loss = self.crit(srl_pred.view(-1, srl_pred.size(-1)), srl.view(-1))

        return loss, preds
