#-*-encoding:utf-8
import sys
from CWB.CL import Corpus
from alphabet import CPPUniAlphabet
from dist_sim import sparsmat
from gzip import GzipFile
import optparse
import simplejson as json
import codecs

from mltk_qualia.task_config import get_word_alphs, get_pair_alphs
from context_extractor import ContextExtractor

def read_input_pairs(f):
    alph=CPPUniAlphabet()
    alph_w=CPPUniAlphabet()
    word_pairs=[]
    for l in f:
        line=l.strip().split()
        word1=line[3]
        word2=line[0]
        alph[u'%s_%s'%(word1,word2)]
        alph_w[word1]
        alph_w[word2]
        word_pairs.append((word1,word2))
    alph.growing=False #stick to known word pairs
    return alph, alph_w, word_pairs

def print_counts(pair_alph, rel_alph, counts): #re-map indices to strings
    for pair_idx, rel_idx, count in counts:
        if count>=5:
            print "%s\t%s\t%s"%(pair_alph.get_sym(pair_idx),
                            rel_alph.get_sym(rel_idx),
                            count)

LEFT_CTX=4
RIGHT_CTX=4

def gather_word_vectors(words, attr, attr_find, attr_sent,
                        unigram_alph,bigram_alph,unigram_feat_alph,
                        map_w=None, limit=-1):
    extractor=ContextExtractor(attr,unigram_alph,bigram_alph,attr_sent,alph_limit=limit)
    left_matrix=sparsmat.VecI2()
    for i,w_u in enumerate(words):
        if isinstance(w_u,unicode):
            w=w_u.encode('ISO-8859-15','replace')
        else:
            w=w_u
        print >>sys.stderr,w
        try:
            if map_w is None or w not in map_w:
                lst=attr_find.find(w)
            else:
                lst=attr_find.find_list(map_w[w])
            extractor.collect_word_context(lst,i,unigram_feat_alph,left_matrix)
        except KeyError,e:
            print >>sys.stderr, "Cannot find %s: %s"%(w, e)
    return left_matrix.to_csr()

def gather_pair_vectors(pairs, attr, attr_find, attr_sent,
                        unigram_alph,bigram_alph,unigram_feat_alph,
                        map_w1, map_w2, limit):
    extractor=ContextExtractor(attr,unigram_alph,bigram_alph,attr_sent,alph_limit=limit)
    left_matrix=sparsmat.VecI2()
    for i,(w1_u, w2_u) in enumerate(pairs):
        if isinstance(w1_u,unicode):
            w1=w1_u.encode('ISO-8859-15','replace')
        else:
            w1=w1_u
        if isinstance(w2_u,unicode):
            w2=w2_u.encode('ISO-8859-15','replace')
        else:
            w2=w2_u
        #print >>sys.stderr,w1,w2
        sys.stderr.write('.')
        try:
            if map_w1 is None or w1 not in map_w1:
                lst1=attr_find.find(w1)
            else:
                lst1=attr_find.find_list(map_w1[w1])
            if map_w2 is None or w2 not in map_w2:
                lst2=attr_find.find(w2)
            else:
                lst2=attr_find.find_list(map_w2[w2])
            extractor.collect_pair_context(lst1,lst2,i,unigram_feat_alph,left_matrix)
        except KeyError,e:
            print >>sys.stderr, "Cannot find %s %s: %s"%(w1, w2, e)
    return left_matrix.to_csr()

