import sys
import numpy
from pcfg_site_config import ConfigValue
from alphabet import CPPUniAlphabet
from mltk import Factory
from dist_sim.semkernel import JSDKernel, PolynomialKernel, KPolynomial
from dist_sim import sparsmat
from cStringIO import StringIO

def make_poly_single(n):
    result=[]
    for i in xrange(n):
        lst=[0]*n
        lst[i]=1
        lst.append(1.0/n)
        result.append(tuple(lst))
    return result

class SupportVector(object):
    def __init__(self, sfact, ws):
        self.sfact=sfact
        lst=[]
        for w0 in ws:
            if isinstance(w0,basestring):
                w=w0
                val=1.0
            else:
                w,val=w0
            lst.append((sfact.get_index(w),val))
        lst.sort()
        self.vec=sparsmat.SparseVectorD(lst)
    def rank_similar(self,cand_words):
        kern=self.sfact.get('kernel').kernel
        ranked=[]
        for w in cand_words:
            i=self.sfact.get_index(w)
            score=0.0
            for j,val in self.vec:
                score+=val*kern(i,j)
            ranked.append((w,score))
        ranked.sort(key=lambda x:-x[1])
        return ranked
    def __repr__(self):
        f=StringIO()
        wr=f.write
        alph=self.sfact.get('target_alph')
        wr('<SV')
        for k,v in self.vec:
            wr(' %s:%g'%(alph.get_sym(k),v))
        wr('>')
        return wr.getvalue()

class SimilarityFactory(Factory):
    def load_component_alph(self,name):
        alph=CPPUniAlphabet()
        alph.fromfile(self.open_by_pat('component_alph',matrix_name=name))
        if self.max_range is None:
            self.max_range=len(alph)
        return alph
    def load_component_mat(self,name):
        f_in=self.open_by_pat('component_mat',matrix_name=name)
        mat=sparsmat.mmapCSR(f_in).transform_mi_discount()
        return mat
    def load_target_alph(self):
        alph=CPPUniAlphabet()
        alph.fromfile(self.open_by_pat('target_alph'))
        return alph
    def load_transformed_mat(self, name, transform):
        orig_mat=self.get('component_mat',name)
        if transform=='mi_discount':
            mat=orig_mat.transform_mi_discount()
        elif transform=='mi':
            mat=orig_mat.transform_mi()
        elif transform=='l1':
            mat=orig_mat.transform_l1()
        elif transform=='ll':
            mat=orig_mat.transform_ll()
        else:
            assert False,transform
        return mat
    def get_index(self,name):
        """returns the index for one particular target word"""
        alph=self.get('target_alph')
        return alph[name]
    def load_kernel(self):
        kernels=[JSDKernel(self.get('component_mat',x)) for x in self.val('matrix_names')]
        return KPolynomial(kernels, make_poly_single(len(kernels)))
    def load_similar(self,w):
        kern=self.get('kernel').kernel
        target_alph=self.get('target_alph')
        k1=target_alph[w]
        cands=[]
        for k2 in xrange(self.max_range):
            if k1==k2: continue
            val=kern(k1,k2)
            cands.append((val,k2))
        cands.sort(reverse=True)
        cands=cands[:self.cutoff]
        return [(target_alph.get_sym(k), val) for (val,k) in cands]
    def rank_similar(self,w,cand_words):
        kern=self.get('kernel').kernel
        target_alph=self.get('target_alph')
        k1=target_alph[w]
        cands=[]
        for w2 in cand_words:
            try:
                k2=target_alph[w2]
            except KeyError:
                continue
            if k1==k2: continue
            val=kern(k1,k2)
            cands.append((val,w2))
        cands.sort(reverse=True)
        return cands
    def raw_features(self,w,simplified=False):
        target_alph=self.get('target_alph')
        idx=target_alph[w]
        result=[]
        for mat_name in self.val('matrix_names'):
            mat=self.get('component_mat',mat_name)
            mname=mat_name
            if simplified and '_' in mname:
                mname=mname[mname.index('_')+1:]
            row=mat[idx]
            alphF=self.get('component_alph',mat_name)
            for k0,v in row:
                k=alphF.get_sym_unicode(k0)
                result.append(('%s:%s'%(mname,k),v))
        result.sort(key=lambda x:x[1], reverse=True)
        return result
    def get_collocates(self, w, mat_name, weighting='ll'):
        target_alph=self.get('target_alph')
        idx=target_alph[w]
        result=[]
        mat=self.get('transformed_mat',mat_name,weighting)
        row=mat[idx]
        alphF=self.get('component_alph',mat_name)
        for k0,v in row:
            k=alphF.get_sym_unicode(k0)
            result.append((k,v))
        result.sort(key=lambda x:x[1], reverse=True)
        return result
    def get_vectors(self,w):
        target_alph=self.get('target_alph')
        idx=target_alph[w]
        result=[]
        for mat_name in self.val('matrix_names'):
            mat=self.get('component_mat',mat_name)
            row=mat[idx]
            result.append(row)
        return result
    def common_features(self,w1,w2,simplified=False):
        target_alph=self.get('target_alph')
        idx1=target_alph[w1]
        idx2=target_alph[w2]
        result=[]
        for mat_name in self.val('matrix_names'):
            mat=self.get('component_mat',mat_name)
            mname=mat_name
            if simplified and '_' in mname:
                mname=mname[mname.index('_')+1:]
            row=mat[idx1].min_vals(mat[idx2])
            alphF=self.get('component_alph',mat_name)
            for k0,v in row:
                k=alphF.get_sym_unicode(k0)
                result.append(('%s:%s'%(mname,k),v))
        result.sort(key=lambda x:x[1], reverse=True)
        return result

