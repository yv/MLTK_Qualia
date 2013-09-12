Getting Started
===============

MLTK_Qualia provides feature extraction for relations between **words**, which belong to a certain **part of speech category**
and a certain **language**. In the most common case, these features either come from **co-occurrence matrices**, which can be
transformed or weighted in several ways, or using the **hypernymy graph** of a wordnet such as GermaNet.

The datasets that are to be classified are configured in the ``.pynlp.yml`` file in one's home directory, under the key ``dist_sim``.

Here is an example for a YAML configuration with various file name patterns and directories::

  dist_sim:
    DE:
      pos_map:
        N: [NN, NP]
        V: [VVFIN, VVINF, VVIZU, VVPP]
        A: [ADJA, ADJD, ADV]
    deps_blacklist: [NEB, OBJI, S, REL]
    word_alph_pattern: /gluster/nufa/yannick/TUEPP_vocab_%(pos_tag)s.txt
    pair_alph_pattern: /gluster/nufa/yannick/pair_%(pos_tag)s.txt
    matrices_dir: /gluster/nufa/yannick/matrices
    component_alph_pattern: /gluster/nufa/yannick/matrices/%(pos_tag)s/%(matrix_name)s.alph
    component_mat_pattern: /gluster/nufa/yannick/matrices/%(pos_tag)s/%(matrix_name)s.dat
    default_matrices:
      N: [NEWS_DMOZ_1000_malt_ATTR,NEWS_DMOZ_1000_malt_OBJA]
    default_corpora: [NEWS_DMOZ]
    datasets:
      qualia:
        path: /gluster/common/annotation/LexRelationen/Noun-Associations_gold_forCluto.csv
        pattern: "W_W\tL"
        postags: [N,V]
      rkomp:
        path: /gluster/common/annotation/LexRelationen/rektionskomposita.txt
        pattern: "W_W\tL"
        postags: [N,V]

The entries of the ``dist_sim.DE.pos_map`` key specify which coarse-grained
part-of-speech entries (e.g., N or V) correspond to which part-of-speech tag in the tagset
used in the corpora (e.g., STTS or PTB POS tags).

The entries in ``word_alph_pattern`` and ``pair_alph_pattern`` point to word numberings
for target words and target word pairs. In this way, a target word is mapped to a number
which is the same across prediction tasks and across feature matrices.

The entries  ``component_mat_pattern`` and ``component_alph_pattern`` point to single feature
matrices, which correspond to one kind of collocates for the words of a particular part-of-speech.

compile_alphabets
~~~~~~~~~~~~~~~~~

.. program:: compile_alphabets


The ``compile_alphabets`` program reads in all datasets and creates alphabets.

.. option:: --lang language

   Specifies for which language the feature alphabets should be re-created. If no language
   is specified, the program will re-create the alphabets for all languages.

.. option:: --suffix suffix

   Specifies that the file names for the alphabets that are created should be appended with
   a specific suffix (e.g., to avoid overwriting existing files).


