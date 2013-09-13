# -*- coding: utf-8 -*-
import sys
import numpy
import codecs
import optparse
import simplejson as json
from itertools import izip
from alphabet import CPPUniAlphabet
from dist_sim import sparsmat
import pkg_resources
from pcfg_site_config import get_config_var, ConfigValue
from mltk_qualia.ds_wrap import simfact, feat_mat
from mltk_qualia.task_config import *

class SingleWordFeatures:
    def __init__(self, opts):
        if opts.germanet is 'none':
            self.extractor = lambda w1, w2: []
        else:
            endpoints=list(pkg_resources.iter_entry_points('word_features', '%s_%s'%(opts.language, opts.germanet)))
            if len(endpoints)==0:
                raise ValueError, "There is no extractor for word features called %s for language %s"%(opts.germanet,opts.language)
            elif len(endpoints)>1:
                print >>sys.stderr, "Multiple endpoints found for %s"%(opts.germanet,)
            self.extractor=endpoints[0].load()
    def __call__(self, w1, w2):
        result=[]
        result+=['w1%s'%(feat,) for feat in self.extractor(w1,True)]
        result+=['w2%s'%(feat,) for feat in self.extractor(w2,True)]
        return result

def expand_pairs(w1,w2,expander,pair_alph):
    idxs=[]
    all_w1=expander(w1)
    for w1a in all_w1:
        try:
            k=pair_alph[u'%s_%s'%(w1a,w2)]
            idxs.append(k)
        except KeyError:
            pass
    return idxs

# class GWN_Expander:
#     def __init__(self):
#         self.db=germanet.get_database('gwn6')
#     def __call__(self,w):
#         a1=self.db.synsets_for_word(w)
#         related=list(similar.get_related(a1,2.9,30))
#         return related

# class DS_GWN_Expander(GWN_Expander):
#     def __call__(self,w):
#         related=GWN_Expander.__call__(self,w)
#         ranked=simfact.rank_similar(w,related)
#         return [x[1] for x in ranked[:10]]

oparse=optparse.OptionParser()
oparse.add_option('-L','--lang',dest='language',
                  default='DE',
                  help='language that is used')
oparse.add_option('-m','--matrices',dest='matrices',
                  default='',
                  help='pair features to be used, separated by commas')
oparse.add_option('-M','--word-matrices',dest='wmatrices',
                  default='',
                  help='word features to be used, separated by commas')
oparse.add_option('-1',dest='wmatrices1',
                  default='',
                  help='word features to be used for w1, separated by commas')
oparse.add_option('-2',dest='wmatrices2',
                  default='',
                  help='word features to be used for w2, separated by commas')
oparse.add_option('-G','--germanet',dest='germanet',
                  choices=['none','hyper'],
                  default='none',
                  help='GermaNet/WordNet-based features for single words')
oparse.add_option('--transform',dest='transform',
                  choices=['mi','mi_discount','l1','ll'],
                  default='mi_discount',
                  help='weight transformation')
oparse.add_option('--bound',dest='bound',
                  choices=['const','norm','quant','nonzero'],
                  default='const',
                  help='threshold bound')
oparse.add_option('--method',dest='method',
                  choices=['threshold','scale'],
                  default='threshold')
# oparse.add_option('--expand',dest='expand',
#                   choices=['none','gwn','combo'],
#                   default='none')
oparse.add_option('--dataset', dest='dataset',
                  choices=[x[0] for x in all_tasks],
                  default='qualia')

pair_alph_path=ConfigValue('dist_sim.$lang.pair_alph_pattern')
word_alph_path=ConfigValue('dist_sim.$lang.word_alph_pattern')

