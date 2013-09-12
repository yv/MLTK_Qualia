Learning Bag-of-Words features
==============================

The programs ``make_bigram_alph`` and ``bow_learn`` implement learning
of bag-of-words features for single words and pairs based on a corpus
in CQP format.

make_bigram_alph
~~~~~~~~~~~~~~~~

.. program:: make_bigram_alph

The program ``make_bigram_alph`` takes a CQP-format corpus
and determines the N most frequent unigrams and bigrams
(in this case, 1000 most frequent unigrams and 100 most frequent
bigrams). These unigram and bigram collocates will be used
as feature filter for the context-window-based collocate extraction.

.. option:: --lang language

   Specifies for which language the unigram and bigram frequencies
   should be determined (default: DE)

.. option:: --attr attribute name

   Specifies which CQP positional attribute should be used for the
   unigram and bigram features (default: word)

.. option:: --outdir output directory

   Specifies the location where the resulting files are to be stored.

bow_learn
~~~~~~~~~

.. program:: bow_learn

The program ``bow_learn`` uses the selection of unigrams and bigrams
from ``make_bigram_alph`` and extracts co-occurrence frequencies
between the target words, or the target word pairs, in one language,
and the feature unigrams and bigrams in a fixed window of these
occurrences, within a CQP corpus.

.. option:: --lang language

   Specifies for which language the unigram and bigram frequencies
   should be determined (default: DE)

.. option:: --attr attribute name

   Specifies which CQP positional attribute should be used for the
   unigram and bigram features (default: word)

.. option:: --outdir output directory

   Specifies the location where the resulting files are to be stored.

.. option:: --limit maximum

   Specifies that only the ``maximum`` most frequent feature words
   and feature bigrams should be used.

create_features
~~~~~~~~~~~~~~~

The program ``create_features`` takes a dataset of word pairs,
and performs the feature lookup, feature weighting, and additionally
the computation of GermaNet hyperonym features.
