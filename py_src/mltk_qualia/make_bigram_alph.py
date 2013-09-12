import sys
import os.path
from CWB.CL import Corpus
from dist_sim import sparsmat
from alphabet import CPPAlphabet
from itertools import islice
from collections import defaultdict
from pcfg_site_config import get_config_var
import optparse

UNIGRAM_LIMIT=1000
BIGRAM_LIMIT=100

MAX_LIST=10000

def make_frequencies(attr):
    unigrams=sparsmat.LargeVecI1()
    unigrams_add=unigrams.add_count
    bigrams=sparsmat.LargeVecI2()
    bigrams_add=bigrams.add_count
    cpos2id=attr.cpos2id
    last_id=cpos2id(0)
    unigrams_add(last_id)
    N_BIG=3*len(attr.getDictionary())
    old_size=0
    for i in xrange(1,len(attr)):
        next_id=cpos2id(i)
        unigrams_add(next_id)
        bigrams_add(last_id,next_id)
        last_id=next_id
        if (i%100000)==0:
            print >>sys.stderr, "\r",i/1000,
    print >>sys.stderr, i
    unigram_list=[]
    attr_dict=attr.getDictionary()
    for k_id,c in unigrams:
        if c>=UNIGRAM_LIMIT:
            unigram_list.append((c,attr_dict.get_word(k_id)))
    unigram_list.sort(reverse=True)
    bigram_list=[]
    for k1_id, k2_id, c in bigrams:
        if c>=BIGRAM_LIMIT:
            bigram_list.append((c,'%s_%s'%(attr_dict.get_word(k1_id),attr_dict.get_word(k2_id))))
    bigram_list.sort(reverse=True)
    return unigram_list, bigram_list

def make_bigram_alph(corpora, attr_name='word',suffix='', outdir='.'):
    unigram_freqs=defaultdict(int)
    bigram_freqs=defaultdict(int)
    for corpus_name in corpora:
        print >>sys.stderr, "Reading corpus: %s"%(corpus_name,)
        corpus=Corpus(corpus_name)
        att=corpus.attribute(attr_name, 'p')
        unigram_list, bigram_list = make_frequencies(att)
        for v, k in unigram_list:
            unigram_freqs[k]+=v
        for v, k in bigram_list:
            bigram_freqs[k]+=v
    unigram_list=[(v,k) for (k,v) in unigram_freqs.iteritems()]
    unigram_list.sort()
    del unigram_list[MAX_LIST:]
    unigram_alph=CPPAlphabet()
    for c,k in unigram_list:
        unigram_alph[k]
    unigram_alph.tofile(file(os.path.join(outdir, 'unigram%s_alph.txt'%(suffix,)),'w'))
    bigram_list=[(v,k) for (k,v) in bigram_freqs.iteritems()]
    bigram_list.sort()
    del bigram_list[MAX_LIST:]
    bigram_alph=CPPAlphabet()
    for c,k in bigram_list:
        bigram_alph[k]
    bigram_alph.tofile(file(os.path.join(outdir, 'bigram%s_alph.txt'%(suffix,)),'w'))

oparse=optparse.OptionParser()
oparse.add_option('--attr', dest='attr_name',
                  default='word')
oparse.add_option('--lang', dest='language',
                  default='DE')
oparse.add_option('--outdir', dest='outdir',
                  default='.')

def main():
    opts,args=oparse.parse_args()
    if args:
        corpora=args
    else:
        corpora=get_config_var('dist_sim.$lang.default_corpora',{'lang':opts.language})
    if opts.attr_name!='word':
        suffix='_'+attr_name
    else:
        suffix=''
    make_bigram_alph(corpora, opts.attr_name, suffix, opts.outdir)


if __name__=='__main__':
    main()
