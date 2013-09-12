from CWB.CL cimport Corpus, IDList, AttStruc, PosAttrib
from CWB.CL cimport cl_cpos2str, cl_cpos2struc, get_bounds_of_nth_struc
from alphabet cimport CPPUniAlphabet, AbstractAlphabet
from dist_sim.sparsmat cimport VecI2

cdef int MAX_DIST=4

cdef class ContextExtractor:
    cdef AttStruc sentences
    cdef PosAttrib ctx_att
    cdef int win_l, win_r
    cdef int max_pos
    cdef int alph_limit
    cdef AbstractAlphabet alph_unigram, alph_bigram
    def __cinit__(self, PosAttrib ctx,
                  AbstractAlphabet alph_unigram,
                  AbstractAlphabet alph_bigram,
                  AttStruc sentences,
                  win_left=4, win_right=4,
                  alph_limit=-1):
        self.sentences=sentences
        self.ctx_att=ctx
        self.win_l=win_left
        self.win_r=win_right
        self.alph_unigram=alph_unigram
        self.alph_bigram=alph_bigram
        self.max_pos=len(ctx)
        if alph_limit == -1:
            self.alph_limit=len(alph_unigram)
        else:
            self.alph_limit=alph_limit
    cpdef collect_unigrams(self, int k1, prefix, int frm, int to,
                          AbstractAlphabet alph, VecI2 counts):
        cdef char *s
        cdef int sym
        for i from frm<=i<to:
            s=cl_cpos2str(self.ctx_att.att,i)
            sym=self.alph_unigram.sym2num(s)
            if sym!=-1 and sym<self.alph_limit:
                sym=alph[prefix+s]
                counts.c_add(k1,sym,1)
    cpdef collect_bigrams(self, int k1, prefix, int frm, int to,
                          AbstractAlphabet alph, VecI2 counts):
        cdef int sym
        s1=self.ctx_att[frm]
        for i from frm+1<=i<to:
            s2=self.ctx_att[i]
            s='%s_%s'%(s1,s2)
            try:
                sym=self.alph_bigram[s]
                if sym<self.alph_limit:
                    sym=alph[prefix+s]
                    counts.c_add(k1,sym,1)
            except KeyError:
                pass
    cpdef collect_word_context(self, IDList lst, int k1,
                               AbstractAlphabet alph, VecI2 counts):
        cdef int i, pos
        cdef int s_no
        cdef int s_start, s_end
        cdef int ctx_start, ctx_end
        for i from 0<=i<lst.length:
            pos=lst.ids[i]
            ctx_start=pos-self.win_l
            ctx_end=pos+self.win_r
            if ctx_start<0:
                ctx_start=0
            if ctx_end>=self.max_pos:
                ctx_end=self.max_pos
            if self.sentences is not None:
                s_no=cl_cpos2struc(self.sentences.att, pos)
                get_bounds_of_nth_struc(self.sentences.att, s_no, &s_start, &s_end)
                if ctx_start<s_start:
                    ctx_start=s_start
                if ctx_end>s_end:
                    ctx_end=s_end+1
            if self.alph_unigram is not None:
                self.collect_unigrams(k1, b'L', ctx_start, pos,
                                      alph, counts)
                self.collect_unigrams(k1,b'R', pos+1, ctx_end,
                                      alph, counts)
            if self.alph_bigram is not None:
                self.collect_bigrams(k1,b'L', ctx_start, pos,
                                     alph, counts)
                self.collect_bigrams(k1,b'R', pos+1, ctx_end,
                                     alph, counts)
    cpdef collect_pair_context(self, IDList lst1, IDList lst2, int k1,
                                   AbstractAlphabet alph, VecI2 counts):
            cdef int i1, i2, pos1, pos2, s1, s2
            cdef int s_start, s_end
            cdef int ctx_start, ctx_end
            i1=0
            i2=0
            if lst1.length==0 or lst2.length==0:
                return
            pos1=lst1.ids[i1]
            pos2=lst2.ids[i2]
            s1=cl_cpos2struc(self.sentences.att, pos1)
            s2=cl_cpos2struc(self.sentences.att, pos2)
            while i1<lst1.length and i2<lst2.length:
                if s1<s2:
                    i1+=1
                    if i1==lst1.length:
                        break
                    pos1=lst1.ids[i1]
                    s1=cl_cpos2struc(self.sentences.att, pos1)
                elif s2<s1:
                    i2+=1
                    if i2==lst2.length:
                        break
                    pos2=lst2.ids[i2]
                    s2=cl_cpos2struc(self.sentences.att, pos2)
                else:
                    # same sentence
                    if pos1<pos2:
                        if pos1>pos2-MAX_DIST:
                            ctx_start=pos1-self.win_l
                            ctx_end=pos2+self.win_r
                            get_bounds_of_nth_struc(self.sentences.att, s1, &s_start, &s_end)
                            if ctx_start<s_start:
                                ctx_start=s_start
                            if ctx_end>s_end:
                                ctx_end=s_end+1
                            if self.alph_unigram is not None:
                                self.collect_unigrams(k1, b'1L', ctx_start, pos1,
                                                      alph, counts)
                                self.collect_unigrams(k1, b'1M', pos1+1, pos2,
                                                      alph, counts)
                                self.collect_unigrams(k1,b'1R', pos2+1, ctx_end,
                                                      alph, counts)
                            if self.alph_bigram is not None:
                                self.collect_bigrams(k1, b'1L', ctx_start, pos1,
                                                      alph, counts)
                                self.collect_bigrams(k1, b'1M', pos1+1, pos2,
                                                      alph, counts)
                                self.collect_bigrams(k1,b'1R', pos2+1, ctx_end,
                                                     alph, counts)
                        i1+=1
                        if i1==lst1.length:
                            break
                        pos1=lst1.ids[i1]
                        s1=cl_cpos2struc(self.sentences.att, pos1)
                    else:
                        if pos1<pos2+MAX_DIST:
                            ctx_start=pos2-self.win_l
                            ctx_end=pos1+self.win_r
                            get_bounds_of_nth_struc(self.sentences.att, s1, &s_start, &s_end)
                            if ctx_start<s_start:
                                ctx_start=s_start
                            if ctx_end>s_end:
                                ctx_end=s_end+1
                            if self.alph_unigram is not None:
                                self.collect_unigrams(k1, b'2L', ctx_start, pos2,
                                                      alph, counts)
                                self.collect_unigrams(k1, b'2M', pos2+1, pos1,
                                                      alph, counts)
                                self.collect_unigrams(k1,b'2R', pos1+1, ctx_end,
                                                      alph, counts)
                            if self.alph_bigram is not None:
                                self.collect_bigrams(k1, b'2L', ctx_start, pos1,
                                                      alph, counts)
                                self.collect_bigrams(k1, b'2M', pos1+1, pos2,
                                                      alph, counts)
                                self.collect_bigrams(k1,b'2R', pos2+1, ctx_end,
                                                     alph, counts)
                        i2+=1
                        if i2==lst2.length:
                            break
                        pos2=lst2.ids[i2]
                        s2=cl_cpos2struc(self.sentences.att, pos2)
                    
