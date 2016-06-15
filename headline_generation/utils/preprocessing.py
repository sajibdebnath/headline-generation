"""A module for formatting article/headline pairs for a Keras model. 

This module contains functions for running article/headline pairs through an
embedding to vectorize them. 
"""

import numpy as np

def gen_embedding_weights(word_idx_dct, word_vector_dct): 
    """Generate the initial embedding weights.

    Args: 
    ----
        word_idx_dct: dict
        word_vector_dct: dict

    Return: 
    ------
        embedding_weights: 2d np.ndarry
    """

    n_words = len(word_idx_dct)
    # A little gross, but avoids loading all keys/values into memory. We need 
    # to access one of the lists and see how many dimensions each embedding has.
    n_dim = next(len(word_vector_dct[word]) for word in word_vector_dct)

    embedding_weights = np.zeros((n_words, n_dim))

    for wrd, idx in word_idx_dct.items():
        embedding_weights[idx, :] = word_vector_dct[wrd]

    return embedding_weights

def _vec_txt(words, word_idx_dct): 
    """Translate the inputted words into numbers using the `word_idx_dct`. 

    This is a helper function to `vectorize_txts`. 

    Args: 
    ----
        words: list of strings
        word_idx_dct: dct

    Return: 
    ------
        vectorized_words_lst: list of ints
            Returns `None` if none of the inputted words are in the `word_idx_dct` 
    """

    vectorized_words_lst = []
    for word in words: 
        if word in word_idx_dct: 
            vectorized_words_lst.append(word_idx_dct[word])

    return vectorized_words_lst

def vectorize_texts(bodies, headlines, word_idx_dct): 
    """Translate each of the inputted text's words into numbers. 

    This calls the helper function `_vec_txt`. 

    Args: 
    ----
        bodies: list of lists of strings
        headlines: list of lists of strings
        word_idx_dct: dct

    Return: 
    ------
        vec_bodies_arr: 1d np.ndarray
        vec_headlines_arr: 1d np.ndarray
    """

    vec_bodies = []
    vec_headlines = []
    for body, headline in zip(bodies, headlines):  
        vec_body = _vec_txt(body, word_idx_dct)
        vec_headline = _vec_txt(headline, word_idx_dct)
        if vec_body and vec_headline: 
            vec_bodies.append(vec_body)
            vec_headlines.append(vec_headline)
    
    vec_bodies_arr = np.array(vec_bodies)
    vec_headlines_arr = np.array(vec_headlines)

    return vec_bodies_arr, vec_headlines_arr

def format_inputs(bodies_arr, headlines_arr, vocab_size, maxlen=50, step=1): 
    """Format the body and headline arrays into the X,y matrices fed into the LSTM.

    Take the article bodies and headlines concatenated (e.g. a continuous array
    of words starting with the first word in the body and ending with the last
    word in the headline), and create (X, y) pairs to build up X and y matrices
    to feed into the LSTM. 
    
    Building these (X, y) pairs includes: 
        - Dropping any body/article pairs where the body is less than the `maxlen` 
          plus the length of the heading (and accounting for step size); this allows 
          for the number of samples per body/article pair to be equal to the number  
          of words in the heading 
        - Taking the first `maxlen` + headline length words of the body and stepping
          through those by the `step` to obtain X's, and stepping through the 
          words of the heading by `step` to obtain the corresponding y
    
    Args: 
    ----
        bodies_arr: 1d np.ndarray of lists of strings
        headlines_arr: 1d np.ndarray of lists of strings
        vocab_size: int
        maxlen (optional): int
            How long to make the X sequences used for predicting. 
        step (optional): int
            How many words to skip over when passing through the concatenated
            article + body and generating (X,y) pairs 

    Return: 
    ------
        X_s: 2d np.ndarray
        y_s: 2d np.ndarray
    """

    X_s = np.zeros((0, maxlen)).astype('int32')
    ys = np.zeros((0, 1)).astype('int32')

    master_arr = []
    for body, hline in zip(bodies_arr, headlines_arr): 

        len_body, len_hline = len(body), len(hline)
        max_hline_len = (len_body - maxlen) // step

        if len_hline <= max_hline_len: 
            clipped_body = body[:(maxlen + len_hline)]
            clipped_body.extend(hline)
            master_arr.append((clipped_body, len_hline))


    for body_n_hline, len_hline in master_arr:
        for idx in range(0, len_hline, step): 
            X_start = idx
            X_end = X_start + maxlen
            X = np.array(body_n_hline[X_start:X_end])[np.newaxis]

            y_start = idx + maxlen + len_hline
            y_end = y_start + 1
            y = np.array(body_n_hline[y_start:y_end])[np.newaxis]

            X_s = np.concatenate([X_s, X])
            ys = np.concatenate([ys, y])

    # This is much faster than inserting in the above loop.
    y_s = np.zeros((X_s.shape[0], vocab_size)).astype('int32')
    idx = np.arange(X_s.shape[0])
    for idx, y in enumerate(ys):
        y_s[idx, y] = 1

    return X_s, y_s