def main(argv=None):
    if argv is None:
        opts, args=oparse.parse_args(sys.argv[1:])
    else:
        opts, args=oparse.parse_args(argv)
    data=get_dataset(opts.dataset, opts.language)
    pos_pair=data.postags
    env={'lang':opts.language, 'pos_tag': pos_pair}
    pair_alph=data.load_alphabet(None)
    pair_features=[]
    for k in opts.matrices.split(','):
        if k=='': continue
        print >>sys.stderr, "Loading %s%s ..."%(k,pos_pair)
        pair_features.append(feat_mat.bind(pos_tag=pos_pair, matrix_name=k,
                                           transform=opts.transform, method=opts.method, bound=opts.bound))
    word_alphs=get_word_alphs_by_pos(opts.language)
    word_features={}
    for pos in pos_pair:
        wfeat=[]
        for k in opts.wmatrices.split(','):
            if k=='': continue
            try:
                print >>sys.stderr, "Loading %s%s ..."%(k,pos)
                wfeat.append(feat_mat.bind(pos_tag=pos, matrix_name=k,
                                           transform=opts.transform, method=opts.method, bound=opts.bound))
            except IOError, e:
                print >>sys.stderr, k+pos, e
        word_features[pos]=wfeat
    if opts.wmatrices1:
        simfact1=simfact.bind(pos_tag=pos_pair[0],
                              matrix_names=opts.wmatrices1.split())
    else:
        simfact1=None
    if opts.wmatrices2:
        simfact2=simfact.bind(pos_tag=pos_pair[1],
                              matrix_names=opts.wmatrices2.split())
    else:
        simfact2=None
    single_word_features=SingleWordFeatures(opts)
    # if opts.expand=='none':
    #     expander=None
    # elif opts.expand=='gwn':
    #     expander=GWN_Expander()
    # elif opts.expand=='combo':
    #     expander=DS_GWN_Expander()
    w1_alph=data.load_alphabet(0)
    w1_features=word_features[pos_pair[0]]
    w2_alph=data.load_alphabet(1)
    w2_features=word_features[pos_pair[1]]
    print >>sys.stderr, pos_pair, w1_alph.get_sym(0), w2_alph.get_sym(0)
    for (w1orig,w2orig), gold_label in izip(data.data, data.labels):
        wpair='%s_%s'%(w1orig,w2orig)
        try:
            pair_idx=pair_alph[wpair.replace('#','')]
        except KeyError:
            print >>sys.stderr, "Not found: %s"%(repr(wpair),)
        else:
            w1=w1orig
            w2=w2orig.replace('#','')
            features=single_word_features(w1,w2)
            all_features=[features]
            try:
                idx1=w1_alph[w1]
                for feat in w1_features:
                    try:
                        all_features.append([('w1_'+k,v) for (k,v) in feat.get_features(idx1)])
                    except KeyError:
                        all_features.append([])
            except KeyError:
                print >>sys.stderr, "No such w1: %s"%(repr(w1),), wpair
            try:
                idx2=w2_alph[w2]
                for feat in w2_features:
                    try:
                        all_features.append([('w2_'+k,v) for (k,v) in feat.get_features(idx2)])
                    except KeyError:
                        all_features.append([])
            except KeyError:
                print >>sys.stderr, "No such w2: %s"%(repr(w2),), wpair
            if simfact1 is not None:
                if opts.method=='scale':
                    all_features.append([('w1_'+k,v) for (k,v) in simfact1.raw_features(w1)])
                elif opts.method=='threshold':
                    all_features.append([('w1_'+k,1.0) for (k,v) in simfact1.raw_features(w1) if v>=1.0])
            if simfact2 is not None:
                if opts.method=='scale':
                    all_features.append([('w2_'+k,v) for (k,v) in simfact2.raw_features(w2_orig)])
                elif opts.method=='threshold':
                    all_features.append([('w2_'+k,1.0) for (k,v) in simfact2.raw_features(w2_orig) if v>=1.0])                    
            try:
                idx2=w2_alph[w2]
                for feat in w2_features:
                    try:
                        all_features.append([('w2_'+k,v) for (k,v) in feat.get_features(idx2)])
                    except KeyError:
                        all_features.append([])
            except KeyError:
                print >>sys.stderr, "No such w2: %s"%(repr(w2),)
            for mat in pair_features:
                try:
                    all_features.append(mat.get_features(pair_idx))
                except IndexError:
                    print >>sys.stderr, "No features found: %s"%(repr(wpair),)
            # if opts.expand!='none':
            #     idxs=expand_pairs(w1,w2,expander,pair_alph)
            #     for mat in pair_features:
            #         try:
            #             all_features.append(mat.get_max_features(idxs,'x_'))
            #         except IndexError:
            #             pass
        print json.dumps([0, {'_type':'multipart','parts':all_features}, gold_label, wpair])