def create_bow_tag(corpora, language, pos_tags, outdir='.',alph_suffix=''):
    # Step 1: extract unigram distributions for words
    unigram_alph=CPPUniAlphabet()
    unigram_alph.fromfile(file(os.path.join(outdir,'unigram%s_alph.txt'%(alph_suffix,))))
    unigram_alph.growing=False
    bigram_alph=CPPUniAlphabet()
    bigram_alph.fromfile(file(os.path.join(outdir,'bigram%s_alph.txt'%(alph_suffix,))))
    bigram_alph.growing=False
    infix='_'.join(prefix_l)
    if infix!='': infix='_'+infix
    if opts.limit!=-1:
        prefix_l.append('%d'%(opts.limit/1000))
    word_matrix=None
    word_alphs=get_word_alphs_by_pos(language)
    for word_pos in pos_tags:
        word_alph=word_alphs[word_pos]
        word_feat_alph=CPPUniAlphabet()
        for corpus_name in corpora:
            corpus=Corpus(corpus_name)
            att=corpus.attribute(opts.attr_name,'p')
            att_find=corpus.attribute('tb_lemma','p')
            att_sent=corpus.attribute('s','s')
            pair_alphs=get_pair_alphs_by_pos(opts.language)
            word_alphs=get_word_alphs_by_pos(opts.language)
            print "word features for %s in %s"%(word_pos,corpus_name)
            wmat=gather_word_vectors(list(word_alph),att, att_find, att_sent,
                                                unigram_alph, bigram_alph, word_feat_alph,
                                                forward_mapping_by_pos(word_pos),
                                                opts.limit)
            if word_matrix is None:
                word_matrix=wmat
            else:
                word_matrix+=wmat
        word_feat_alph.tofile_utf8(file(os.path.join(opts.outdir,'word_bow%s%s_alph.txt'%(infix,word_pos,)),'w'))
        word_matrix.write_binary(file(os.path.join(opts.outdir,'word_bow%s%s_mtx.bin'%(infix,word_pos,)),'w'))

def create_bow_pair(corpora, language, pos_pairs, outdir='.',alph_suffix=''):
    unigram_alph=CPPUniAlphabet()
    unigram_alph.fromfile(file(os.path.join(outdir,'unigram%s_alph.txt'%(alph_suffix,))))
    unigram_alph.growing=False
    bigram_alph=CPPUniAlphabet()
    bigram_alph.fromfile(file(os.path.join(outdir,'bigram%s_alph.txt'%(alph_suffix,))))
    bigram_alph.growing=False
    if opts.limit!=-1:
        prefix_l.append('%d'%(opts.limit/1000))
    pair_alphs=get_pair_alphs_by_pos(language)
    for word_pos in pos_pairs:
        pair_alph=pair_alphs[word_pos]
        pair_feat_alph=CPPUniAlphabet()
        word_matrix=None
        for corpus_name in corpora:
            print "word pair features for %s"%(pos_pair,)
            pair_feat_alph=CPPUniAlphabet()
            for corpus_name in corpora:
                wmat=gather_pair_vectors([x.split('_',1) for x in pair_alph], att, att_find, att_sent,
                                         unigram_alph, bigram_alph, pair_feat_alph,
                                         forward_mapping_by_pos(pos_pair[0]),
                                         forward_mapping_by_pos(pos_pair[1]),
                                         opts.limit)
                if word_matrix is None:
                    word_matrix=wmat
                else:
                    word_matrix+=wmat
        pair_feat_alph.tofile_utf8(file('pair_bow%s%s_alph.txt'%(infix,pos_pair,),'w'))
        word_matrix.write_binary(file('pair_bow%s%s_mtx.bin'%(infix,pos_pair,),'w'))

oparse=optparse.OptionParser()
oparse.add_option('--lang', dest='language',
                  default='DE')
oparse.add_option('--limit', type="int", dest="limit",
                  default=-1)
oparse.add_option('--attr', dest="attr_name",
                  default="word")
oparse.add_option('--outdir', dest="outdir",
                  default=".")

def main():
    opts,args=oparse.parse_args(sys.argv[1:])
    prefix_l=[]
    if args:
        corpora=args
        prefix_l.append('-'.join(args))
    else:
        corpora=get_config_var('dist_sim.$lang.default_corpora',{'lang':opts.language})
    if opts.attr_name!='word':
        alph_suffix='_'+opts.attr_name
        prefix_l.append(opts.attr_name)
    else:
        alph_suffix=''
    infix='_'.join(prefix_l)
    if infix!='': infix='_'+infix
    pos_pairs=get_task_pos_pairs(language=opts.language)
    create_bow_pair(corpora, opts.language, pos_pairs, opts.outdir, alph_suffix, infix)
    pos_tags=get_task_pos_tags(language=opts.language)
    create_bow_tag(corpora, opts.language, pos_tags, opts.outdir, alph_suffix, infix)
    print >>sys.stderr,"Exiting normally."
