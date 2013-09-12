MLTK_Qualia -- Supervised Learning of Semantic Relations
=================================================================

The tools in this package can be used to extract co-occurrence matrices
of various kinds from corpora and subsequently do learning experiments
on them.

Datasets are described in the .pynlp.yml configuration file and are used
throughout the tool suite.

The MLTK-Qualia package assists you in the following tasks:
- creation of feature matrices describing words and relations
- composing these feature matrices into JSON files that can be
  fed into MLTK's xvalidate_mlab script for cross-validating
  multilabel classifiers.

Basic Configuration
-------------------

MLTK-Qualia is configured through PyTrees ".pynlp.yml" configuration
file in your home directory, which must contain paths to the directories
that you want to use for existing or new feature matrices and alphabets.

For example, the file could look like the following:

```yaml
dist_sim:
  DE:
    pos_map:
      N: [NN, NP]
      V: [VVFIN, VVINF, VVIZU, VVPP]
      A: [ADJA, ADJD, ADV]
    word_alph_pattern: /gluster/nufa/yannick/TUEPP_vocab_%(pos_tag)s.txt
    pair_alph_pattern: /gluster/nufa2/yannick/cooccurrence_data/DE/vocabulary/pair%(pos_tag)s_alph.txt
    matrices_dir: /gluster/nufa/yannick/matrices
    component_alph_pattern: /gluster/nufa2/yannick/cooccurrence_data/DE/matrices/%(pos_tag)s/%(matrix_name)s.alph
    component_mat_pattern: /gluster/nufa2/yannick/cooccurrence_data/DE/matrices/%(pos_tag)s/%(matrix_name)s.dat
    default_corpora: [NEWS_DMOZ]
    datasets:
      qualia:
        path: /gluster/common/annotation/LexRelationen/Noun-Associations_gold_forCluto.csv
        pattern: "W_W\tL"
        postags: [N,V]
```

Datasets are declared with their path, a pattern to parse the respective file (where ``W'' stands for
one word from the word pair, and ``L'' stands for the gold-standard label(s)).

Creating Feature Matrices
-------------------------

Feature matrices are created from collocations in a large corpus.

The first step is to extract the needed vocabulary from the datasets with which
you want to do classification:

    compile_alphabets --lang DE

(You can also create the vocabulary yourself as a one-word-per-line file, prefixed with the number
of entries in the file).

After having gotten hold of a suitably large corpus, you can proceed to
creating feature matrices for the single words in your datasets as well as
for the word pairs (of differen POS categories) that occur there.

First, create a list of the most frequent unigrams and bigrams in your corpus
by using

    make_bigram_alph --lang DE

and then compile feature vectors for these unigrams/bigrams with

    bow_learn --lang DE

which you then need to move to the locations that you have given in your .pytree.yml.

Finally, you can create a JSON file for your dataset with all the requisite features:

    create_features -m pair_bow_NEWS_DMOZ -G hyper --lang DE qualia