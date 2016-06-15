import pytest
from gensim.models.word2vec import Word2Vec
from headline_generation.utils.mappings import create_mapping_dicts

class TestMappings: 

    def setup_class(cls): 
        sentences = [['body1', 'words', 'and', 'stuff', 'words', '?'], 
                     ['body2', 'more', 'words', 'parrots', 'are', 'talkative',
                      'parrots', '?']]
        cls.bodies = [['body1', 'words', 'and', 'stuff'], 
                  ['body2', 'more', 'words', 'parrots', 'are' , 'talkative']]
        cls.headlines = [['words', '?'], ['parrots', '?']]

        bodies_set = set(word for body in cls.bodies for word in body)
        headlines_set = set(word for headline in cls.headlines for word in headline)

        cls.vocab = bodies_set.union(headlines_set)
        cls.word2vec_model = Word2Vec(sentences, min_count=1, size=len(cls.vocab))
        cls.word_idx_dct, cls.idx_word_dct, cls.word_vector_dct = \
                create_mapping_dicts(cls.word2vec_model)
    
    def teardown_class(cls): 
        del cls.vocab
        del cls.word2vec_model
        del cls.word_idx_dct
        del cls.idx_word_dct 
        del cls.word_vector_dct
        del cls.bodies
        del cls.headlines

    def test_create_mapping_dicts(self): 

        assert (len(self.word_idx_dct) == len(self.vocab))
        assert (len(self.idx_word_dct) == len(self.vocab))
        assert (len(self.word_vector_dct) == len(self.vocab))

        assert (set(self.word_idx_dct.keys()) == self.vocab)
        assert (set(self.idx_word_dct.values()) == self.vocab)
        assert (set(self.word_vector_dct.keys()) == self.vocab)

    def test_create_mapping_dicts_w_filter(self):
        
        bodies = [['body', 'words', 'and', 'stuf'], 
                  ['body2', 'mo', 'words', 'parrot', 'are' , 'talkative']]
        headlines = [['words', '!!'], ['par', '?']]
        bodies_set = set(word for body in bodies for word in body)
        headlines_set = set(word for headline in headlines for word in headline)

        test_vocab = bodies_set.union(headlines_set)

        word_idx_dct, idx_word_dct, word_vector_dct = \
                create_mapping_dicts(self.word2vec_model, filter_corpus=True, 
                                     bodies=bodies, headlines=headlines)

        assert (len(word_idx_dct) <= len(test_vocab))
        assert (len(idx_word_dct) <= len(test_vocab))
        assert (len(word_vector_dct) <= len(test_vocab))

