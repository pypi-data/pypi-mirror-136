#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: T. Malfatti <malfatti@disroot.org>
@date: 20170612
@license: GNU GPLv3 <https://gitlab.com/malfatti/SciScripts/raw/master/LICENSE>
@homepage: https://gitlab.com/Malfatti/SciScripts
"""

import numpy as np
from itertools import combinations,product
from scipy import stats as sstats

from sciscripts.IO.Txt import Print

try:
    from rpy2 import robjects as RObj
    from rpy2.robjects import packages as RPkg
except ModuleNotFoundError as e:
    print(f'[Analysis.Stats] {e}: Module `rpy2` not available. Some functions will not work.')

SubAnovas = ('ANOVA','WelchAnOVa','KruskalWallis','Friedman')
SubPWCs = ('TTest', 'Wilcoxon')

## Level 0
def sak(d):
    k = [_ for _ in SubAnovas if _ in d.keys()]
    k = k[0] if len(k) else None
    return(k)

def spk(d):
    k = [_ for _ in SubPWCs if _ in d.keys()]
    k = k[0] if len(k) else None
    return(k)

def GetAnovaReport(Anova, FacNames):
    Report = []
    try:
        if Anova[sak(Anova)]['p'].min()<0.05:
            Report.append(f'''
        {len(FacNames)}-way anova:
            {Anova[sak(Anova)]['Effect'][Anova[sak(Anova)]['p']<0.05]},
            F: {Anova[sak(Anova)]['F'][Anova[sak(Anova)]['p']<0.05]},
            p: {Anova[sak(Anova)]['p'][Anova[sak(Anova)]['p']<0.05]}
        ''')
    except IndexError: pass
    except KeyError: pass

    if 'FXs' in Anova.keys():
        Report.append('\n'); Report.append('Sub anovas:\n')

        rd = {}
        for kf,vf in Anova['FXs'].items():
            if sak(vf) is None: continue

            kvpk = 'p.adj' if 'p.adj' in vf[sak(vf)] else 'p'
            fnl = tuple(FacNames)+('Effect',kvpk,'F')
            vfps = vf[sak(vf)][kvpk]
            kvpv = np.array([
                _ if _ is not None else np.nan
                for _ in vf[sak(vf)][kvpk]
            ])

            for k,v in vf[sak(vf)].items():
                if k in fnl and vfps.size and kvpv.min()<0.05:
                    if kf not in rd.keys(): rd[kf] = {}
                    rd[kf][k] = v[kvpv<0.05]

                    for esk in (sak(vf)+'EffSize', sak(vf)+'Effect'):
                        if esk in vf.keys():
                            rd[kf][esk] = vf[esk]['effsize'][kvpv<0.05]

        Report.append(Print(rd))


    if 'PWCs' in Anova.keys():
        Report.append('\n'); Report.append('Pairwise comparisons:\n')

        rd = {}
        for kf,vf in Anova['PWCs'].items():
            if spk(vf) is None: continue

            kvpk = 'p.adj' if 'p.adj' in vf[spk(vf)] else 'p'
            fnl = tuple(FacNames)+('group1','group2','Effect',kvpk,'F')
            vfps = vf[spk(vf)][kvpk]

            for k,v in vf[spk(vf)].items():
                if k in fnl and vfps.size and vfps.min()<0.05:
                    if kf not in rd.keys(): rd[kf] = {}
                    rd[kf][k] = v[vfps<0.05]

                    for esk in (spk(vf)+'EffSize', spk(vf)+'Effect'):
                        if esk in vf.keys():
                            rd[kf][esk] = vf[esk]['effsize'][vfps<0.05]

        Report.append(Print(rd))

    Report.append('='*72); Report.append('\n')
    return(Report)


def GetSigEff(Anova):
    pss = Anova['p']<0.05
    if True in pss:
        pssFacOrder = sorted(
            [_.split(':') for _ in Anova['Effect'][pss]],
            key=lambda x:len(x), reverse=True
        )
        pssFacOrder = [sorted(pssFacOrder[0])]+[
            sorted(p) if len(p)>1 else p for p in pssFacOrder[1:]
            # if not np.prod([_ in pssFacOrder[0] for _ in ['Epoch', 'Class']])
        ]
    else:
        pssFacOrder = []

    return(pssFacOrder)


def IsMatched(Factor, Paired, FactorsGroupBy=[]):
    ThisFactor = np.array(Factor)
    if ThisFactor.dtype == np.dtype('O'):
        raise TypeError('`Factor` should be a list or array of strings!')

    if Paired:
        if len(FactorsGroupBy):
            IM = [[f==fac for fac in np.unique(f)] for f in FactorsGroupBy]
            IM = [
                np.prod(
                    [IM[e][el] for e,el in enumerate(p)]
                    , axis=0
                ).astype(bool)
                for p in product(*(range(len(_)) for _ in IM))
            ]

            IM = [
                np.unique([
                    ThisFactor[i*(ThisFactor==_)].shape
                    for _ in np.unique(ThisFactor)
                ]).shape[0] == 1
                for i in IM
            ]

            IM = False not in IM
        else:
            IM = [len(ThisFactor[ThisFactor==_]) for _ in np.unique(ThisFactor)]
            IM = np.unique(IM).shape[0] == 1
    else:
        IM = False


    return(IM)


def PearsonRP(A,B):
    r = sstats.pearsonr(A, B)
    r = list(r)
    r[0] = round(r[0], 3)
    if r[1] < 0.05:
        r[1] = '%.1e' % r[1] + ' *'
    else:
        r[1] = str(round(r[1], 3))

    return(r)


def PToStars(p, Max=3):
    No = 0
    while p < 0.05 and No < Max:
        p *=10
        No +=1

    return(No)


def RAdjustNaNs(Array):
    try: NaN = RObj.NA_Real
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    for I, A in enumerate(Array):
        if A != A: Array[I] = NaN

    return(Array)


def RCheckPackage(Packages):
    try:
        RPacksToInstall = [Pack for Pack in Packages if not RPkg.isinstalled(Pack)]
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if len(RPacksToInstall) > 0:
        print(str(RPacksToInstall), 'not installed. Install now?')
        Ans = input('[y/N]: ')

        if Ans.lower() in ['y', 'yes']:
            from rpy2.robjects.vectors import StrVector as RStrVector

            RUtils = RPkg.importr('utils')
            RUtils.chooseCRANmirror(ind=1)

            RUtils.install_packages(RStrVector(RPacksToInstall))

        else: print('Aborted.')

    return(None)


def RModelToDict(Model):
    Dict = {}
    Dict['l'] = []

    for C,Col in Model.items():
        try:
            Dict[C] = np.array(list(Col.iter_labels()))
        except AttributeError:
            if C is None and 'rpy2.robjects.vectors.DataFrame' in str(type(Col)):
                Dict['l'] += [{c: RModelToDict(col) for c,col in Col.items()}]
            elif 'rpy2.robjects.vectors.DataFrame' in str(type(Col)):
                Dict[C] = RModelToDict(Col)
            elif C is None:
                Dict = np.array(Col)
            else:
                Dict[C] = np.array(Col)

    if type(Dict) == dict:
        if not len(Dict['l']): del(Dict['l'])
        if list(Dict.keys()) == ['l']: Dict = Dict['l']

    return(Dict)


## Level 1
def Friedman(Data, Factor, Id, FactorName='Factor', FactorsGroupBy=[], FactorGBNames=[], pAdj='holm'):
    try:
        RCheckPackage(['rstatix']); RPkg.importr('rstatix')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if not len(FactorGBNames):
        FactorGBNames = [f'FactorGB{_+1}' for _ in range(len(FactorsGroupBy))]

    Values = RObj.FloatVector(Data)
    Idv = RObj.IntVector(Id)
    FactorsV = [RObj.FactorVector(_) for _ in [Factor]+FactorsGroupBy]
    Frame = {([FactorName]+FactorGBNames)[f]: F for f,F in enumerate(FactorsV)}
    Frame['Values'] = Values
    Frame['Id'] = Idv
    Frame = RObj.DataFrame(Frame)

    RObj.globalenv['Frame'] = Frame
    RObj.globalenv['Values'] = Values
    RObj.globalenv['Id'] = Idv
    for F,FFactor in enumerate(FactorsV):
        RObj.globalenv[([FactorName]+FactorGBNames)[F]] = FFactor

    fGB = f"group_by({','.join(FactorGBNames)}) %>%" if len(FactorsGroupBy) else ''

    Model = RObj.r(f'''Frame %>% {fGB} friedman_test(Values~{FactorName}|Id) %>% adjust_pvalue(method="{pAdj}")''')
    Modelc = RObj.r(f'''Frame %>% {fGB} friedman_effsize(Values~{FactorName}|Id)''')

    Result = {'Friedman': RModelToDict(Model), 'FriedmanEffect': RModelToDict(Modelc)}
    Result['Friedman']['Effect'] = np.array([FactorName]*len(Result['Friedman']['p']))
    return(Result)


def Levene(Data, Factor, FactorName='Factor', FactorsGroupBy=[], FactorGBNames=[], pAdj='holm'):
    try:
        RCheckPackage(['rstatix']); RPkg.importr('rstatix')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if not len(FactorGBNames):
        FactorGBNames = [f'FactorGB{_+1}' for _ in range(len(FactorsGroupBy))]

    Values = RObj.FloatVector(Data)
    FactorsV = [RObj.FactorVector(_) for _ in [Factor]+FactorsGroupBy]
    Frame = {([FactorName]+FactorGBNames)[f]: F for f,F in enumerate(FactorsV)}
    Frame['Values'] = Values
    Frame = RObj.DataFrame(Frame)

    RObj.globalenv['Frame'] = Frame
    RObj.globalenv['Values'] = Values
    for F,FFactor in enumerate(FactorsV):
        RObj.globalenv[([FactorName]+FactorGBNames)[F]] = FFactor

    fGB = f"group_by({','.join(FactorGBNames)}) %>%" if len(FactorsGroupBy) else ''

    Model = RObj.r(f'''Frame %>% {fGB} levene_test(Values~{FactorName}) %>% adjust_pvalue(method="{pAdj}")''')
    Result = {'Levene': RModelToDict(Model)}
    return(Result)


def KruskalWallis(Data, Factor, FactorName='Factor', FactorsGroupBy=[], FactorGBNames=[], pAdj='holm'):
    try:
        RCheckPackage(['rstatix']); RPkg.importr('rstatix')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if not len(FactorGBNames):
        FactorGBNames = [f'FactorGB{_+1}' for _ in range(len(FactorsGroupBy))]

    Values = RObj.FloatVector(Data)
    FactorsV = [RObj.FactorVector(_) for _ in [Factor]+FactorsGroupBy]
    Frame = {([FactorName]+FactorGBNames)[f]: F for f,F in enumerate(FactorsV)}
    Frame['Values'] = Values
    Frame = RObj.DataFrame(Frame)

    RObj.globalenv['Frame'] = Frame
    RObj.globalenv['Values'] = Values
    for F,FFactor in enumerate(FactorsV):
        RObj.globalenv[([FactorName]+FactorGBNames)[F]] = FFactor

    fGB = f"group_by({','.join(FactorGBNames)}) %>%" if len(FactorsGroupBy) else ''

    Model = RObj.r(f'''Frame %>% {fGB} kruskal_test(Values~{FactorName}) %>% adjust_pvalue(method="{pAdj}")''')
    Modelc = RObj.r(f'''Frame %>% {fGB} kruskal_effsize(Values~{FactorName})''')

    Result = {'KruskalWallis': RModelToDict(Model), 'KruskalWallisEffect': RModelToDict(Modelc)}
    Result['KruskalWallis']['Effect'] = np.array([FactorName]*len(Result['KruskalWallis']['p']))
    return(Result)


def RPCA(Matrix):
    try:
        RCheckPackage(['stats']); Rstats = RPkg.importr('stats')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    RMatrix = RObj.Matrix(Matrix)
    PCA = Rstats.princomp(RMatrix)
    return(PCA)


def RAnOVa(Data, Factors, Id, Paired, FactorNames=[], FactorsGroupBy=[], FactorGBNames=[], pAdj='holm'):
    try:
        RCheckPackage(['rstatix']); RPkg.importr('rstatix')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if not len(FactorNames):
        FactorNames = [f'Factor{_+1}' for _ in range(len(Factors))]
    if not len(FactorGBNames):
        FactorGBNames = [f'FactorGB{_+1}' for _ in range(len(FactorsGroupBy))]

    Values = RObj.FloatVector(Data)
    FactorsV = [RObj.FactorVector(_) for _ in Factors+FactorsGroupBy]
    Idv = RObj.IntVector(Id)

    Frame = {(list(FactorNames)+FactorGBNames)[f]: F for f,F in enumerate(FactorsV)}
    Frame['Id'] = Idv
    Frame['Values'] = Values
    Frame = RObj.DataFrame(Frame)

    RObj.globalenv['Frame'] = Frame
    RObj.globalenv['Id'] = Idv
    RObj.globalenv['Values'] = Values
    for F,FFactor in enumerate(FactorsV):
        RObj.globalenv[(list(FactorNames)+FactorGBNames)[F]] = FFactor

    FactorsW = ','.join([FactorNames[_] for _ in range(len(Factors)) if Paired[_]])
    FactorsB = ','.join([FactorNames[_] for _ in range(len(Factors)) if not Paired[_]])
    fGB = f"group_by({','.join(FactorGBNames)}) %>%" if len(FactorsGroupBy) else ''

    Model = RObj.r(f'''Frame %>% {fGB} anova_test(dv=Values, wid=Id, between=c({FactorsB}), within=c({FactorsW})) %>% adjust_pvalue(method="{pAdj}")''')
    Result = RModelToDict(Model)

    if 'ANOVA' not in Result.keys() and 'anova' not in Result.keys(): Result = {'ANOVA': Result}
    if 'anova' in Result.keys() and 'ANOVA' not in Result.keys(): Result['ANOVA'] = Result.pop('anova')

    if type(Result['ANOVA']) == list:
        N = np.unique([len(_) for _ in Result.values()])
        if len(N) > 1:
            raise IndexError('All values should have the same length.')

        fKeys = {_ for _ in Result.keys() if _ != 'ANOVA'}
        a = {}
        for n in range(N[0]):
            rKeys = list(Result['ANOVA'][n].keys())
            if 'ANOVA' in rKeys:
                for k in rKeys:
                    if k not in a.keys(): a[k] = {}

                    sKeys = list(Result['ANOVA'][n][k].keys())
                    for s in sKeys:
                        if s not in a[k].keys(): a[k][s] = []
                        a[k][s].append(Result['ANOVA'][n][k][s])

                    for f in fKeys:
                        if f not in a[k].keys(): a[k][f] = []
                        a[k][f].append([Result[f][n]]*Result['ANOVA'][n][k][s].shape[0])
            else:
                if 'ANOVA' not in a.keys(): a['ANOVA'] = {}

                for k in rKeys:
                    if k not in a['ANOVA'].keys(): a['ANOVA'][k] = []
                    kn = Result['ANOVA'][n][k].shape[0] if len(Result['ANOVA'][n][k].shape) else 1

                    if kn==1:
                        a['ANOVA'][k].append([Result['ANOVA'][n][k]])
                    else:
                        a['ANOVA'][k].append(Result['ANOVA'][n][k])

                for f in fKeys:
                    if f not in a['ANOVA'].keys(): a['ANOVA'][f] = []
                    a['ANOVA'][f].append([Result[f][n]]*kn)


        Result = {K: {k: np.concatenate(v) for k,v in V.items()} for K,V in a.items()}

    return(Result)


def RAnOVaAfex(Data, Factors, Paired, Id=[], FactorNames=[]):
    try:
        RCheckPackage(['afex']); RPkg.importr('afex')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if not len(FactorNames):
        FactorNames = [f'Factor{_+1}' for _ in range(len(Factors))]

    Values = RObj.FloatVector(Data)
    FactorsV = [RObj.FactorVector(_) for _ in Factors]
    Frame = {FactorNames[f]: F for f,F in enumerate(FactorsV)}
    Frame['Values'] = Values

    if len(Id):
        Idv = RObj.IntVector(Id)
        RObj.globalenv['Id'] = Idv
        Frame['Id'] = Idv

    Frame = RObj.DataFrame(Frame)

    RObj.globalenv['Frame'] = Frame
    RObj.globalenv['Values'] = Values
    for F,Factor in enumerate(FactorsV): RObj.globalenv[FactorNames[F]] = Factor

    FactorsW = '*'.join([FactorNames[_] for _ in range(len(Factors)) if Paired[_]])
    FactorsAll = '*'.join(FactorNames)

    Model = RObj.r(f'''aov_car(Values ~ {FactorsAll} + Error(1|Id/({FactorsW})), Frame, na.rm=TRUE)''')
    Result = RModelToDict(Model)
    return(Result)


def RAnOVaPwr(GroupNo=None, SampleSize=None, Power=None,
           SigLevel=None, EffectSize=None):
    try:
        RCheckPackage(['pwr']); Rpwr = RPkg.importr('pwr')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if GroupNo is None: GroupNo = RObj.NULL
    if SampleSize is None: SampleSize = RObj.NULL
    if Power is None: Power = RObj.NULL
    if SigLevel is None: SigLevel = RObj.NULL
    if EffectSize is None: EffectSize = RObj.NULL

    Results = Rpwr.pwr_anova_test(k=GroupNo, power=Power, sig_level=SigLevel,
                                  f=EffectSize, n=SampleSize)

    print('Running', Results.rx('method')[0][0] + '... ', end='')
    AnOVaResults = {}
    for Key, Value in {'k': 'GroupNo', 'n': 'SampleSize', 'f': 'EffectSize',
                       'power':'Power', 'sig.level': 'SigLevel'}.items():
        AnOVaResults[Value] = Results.rx(Key)[0][0]

    print('Done.')
    return(AnOVaResults)


def Shapiro(Data, Factors, FactorNames=[], pAdj='holm'):
    try:
        RCheckPackage(['rstatix']); RPkg.importr('rstatix')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if not len(FactorNames):
        FactorNames = [f'Factor{_+1}' for _ in range(len(Factors))]

    Values = RObj.FloatVector(Data)
    FactorsV = [RObj.FactorVector(_) for _ in Factors]
    Frame = {FactorNames[f]: F for f,F in enumerate(FactorsV)}
    Frame['Values'] = Values
    Frame = RObj.DataFrame(Frame)

    RObj.globalenv['Frame'] = Frame
    RObj.globalenv['Values'] = Values
    for F,Factor in enumerate(FactorsV): RObj.globalenv[FactorNames[F]] = Factor

    Model = RObj.r(f'''Frame %>% group_by({','.join(FactorNames)}) %>% shapiro_test(Values) %>% adjust_pvalue(method="{pAdj}")''')
    Result = {'Shapiro': RModelToDict(Model)}

    return(Result)


def TTest(Data, Factor, Paired, FactorName='Factor', FactorsGroupBy=[], FactorGBNames=[], pAdj= "holm", EqualVar=False, Alt="two.sided", ConfLevel=0.95):
    try:
        RCheckPackage(['rstatix']); RPkg.importr('rstatix')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if not len(FactorGBNames):
        FactorGBNames = [f'FactorGB{_+1}' for _ in range(len(FactorsGroupBy))]

    Values = RObj.FloatVector(Data)
    FactorsV = [RObj.FactorVector(_) for _ in [Factor]+FactorsGroupBy]
    Frame = {([FactorName]+FactorGBNames)[f]: F for f,F in enumerate(FactorsV)}
    Frame['Values'] = Values
    Frame = RObj.DataFrame(Frame)

    RObj.globalenv['Frame'] = Frame
    RObj.globalenv['Values'] = Values
    for F,FFactor in enumerate(FactorsV):
        RObj.globalenv[([FactorName]+FactorGBNames)[F]] = FFactor

    fGB = f"group_by({','.join(FactorGBNames)}) %>%" if len(FactorsGroupBy) else ''
    PairedV = 'TRUE' if Paired else 'FALSE'
    EqualVarV = 'TRUE' if EqualVar else 'FALSE'

    try:
        Modelt = RObj.r(f'''Frame %>% {fGB} pairwise_t_test(Values~{FactorName}, paired={PairedV}, var.equal={EqualVarV}, alternative="{Alt}", conf.level={ConfLevel}) %>% adjust_pvalue(method="{pAdj}")''')
    except:
        Modelt = RObj.r(f'''Frame %>% {fGB} pairwise_t_test(Values~{FactorName}, paired={PairedV}, alternative="{Alt}") %>% adjust_pvalue(method="{pAdj}")''')

    Modelc = RObj.r(f'''Frame %>% {fGB} cohens_d(Values~{FactorName}, conf.level={ConfLevel}, var.equal={EqualVarV}, paired={PairedV})''')

    Result = {'TTest': RModelToDict(Modelt), 'CohensD': RModelToDict(Modelc)}
    return(Result)


def WelchAnOVa(Data, Factor, FactorName='Factor', FactorsGroupBy=[], FactorGBNames=[], pAdj='holm'):
    try:
        RCheckPackage(['rstatix']); RPkg.importr('rstatix')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if not len(FactorGBNames):
        FactorGBNames = [f'FactorGB{_+1}' for _ in range(len(FactorsGroupBy))]

    Values = RObj.FloatVector(Data)
    FactorsV = [RObj.FactorVector(_) for _ in [Factor]+FactorsGroupBy]
    Frame = {([FactorName]+FactorGBNames)[f]: F for f,F in enumerate(FactorsV)}
    Frame['Values'] = Values
    Frame = RObj.DataFrame(Frame)

    RObj.globalenv['Frame'] = Frame
    RObj.globalenv['Values'] = Values
    for F,FFactor in enumerate(FactorsV):
        RObj.globalenv[([FactorName]+FactorGBNames)[F]] = FFactor

    fGB = f"group_by({','.join(FactorGBNames)}) %>%" if len(FactorsGroupBy) else ''

    Model = RObj.r(f'''Frame %>% {fGB} welch_anova_test(Values~{FactorName}) %>% adjust_pvalue(method="{pAdj}")''')
    Result = {'WelchAnOVa': RModelToDict(Model)}
    return(Result)


def Wilcoxon(Data, Factor, Paired, FactorName='Factor', FactorsGroupBy=[], FactorGBNames=[], pAdj= "holm", Alt="two.sided", ConfLevel=0.95):
    try:
        RCheckPackage(['rstatix']); RPkg.importr('rstatix')
    except NameError as e:
        raise e(f'[Analysis.Stats] {e}: Module `rpy2` not available.')

    if not len(FactorGBNames):
        FactorGBNames = [f'FactorGB{_+1}' for _ in range(len(FactorsGroupBy))]

    Values = RObj.FloatVector(Data)
    FactorsV = [RObj.FactorVector(_) for _ in [Factor]+FactorsGroupBy]
    Frame = {([FactorName]+FactorGBNames)[f]: F for f,F in enumerate(FactorsV)}
    Frame['Values'] = Values
    Frame = RObj.DataFrame(Frame)

    RObj.globalenv['Frame'] = Frame
    RObj.globalenv['Values'] = Values
    for F,FFactor in enumerate(FactorsV):
        RObj.globalenv[([FactorName]+FactorGBNames)[F]] = FFactor

    fGB = f"group_by({','.join(FactorGBNames)}) %>%" if len(FactorsGroupBy) else ''
    PairedV = 'TRUE' if Paired else 'FALSE'

    try:
        Modelt = RObj.r(f'''Frame %>% {fGB} pairwise_wilcox_test(Values~{FactorName}, paired={PairedV}, alternative="{Alt}", conf.level={ConfLevel}) %>% adjust_pvalue(method="{pAdj}")''')
    except:
        Modelt = RObj.r(f'''Frame %>% {fGB} pairwise_wilcox_test(Values~{FactorName}, paired={PairedV}, alternative="{Alt}") %>% adjust_pvalue(method="{pAdj}")''')

    Modelc = RObj.r(f'''Frame %>% {fGB} wilcox_effsize(Values~{FactorName}, conf.level={ConfLevel}, paired={PairedV}, alternative="{Alt}")''')

    Result = {'Wilcoxon': RModelToDict(Modelt), 'WilcoxonEffSize': RModelToDict(Modelc)}
    return(Result)


## Level 2
def PairwiseComp(Data, Factor, Paired, Parametric='auto', FactorName='Factor', FactorsGroupBy=[], FactorGBNames=[], pAdj='holm', Alt="two.sided", ConfLevel=0.95):
    Results = {}

    if Parametric == 'auto':
        try:
            IsNormal = Shapiro(Data, [Factor], [FactorName], pAdj)
        except Exception as e:
            print('Cannot calculate Shapiro test. Assuming normally-distributed samples.')
            IsNormal = [True]

        if type(IsNormal) == dict:
            Results = {**Results,**IsNormal}
            IsNormal = IsNormal['Shapiro']['p.adj'].min()>0.05
        else:
            IsNormal = False not in IsNormal
    else:
        IsNormal = Parametric

    IsEqVar = Levene(Data, Factor, FactorName, pAdj=pAdj)
    Results.update(IsEqVar)
    IsEqVar = IsEqVar['Levene']['p'].min()>0.05

    IM = IsMatched(Factor, Paired, FactorsGroupBy)

    if IsNormal:
        PWCs = TTest(
            Data, Factor, IM, FactorName, FactorsGroupBy, FactorGBNames, EqualVar=IsEqVar, pAdj=pAdj
        )
    else:
        PWCs = Wilcoxon(
            Data, Factor, IM, FactorName, FactorsGroupBy, FactorGBNames, pAdj=pAdj
        )

    Results = {**Results, **PWCs}

    return(Results)


## Level 3
def AnOVa(Data, Factors, Id, Paired=[], Parametric='auto', FactorNames=[], GetAllPairwise=False, GetInvalidPWCs=False, pAdj='holm'):
    Results = {}

    if not len(Paired):
        print('Assuming all factors are between-subject (unpaired).')
        Paired = [False for _ in Factors]

    if not len(FactorNames):
        FactorNames = [f'Factor{_+1}' for _ in range(len(Factors))]

    if 'int' not in str(type(Id[0])):
        _, Id = np.unique(Id,return_inverse=True)

    # Get full anova
    if Parametric == 'auto':
        try:
            IsNormal = Shapiro(Data, Factors, FactorNames, pAdj)
        except Exception as e:
            print('Cannot calculate Shapiro test. Assuming normally-distributed samples.')
            IsNormal = [True]*len(Factors)

        if type(IsNormal) == dict:
            Results = {**Results,**IsNormal}
            IsNormal = IsNormal['Shapiro']['p.adj'].min()>0.05
        else:
            IsNormal = False not in IsNormal
    else:
        IsNormal = Parametric

    try:
        if len(Factors) == 1:
            IsEqVarL = Levene(Data, Factors[0], pAdj=pAdj)
            IsEqVar = IsEqVarL['Levene']['p.adj'].min()>0.05

            IM = IsMatched(Factors[0], Paired[0])

            if IsNormal and IsEqVar:
                aFull = RAnOVa(Data, Factors, Id, Paired, FactorNames, pAdj=pAdj)
            elif IsNormal and not IsEqVar:
                aFull = WelchAnOVa(Data, Factors[0], FactorNames[0], pAdj=pAdj)
            elif IM:
                try:
                    aFull = Friedman(Data, Factors[0], Id, FactorNames[0], pAdj=pAdj)
                except Exception as e:
                    aFull = KruskalWallis(Data, Factors[0], FactorNames[0], pAdj=pAdj)
            else:
                aFull = KruskalWallis(Data, Factors[0], FactorNames[0], pAdj=pAdj)

            aFull.update(IsEqVarL)

        else:
            aFull = RAnOVa(Data, Factors, Id, Paired, FactorNames, pAdj=pAdj)
    except Exception as e:
        print('Cannot calculate statistics for all factors. Getting all pairwises.')
        aFull = {'ANOVA':{'Effect':[
            ':'.join(_)
            for a in range(len(FactorNames)-1)
            for _ in combinations(FactorNames,a+1)
        ]}}
        GetAllPairwise = True

    Results = {**Results,**aFull}
    aFk = sak(Results)

    # Get sub anovas based on significant effects
    FactorsWi = [_ for _ in range(len(FactorNames)) if Paired[_]]
    FactorsBi = [_ for _ in range(len(FactorNames)) if not Paired[_]]
    FactorsW = [FactorNames[_] for _ in FactorsWi]
    FactorsB = [FactorNames[_] for _ in FactorsBi]

    if GetAllPairwise:
        FullpsFacOrder = sorted(
            [_.split(':') for _ in Results[aFk]['Effect']],
            key=lambda x:len(x), reverse=True
        )
        FullpsFacOrder = [sorted(FullpsFacOrder[0])]+[
            sorted(p) if len(p)>1 else p for p in FullpsFacOrder[1:]
        ]
    else:
        if type(Results[aFk]) == dict:
            FullpsFacOrder = GetSigEff(Results[aFk])
        else:
            raise TypeError('This should be a dict. Check R output')

    FullpsFacOrder = [_ for _ in FullpsFacOrder if len(_) != len(Factors)]
    ToRun = FullpsFacOrder.copy()

    SubCs, PWCs = {}, {}
    while len(ToRun):
        PS = ToRun[0]
        PSs = ':'.join(PS)

        psGB = [Factors[FactorNames.index(_)] for _ in FactorNames if _ not in PS]
        psGBNames = [_ for _ in FactorNames if _ not in PS]
        psWB = [Factors[FactorNames.index(_)] for _ in PS]
        psPaired = [Paired[FactorNames.index(_)] for _ in PS]

        if len(PS) == 1:
            FInd = FactorNames.index(PS[0])

            IsEqVarL = Levene(Data, Factors[FInd], PSs, psGB, pAdj=pAdj)
            IsEqVar = IsEqVarL['Levene']['p.adj'].min()>0.05
            IM = IsMatched(Factors[FInd], Paired[FInd], psGB)

            if IsEqVar and IsNormal:
                SubCs[PSs] = RAnOVa(Data, psWB, Id, psPaired, PS, psGB, psGBNames, pAdj=pAdj)
            elif IsNormal and not IsEqVar:
                SubCs[PSs] = WelchAnOVa(Data, Factors[FInd], PSs, psGB, psGBNames, pAdj=pAdj)
            elif IM:
                try:
                    SubCs[PSs] = Friedman(Data, Factors[FInd], Id, PSs, psGB, psGBNames, pAdj=pAdj)
                except Exception as e:
                    SubCs[PSs] = KruskalWallis(Data, Factors[FInd], PSs, psGB, psGBNames, pAdj=pAdj)
            else:
                SubCs[PSs] = KruskalWallis(Data, Factors[FInd], PSs, psGB, psGBNames, pAdj=pAdj)

            PWCs[PSs] = PairwiseComp(Data, Factors[FInd], Paired[FInd], IsNormal, PSs, psGB, psGBNames, pAdj)
            # PWCs[PSs].update(IsEqVarL)
            SubCs[PSs].update(IsEqVarL)

        else:
            try:
                SubCs[PSs] = RAnOVa(Data, psWB, Id, psPaired, PS, psGB, psGBNames, pAdj=pAdj)
            except Exception as e:
                print(f'Not enough data to run FX for {PSs}.')

        if PSs in SubCs.keys():
            scKey = [_ for _ in SubAnovas if _ in SubCs[PSs].keys()][0]
            if type(SubCs[PSs][scKey]) == dict:
                pssFacOrder = GetSigEff(SubCs[PSs][scKey])
            else:
                raise TypeError('This should be a dict. Check R output')
        else:
            SubCs[PSs] = {}
            pssFacOrder = []

        if not len(pssFacOrder):
            pssFacOrder = [
                sorted(_)
                for _ in tuple(combinations(PS, len(PS)-1))
            ]
            # del(ToRun[0])
            # continue
        else:
            pssFacOrder = [sorted(pssFacOrder[0])] + [
                sorted(_)
                for p in pssFacOrder
                for _ in tuple(combinations(p, len(p)-1))
            ]

        ToRun = [
            _
            for _ in ToRun+pssFacOrder
            if ':'.join(_) not in SubCs.keys()
            and len(_)
        ]
        # print(ToRun)


    # Remove invalid comparisons
    if not GetAllPairwise or not GetInvalidPWCs:
        for PS in FullpsFacOrder:
            PSs = ':'.join(PS)

            FacLevelsValid = {
                _: np.unique(SubCs[PSs][sak(SubCs[PSs])][_][SubCs[PSs][sak(SubCs[PSs])]['p']<0.05])
                for _ in FactorNames if _ in SubCs[PSs][sak(SubCs[PSs])].keys()
            }

            SubFLV = {
                k: {
                    _: np.unique(SubCs[k][sak(SubCs[k])][_][SubCs[k][sak(SubCs[k])]['p']<0.05])
                    for _ in FactorNames if _ in SubCs[k][sak(SubCs[k])].keys()
                }
                for k in SubCs.keys()
                if k!= PSs
                and False not in (_ in PSs.split(':') for _ in k.split(':'))
            }

            SubKeys =  tuple(SubFLV.keys())

            SubFLV = {
                kk: vv
                for k,v in SubFLV.items() if ':' in k
                for kk,vv in v.items() if kk not in FacLevelsValid.keys()
            }

            FacLevelsValid = {**FacLevelsValid, **SubFLV}

            FLVInd = {
                k: [
                    np.array([_ in vv for _ in SubCs[k][sak(SubCs[k])][kk]])
                    for kk,vv in FacLevelsValid.items() if kk in SubCs[k][sak(SubCs[k])]
                ]
                for k in SubKeys
            }

            FLVIndPWC = {
                k: [
                    np.array([_ in vv for _ in PWCs[k][spk(PWCs[k])][kk]])
                    for kk,vv in FacLevelsValid.items() if kk in PWCs[k][spk(PWCs[k])]
                ]
                for k in SubKeys
                if k in PWCs.keys()
            }

            FLVInd = {k: np.prod(v, axis=0).astype(bool) for k,v in FLVInd.items()}
            FLVIndPWC = {k: np.prod(v, axis=0).astype(bool) for k,v in FLVIndPWC.items()}

            SubCs = {**SubCs, **{
                ksub: {
                        ktest: {
                            keff: veff[FLVInd[ksub]] if 'ndarray' in str(type(veff)) else veff for keff,veff in vtest.items()
                        }
                        if ktest in SubAnovas else vtest
                        for ktest,vtest in vsub.items()
                    }
                    if ksub in FLVInd.keys() else vsub
                for ksub,vsub in SubCs.items()
            }}

            PWCs = {**PWCs, **{
                ksub: {
                        ktest: {
                            keff: veff[FLVIndPWC[ksub]] for keff,veff in vtest.items()
                        }
                        for ktest,vtest in vsub.items()
                    }
                    if ksub in FLVInd.keys() else vsub
                for ksub,vsub in PWCs.items()
            }}

    if len(SubCs): Results['FXs'] = {**SubCs}
    if len(PWCs): Results['PWCs'] = {**PWCs}

    return(Results)


