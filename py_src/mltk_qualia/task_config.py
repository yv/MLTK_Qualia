import codecs
import re
import optparse
import sys
from collections import defaultdict
from alphabet import CPPUniAlphabet
from pcfg_site_config import get_config_var
from pynlp.de.smor_pos import get_morphs

__all__=['all_tasks','get_task_pos_pairs','get_task_pos_tags',
         'get_pair_alphs_by_pos', 'get_word_alphs_by_pos',
         'forward_mapping_by_pos','Dataset','get_dataset']

all_tasks=[]

#['Noun-Associations_gold_forCluto.csv','NV','qualia','DE'],
#           ['rektionskomposita.txt','NV','rkomp','DE']]
for lang, conf in get_config_var('dist_sim').iteritems():
    assert len(lang)==2, lang
    for k, dat in conf['datasets'].iteritems():
        all_tasks.append([k,lang,''.join(dat['postags'])])

def get_task_pos_pairs(language=None, task_name=None):
    pairs=set()
    for name, lang, pospair in all_tasks:
        if ((language is None or lang==language) and
            (task_name is None or name==task_name)):
            pairs.add(pospair)
    return sorted(pairs)

def get_task_pos_tags(language=None, task_name=None):
    tags=set()
    for name, lang, pospair in all_tasks:
        if ((language is None or lang==language) and
            (task_name is None or name==task_name)):
            tags.update(pospair)
    return tags

class FilePatternDict(dict):
    def __init__(self, pat, want_utf8=True):
        self.pat=pat
        self.want_utf8=want_utf8
    def __missing__(self, k):
        fname=self.pat%{'pos_tag':k}
        alph=CPPUniAlphabet(want_utf8=self.want_utf8)
        alph.fromfile_utf8(file(fname))
        alph.growing=False
        self[k]=alph
        return alph

pair_alph_cache={}
def get_pair_alphs_by_pos(language):
    if language in pair_alph_cache:
        return pair_alph_cache[language]
    else:
        pair_alph_cache[language]=value=FilePatternDict(get_config_var('dist_sim.$lang.pair_alph_pattern',{'lang':language}))
        return value

word_alph_cache={}
def get_word_alphs_by_pos(language):
    if language in word_alph_cache:
        return word_alph_cache[language]
    else:
        word_alph_cache[language]=value=FilePatternDict(get_config_var('dist_sim.$lang.word_alph_pattern',{'lang':language}))
        return value

_pattern_res={}
def get_regex_for_pattern(pattern):
    if pattern in _pattern_res:
        return _pattern_res[pattern]
    else:
        rx=re.compile(pattern.replace('W','(\S+)').replace('L','(\w+)'))
        _pattern_res[pattern]=rx
        return rx

class Dataset:
    def __init__(self, name, conf, lang):
        self.lang=lang
        self.name=name
        self.postags=''.join(conf['postags'])
        pat=get_regex_for_pattern(conf['pattern'])
        data=[]
        labels=[]
        for l in file(conf['path']):
            m=pat.match(l)
            if not m:
                print >>sys.stderr, "Non-matching line:",l
            else:
                data.append(m.groups()[:-1])
                labels.append([[m.groups()[-1]]])
        self.data=data
        self.labels=labels
    def load_alphabet(self, key=None):
        '''
        retrieves the alphabet for word1(0) or word2(1)
        or the pairs(None)
        '''
        if key is None:
            return get_pair_alphs_by_pos(self.lang)[''.join(self.postags)]
        else:
            return get_word_alphs_by_pos(self.lang)[self.postags[key]]
    def check_alphabets(self):
        alph=self.load_alphabet(None)
        for dat in self.data:
            alph['_'.join(dat)]
        for i,p in enumerate(self.postags):
            alph=self.load_alphabet(i)
            for dat in self.data:
                alph[dat[i]]
    def add_to_vocabulary(self, item_sets):
        p=''.join(self.postags)
        items=item_sets[p]
        for dat in self.data:
            items.add('_'.join(dat))
        for i,p in enumerate(self.postags):
            items=item_sets[p]
            for dat in self.data:
                items.add(dat[i])
        

def get_dataset(name, lang=None):
    '''
    retrieves a dataset with the matching name from the
    configuration.
    '''
    for lang0, conf in get_config_var('dist_sim').iteritems():
        if lang is not None and lang0 != lang:
            continue
        if name in conf['datasets']:
            return Dataset(name, conf['datasets'][name], lang0)
    raise KeyError(name)

_variants_cache={}
def get_variants_by_pos(language, pos_tag):
    """Returns latin1-encoded (baseform, tb-lemma) strings that
    can occur in the tb_lemma attribute"""
    if pos_tag != 'V':
        return None
    if pos_tag in _variants_cache:
        return _variants_cache[language+pos_tag]
    variants=[]
    alph_v=get_word_alphs_by_pos(False)['V']
    for i in xrange(len(alph_v)):
        w=alph_v.get_sym(i)
        morphs=get_morphs(w.replace('#',''),'VVINF')
        for m,l,a in morphs:
            if len(morphs)>1 or l!=w:
                variants.append((w,l))
    _variants_cache[language+pos_tag]=variants
    return variants

def forward_mapping_by_pos(language, pos_tag):
    var=get_variants_by_pos(language, pos_tag)
    if var is None:
        return None
    mapping={}
    for (k,v) in var:
        if k not in mapping:
            lst=[]
            mapping[k]=lst
        else:
            lst=mapping[k]
        if v not in lst:
            lst.append(v)
    return mapping

def compile_alphabets(language, suffix='', wanted_alphs=None):
    pair_pat=get_config_var('dist_sim.$lang.pair_alph_pattern',{'lang':language})
    word_pat=get_config_var('dist_sim.$lang.word_alph_pattern',{'lang':language})
    wanted_words=defaultdict(set)
    conf=get_config_var('dist_sim.'+language)
    for name,cf in conf['datasets'].iteritems():
        print >>sys.stderr, language, name
        dat=Dataset(name,cf,language)
        dat.add_to_vocabulary(wanted_words)
    print >>sys.stderr, "Saving",
    for k,v in wanted_words.iteritems():
        if wanted_alphs is not None and k not in wanted_alphs:
            continue
        print >>sys.stderr, k,
        if len(k)==1:
            fname=word_pat%{'pos_tag':k}+suffix
        else:
            fname=pair_pat%{'pos_tag':k}+suffix
        alph=CPPUniAlphabet(want_utf8=True)
        for word in v:
            alph[word]
            alph.tofile(file(fname,'w'))
    print >>sys.stderr

oparse=optparse.OptionParser()
oparse.add_option('--lang', dest='language',
                  help='compile alphabets for these languages')
oparse.add_option('--suffix', dest='suffix', default='',
                  help='suffix to append to alphabet filenames')
def compile_alphabets_main():
    opts, args=oparse.parse_args()
    if args:
        wanted=args
    else:
        wanted=None
    if opts.language is None:
        languages=sorted(set([x[1] for x in all_tasks]))
    else:
        languages=[opts.language]
    for lang in languages:
        compile_alphabets(lang, opts.suffix, wanted)
    