simfact=SimilarityFactory(lang='DE',
                          target_alph_pattern=ConfigValue('dist_sim.$lang.word_alph_pattern'),
                          component_alph_pattern=ConfigValue('dist_sim.$lang.component_alph_pattern'),
                          component_mat_pattern=ConfigValue('dist_sim.$lang.component_mat_pattern'),
                          cutoff=250, max_range=7000, pos_tag='N',
                          matrix_names=ConfigValue('dist_sim.$lang.default_matrices.$pos_tag'))

class FeatureMatrix(Factory):
    def load_component_alph(self):
        name=self.matrix_name
        alph=CPPUniAlphabet()
        alph.fromfile(self.open_by_pat('component_alph',matrix_name=name))
        return alph
    def load_transformed_mat(self):
        name=self.matrix_name
        bound=self.bound
        thr_val=self.thr_val
        method=self.method
        f_in=self.open_by_pat('component_mat',matrix_name=name)
        orig_mat=sparsmat.mmapCSR(f_in)
        # Step one: weighting function
        transform=self.transform
        if transform=='mi_discount':
            orig_mat=orig_mat.transform_mi_discount()
        elif transform=='mi':
            orig_mat=orig_mat.transform_mi()
        elif transform=='l1':
            orig_mat=orig_mat.transform_l1()
        elif transform=='ll':
            orig_mat=orig_mat.transform_ll()
        else:
            assert False, transform
        # Step 2: calculate thresholds
        if bound=='const':
            thresholds=numpy.zeros(len(self.get('component_alph')))
            thresholds+=thr_val
        elif bound=='norm':
            thresholds=orig_mat.thresholds_norm(thr_val)
        elif bound=='quant':
            thresholds=orig_mat.thresholds_quantile(thr_val)
        elif bound=='nonzero':
            thresholds=orig_mat.thresholds_nonzero(thr_val)
        else:
            assert False, bound
        if method=='threshold':
            orig_mat=orig_mat.apply_threshold(thresholds)
        elif method=='scale':
            orig_mat=orig_mat.apply_scaling(thresholds)
        else:
            assert False, method
        return orig_mat
    def get_features(self, pair_idx):
        counts=self.get('transformed_mat')
        alph=self.get('component_alph')
        feats=[]
        for k_idx,v in counts[pair_idx]:
            k=alph.get_sym_unicode(k_idx)
            # TODO normalize/threshold weights?
            feats.append((k,v))
        return feats
    def get_max_features(self, idxs, prefix=''):
        counts=self.get('transformed_mat')
        alph=self.get('component_alph')
        vec=counts[idxs[0]]
        for other_vec in [counts[idx] for idx in idxs[1:]]:
            vec |= other_vec
        feats=[]
        for k_idx,v in vec:
            k=alph.get_sym_unicode(k_idx)
            # TODO normalize/threshold weights?
            feats.append((prefix+k,v))
        return feats


feat_mat=FeatureMatrix(lang='DE',
                       target_alph_pattern=ConfigValue('dist_sim.$lang.word_alph_pattern'),
                       component_alph_pattern=ConfigValue('dist_sim.$lang.component_alph_pattern'),
                       component_mat_pattern=ConfigValue('dist_sim.$lang.component_mat_pattern'),
                       pos_tag='N',
                       transform='mi', method='threshold', bound='const', thr_val=0.99)
