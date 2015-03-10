# -*- coding: UTF-8 -*-
from collections import OrderedDict
import unittest
from delphin.mrs.components import (
    MrsVariable, AnchorMixin, Lnk, LnkMixin, Hook,
    Argument, Link, HandleConstraint,
    Pred, Node, ElementaryPredication as EP
)
from delphin.mrs.config import (
    QEQ, LHEQ, OUTSCOPES, CVARSORT, IVARG_ROLE, CONSTARG_ROLE,
    EQ_POST, HEQ_POST, NEQ_POST, H_POST, NIL_POST,
    LTOP_NODEID, FIRST_NODEID, ANCHOR_SORT,
)

class TestMrsVariable(unittest.TestCase):
    def test_construct(self):
        self.assertRaises(TypeError, MrsVariable)
        self.assertRaises(TypeError, MrsVariable, 1)
        self.assertRaises(TypeError, MrsVariable, sort='h')
        self.assertRaises(TypeError, MrsVariable, 1, properties={'a':1})
        v = MrsVariable(1, 'h')
        self.assertNotEqual(v, None)

    def test_from_string(self):
        self.assertRaises(ValueError, MrsVariable.from_string('1x'))
        self.assertRaises(ValueError, MrsVariable.from_string('var'))
        v = MrsVariable.from_string('x1')
        self.assertNotEqual(v, None)

    def test_values(self):
        v = MrsVariable(1, 'x')
        self.assertEqual(v.vid, 1)
        self.assertEqual(v.sort, 'x')
        self.assertEqual(len(v.properties), 0)
        v = MrsVariable(10, 'event', properties={'a':1})
        self.assertEqual(v.vid, 10)
        self.assertEqual(v.sort, 'event')
        self.assertEqual(v.properties, {'a':1})
        v = MrsVariable.from_string('event10')
        self.assertEqual(v.vid, 10)
        self.assertEqual(v.sort, 'event')
        self.assertEqual(len(v.properties), 0)

    def test_str(self):
        v = MrsVariable(1, 'x')
        self.assertEqual(str(v), 'x1')
        v = MrsVariable(10, 'individual')
        self.assertEqual(str(v), 'individual10')

    def test_equality(self):
        v = MrsVariable(1, 'x')
        self.assertEqual(v, MrsVariable(1, 'x'))
        self.assertEqual(v, 'x1')
        self.assertNotEqual(v, 'x2')
        self.assertNotEqual(v, 'e1')
        self.assertNotEqual(v, 'x')
        self.assertEqual(v, 1)

    def test_hashable(self):
        v1 = MrsVariable(1, 'x')
        v2 = MrsVariable(2, 'e')
        d = {v1:'one', v2:'two'}
        self.assertEqual(d[v1], 'one')
        self.assertEqual(d['x1'], 'one')
        self.assertEqual(d[v2], 'two')
        self.assertRaises(KeyError, d.__getitem__, v1.vid)
        self.assertRaises(KeyError, d.__getitem__, v1.sort)
        # note: it's invalid to have two variables with different VIDs
        v3 = MrsVariable(2, 'x')
        d[v3] = 'three'
        self.assertEqual(len(d), 3)
        self.assertEqual(d[v3], 'three')

    def test_sort_vid_split(self):
        svs = MrsVariable.sort_vid_split
        self.assertEqual(svs('x1'), ('x', '1'))
        self.assertEqual(svs('event10'), ('event', '10'))
        self.assertRaises(ValueError, svs, 'x')
        self.assertRaises(ValueError, svs, '1')
        self.assertRaises(ValueError, svs, '1x')


class TestAnchorMixin(unittest.TestCase):
    def test_inherit(self):
        class NoNodeId(AnchorMixin):
            pass
        n = NoNodeId()
        self.assertRaises(AttributeError, getattr, n, 'anchor')
        class WithNodeId(AnchorMixin):
            def __init__(self):
                self.nodeid = 0
        n = WithNodeId()
        self.assertEqual(n.anchor, MrsVariable(0, ANCHOR_SORT))
        n.anchor = MrsVariable(1, ANCHOR_SORT)
        self.assertEqual(n.anchor, MrsVariable(1, ANCHOR_SORT))


class TestLnk(unittest.TestCase):
    def testLnkTypes(self):
        # invalid Lnk type
        self.assertRaises(ValueError, Lnk, data=(0,1), type='invalid')
        self.assertRaises(ValueError, Lnk, data=(0,1), type=None)

    def testCharSpanLnk(self):
        lnk = Lnk.charspan(0, 1)
        self.assertEqual(lnk.type, Lnk.CHARSPAN)
        self.assertEqual(lnk.data, (0,1))
        lnk = Lnk.charspan('0', '1')
        self.assertEqual(lnk.data, (0,1))
        self.assertRaises(TypeError, Lnk.charspan, 1)
        self.assertRaises(TypeError, Lnk.charspan, [1])
        self.assertRaises(TypeError, Lnk.charspan, 1, 2, 3)
        self.assertRaises(ValueError, Lnk.charspan, 'a', 'b')

    def testChartSpanLnk(self):
        lnk = Lnk.chartspan(0, 1)
        self.assertEqual(lnk.type, Lnk.CHARTSPAN)
        self.assertEqual(lnk.data, (0,1))
        lnk = Lnk.chartspan('0', '1')
        self.assertEqual(lnk.data, (0,1))
        self.assertRaises(TypeError, Lnk.chartspan, 1)
        self.assertRaises(TypeError, Lnk.chartspan, [1])
        self.assertRaises(TypeError, Lnk.chartspan, 1, 2, 3)
        self.assertRaises(ValueError, Lnk.chartspan, 'a', 'b')

    def testTokensLnk(self):
        lnk = Lnk.tokens([1, 2, 3])
        self.assertEqual(lnk.type, Lnk.TOKENS)
        self.assertEqual(lnk.data, (1,2,3))
        lnk = Lnk.tokens(['1'])
        self.assertEqual(lnk.data, (1,))
        # empty tokens list might be invalid, but accept for now
        lnk = Lnk.tokens([])
        self.assertEqual(lnk.data, tuple())
        self.assertRaises(TypeError, Lnk.tokens, 1)
        self.assertRaises(ValueError, Lnk.tokens, ['a','b'])

    def testEdgeLnk(self):
        lnk = Lnk.edge(1)
        self.assertEqual(lnk.type, Lnk.EDGE)
        self.assertEqual(lnk.data, 1)
        lnk = Lnk.edge('1')
        self.assertEqual(lnk.data, 1)
        self.assertRaises(TypeError, Lnk.edge, None)
        self.assertRaises(TypeError, Lnk.edge, (1,))
        self.assertRaises(ValueError, Lnk.edge, 'a')


class TestLnkMixin(unittest.TestCase):
    def test_inherit(self):
        class NoLnk(LnkMixin):
            pass
        n = NoLnk()
        self.assertEqual(n.cfrom, -1)
        self.assertEqual(n.cto, -1)
        class WithNoneLnk(LnkMixin):
            def __init__(self):
                self.lnk = None
        n = WithNoneLnk()
        self.assertEqual(n.cfrom, -1)
        self.assertEqual(n.cto, -1)
        class WithNonCharspanLnk(LnkMixin):
            def __init__(self):
                self.lnk = Lnk.chartspan(0,1)
        n = WithNonCharspanLnk()
        self.assertEqual(n.cfrom, -1)
        self.assertEqual(n.cto, -1)
        class WithCharspanLnk(LnkMixin):
            def __init__(self):
                self.lnk = Lnk.charspan(0,1)
        n = WithCharspanLnk()
        self.assertEqual(n.cfrom, 0)


class TestHook(unittest.TestCase):
    def test_construct(self):
        h = Hook()
        self.assertEqual(h.ltop, None)
        self.assertEqual(h.index, None)
        self.assertEqual(h.xarg, None)
        h = Hook(ltop=MrsVariable(1, 'h'), index=MrsVariable(2, 'e'),
                 xarg=MrsVariable(3, 'x'))
        self.assertEqual(h.ltop, 'h1')
        self.assertEqual(h.index, 'e2')
        self.assertEqual(h.xarg, 'x3')


class TestArgument(unittest.TestCase):
    def test_construct(self):
        a = Argument(1, 'ARG', 'val')
        self.assertEqual(a.nodeid, 1)
        self.assertEqual(a.argname, 'ARG')
        self.assertEqual(a.value, 'val')

    def test_MrsArgument(self):
        a = Argument.mrs_argument('ARG', 'val')
        self.assertEqual(a.nodeid, None)
        self.assertEqual(a.argname, 'ARG')
        self.assertEqual(a.value, 'val')

    def test_RmrsArgument(self):
        a = Argument.rmrs_argument(MrsVariable(1, ANCHOR_SORT), 'ARG', 'val')
        self.assertEqual(a.nodeid, 1)
        self.assertEqual(a.argname, 'ARG')
        self.assertEqual(a.value, 'val')

    def test_equality(self):
        a1 = Argument(None, 'ARG', 'val')
        a2 = Argument(1, 'ARG', 'val')
        a3 = Argument(2, 'ARG', 'val')
        a4 = Argument(None, 'FOO', 'val')
        a5 = Argument(None, 'FOO', 'bar')
        self.assertEqual(a1, a1)
        self.assertEqual(a1, a2)
        self.assertNotEqual(a2, a3)
        self.assertNotEqual(a1, a4)
        self.assertNotEqual(a4, a5)

    def test_infer_type(self):
        a = Argument(None, IVARG_ROLE, MrsVariable(1, 'x'))
        self.assertEqual(a.infer_argument_type(), Argument.INTRINSIC_ARG)
        a = Argument(None, 'ARG', MrsVariable(1, 'x'))
        self.assertEqual(a.infer_argument_type(), Argument.VARIABLE_ARG)
        a = Argument(None, 'ARG', MrsVariable(1, 'h'))
        self.assertEqual(a.infer_argument_type(), Argument.HANDLE_ARG)
        # fake an Xmrs where h0 is QEQ'd and others are not
        class FakeXmrs(object):
            def get_hcons(self, var):
                if var == 'h0':
                    return 1  # any value is ok for now
                return None
        x = FakeXmrs()
        a = Argument(None, 'ARG', MrsVariable(0, 'h'))
        self.assertEqual(a.infer_argument_type(xmrs=x), Argument.HCONS_ARG)
        a = Argument(None, 'ARG', MrsVariable(1, 'h'))
        self.assertEqual(a.infer_argument_type(xmrs=x), Argument.LABEL_ARG)
        a = Argument(None, CONSTARG_ROLE, 'constant')
        self.assertEqual(a.infer_argument_type(), Argument.CONSTANT_ARG)
        a = Argument(None, 'OTHER', 'constant')
        self.assertEqual(a.infer_argument_type(), Argument.CONSTANT_ARG)


class TestLink(unittest.TestCase):
    def test_construct(self):
        self.assertRaises(TypeError, Link)
        self.assertRaises(TypeError, Link, 0)
        l = Link(0, 1)
        self.assertEqual(l.start, 0)
        self.assertEqual(l.end, 1)
        self.assertEqual(l.argname, None)
        self.assertEqual(l.post, None)
        l = Link('0', '1')
        self.assertEqual(l.start, 0)
        self.assertEqual(l.end, 1)
        self.assertEqual(l.argname, None)
        self.assertEqual(l.post, None)
        l = Link(0, 1, argname='ARG')
        self.assertEqual(l.start, 0)
        self.assertEqual(l.end, 1)
        self.assertEqual(l.argname, 'ARG')
        self.assertEqual(l.post, None)
        l = Link(0, 1, post='NEQ')
        self.assertEqual(l.start, 0)
        self.assertEqual(l.end, 1)
        self.assertEqual(l.argname, None)
        self.assertEqual(l.post, 'NEQ')
        l = Link(0, 1, argname='ARG', post='NEQ')
        self.assertEqual(l.start, 0)
        self.assertEqual(l.end, 1)
        self.assertEqual(l.argname, 'ARG')
        self.assertEqual(l.post, 'NEQ')


class TestHandleConstraint(unittest.TestCase):
    def test_construct(self):
        h1 = MrsVariable(1, 'handle')
        h2 = MrsVariable(2, 'handle')
        self.assertRaises(TypeError, HandleConstraint)
        self.assertRaises(TypeError, HandleConstraint, h1)
        self.assertRaises(TypeError, HandleConstraint, h1, QEQ)
        # planned:
        # self.assertRaises(MrsHconsException, HandleConstraint, h1, QEQ, h1)
        hc = HandleConstraint(h1, QEQ, h2)
        self.assertEqual(hc.hi, h1)
        self.assertEqual(hc.relation, QEQ)
        self.assertEqual(hc.lo, h2)
        hc = HandleConstraint(h1, LHEQ, h2)
        self.assertEqual(hc.relation, LHEQ)

    def test_equality(self):
        h1 = MrsVariable(1, 'h')
        h2 = MrsVariable(2, 'h')
        hc1 = HandleConstraint(h1, QEQ, h2)
        self.assertEqual(hc1, HandleConstraint(h1, QEQ, h2))
        self.assertNotEqual(hc1, HandleConstraint(h2, QEQ, h1))
        self.assertNotEqual(hc1, HandleConstraint(h1, LHEQ, h2))

    def test_hashable(self):
        hc1 = HandleConstraint(MrsVariable(1, 'h'), QEQ, MrsVariable(2, 'h'))
        hc2 = HandleConstraint(MrsVariable(3, 'h'), QEQ, MrsVariable(4, 'h'))
        d = {hc1:1, hc2:2}
        self.assertEqual(d[hc1], 1)
        self.assertEqual(d[hc2], 2)


class TestPred(unittest.TestCase):
    def testGpred(self):
        p = Pred.grammarpred('pron_rel')
        self.assertEqual(p.type, Pred.GRAMMARPRED)
        self.assertEqual(p.string, 'pron_rel')
        self.assertEqual(p.lemma, 'pron')
        self.assertEqual(p.pos, None)
        self.assertEqual(p.sense, None)
        p = Pred.grammarpred('udef_q_rel')
        self.assertEqual(p.string, 'udef_q_rel')
        self.assertEqual(p.lemma, 'udef')
        self.assertEqual(p.pos, 'q')
        self.assertEqual(p.sense, None)
        p = Pred.grammarpred('abc_def_ghi_rel')
        self.assertEqual(p.type, Pred.GRAMMARPRED)
        self.assertEqual(p.string, 'abc_def_ghi_rel')
        # pos must be a single character, so we get abc_def, ghi, rel
        self.assertEqual(p.lemma, 'abc_def')
        self.assertEqual(p.pos, None)
        self.assertEqual(p.sense, 'ghi')

    def testSpred(self):
        p = Pred.stringpred('_dog_n_rel')
        self.assertEqual(p.type, Pred.STRINGPRED)
        self.assertEqual(p.string, '_dog_n_rel')
        self.assertEqual(p.lemma, 'dog')
        self.assertEqual(p.pos, 'n')
        self.assertEqual(p.sense, None)
        p = Pred.stringpred('_犬_n_rel')
        self.assertEqual(p.type, Pred.STRINGPRED)
        self.assertEqual(p.string, '_犬_n_rel')
        self.assertEqual(p.lemma, '犬')
        self.assertEqual(p.pos, 'n')
        self.assertEqual(p.sense, None)
        p = Pred.stringpred('"_dog_n_1_rel"')
        self.assertEqual(p.type, Pred.STRINGPRED)
        self.assertEqual(p.string, '"_dog_n_1_rel"')
        self.assertEqual(p.lemma, 'dog')
        self.assertEqual(p.pos, 'n')
        self.assertEqual(p.sense, '1')
        #TODO: the following shouldn't throw warnings.. the code should
        # be more robust, but there should be some Warning or logging
        #self.assertRaises(ValueError, Pred.stringpred, '_dog_rel')
        #self.assertRaises(ValueError, Pred.stringpred, '_dog_n_1_2_rel')

    def testStringOrGrammarPred(self):
        p = Pred.string_or_grammar_pred('_dog_n_rel')
        self.assertEqual(p.type, Pred.STRINGPRED)
        p = Pred.string_or_grammar_pred('pron_rel')
        self.assertEqual(p.type, Pred.GRAMMARPRED)

    def testRealPred(self):
        # basic, no sense arg
        p = Pred.realpred('dog', 'n')
        self.assertEqual(p.type, Pred.REALPRED)
        self.assertEqual(p.string, '_dog_n_rel')
        self.assertEqual(p.lemma, 'dog')
        self.assertEqual(p.pos, 'n')
        self.assertEqual(p.sense, None)
        # try with arg names, unicode, and sense
        p = Pred.realpred(lemma='犬', pos='n', sense='1')
        self.assertEqual(p.type, Pred.REALPRED)
        self.assertEqual(p.string, '_犬_n_1_rel')
        self.assertEqual(p.lemma, '犬')
        self.assertEqual(p.pos, 'n')
        self.assertEqual(p.sense, '1')
        # in case sense is int, not str
        p = Pred.realpred('dog', 'n', 1)
        self.assertEqual(p.type, Pred.REALPRED)
        self.assertEqual(p.string, '_dog_n_1_rel')
        self.assertEqual(p.lemma, 'dog')
        self.assertEqual(p.pos, 'n')
        self.assertEqual(p.sense, '1')
        self.assertRaises(TypeError, Pred.realpred, lemma='dog')
        self.assertRaises(TypeError, Pred.realpred, pos='n')

    def testEq(self):
        self.assertEqual(Pred.stringpred('_dog_n_rel'),
                         Pred.realpred(lemma='dog', pos='n'))
        self.assertEqual(Pred.stringpred('_dog_n_rel'), '_dog_n_rel')
        self.assertEqual('_dog_n_rel', Pred.realpred(lemma='dog', pos='n'))
        self.assertEqual(Pred.stringpred('"_dog_n_rel"'),
                         Pred.stringpred("'_dog_n_rel'"))
        self.assertEqual(Pred.grammarpred('pron_rel'), 'pron_rel')
        self.assertNotEqual(Pred.string_or_grammar_pred('_dog_n_rel'),
                            Pred.string_or_grammar_pred('dog_n_rel'))


class TestNode(unittest.TestCase):
    def test_construct(self):
        # minimum is a nodeid and a pred
        self.assertRaises(TypeError, Node)
        self.assertRaises(TypeError, Node, 10000)
        n = Node(10000, Pred.stringpred('_dog_n_rel'))
        self.assertEqual(n.nodeid, 10000)
        self.assertEqual(n.pred, '_dog_n_rel')

    def test_sortinfo(self):
        n = Node(10000, Pred.stringpred('_dog_n_rel'))
        self.assertEqual(len(n.sortinfo), 0)
        n = Node(10000, Pred.stringpred('_dog_n_rel'),
                 sortinfo=[(CVARSORT, 'x')])
        self.assertEqual(len(n.sortinfo), 1)
        n = Node(10000, Pred.stringpred('_dog_n_rel'),
                 sortinfo=[(CVARSORT, 'x'), ('PER', '3')])
        self.assertEqual(len(n.sortinfo), 2)
        n2 = Node(10001, Pred.stringpred('_cat_n_rel'),
                  sortinfo=OrderedDict([(CVARSORT,'x'), ('PER','3')]))
        self.assertEqual(n.sortinfo, n2.sortinfo)

    def test_properties(self):
        n = Node(10000, Pred.stringpred('_dog_n_rel'))
        self.assertEqual(len(n.properties), 0)
        n = Node(10000, Pred.stringpred('_dog_n_rel'),
                 sortinfo=[(CVARSORT, 'x')])
        self.assertEqual(len(n.properties), 0)
        n = Node(10000, Pred.stringpred('_dog_n_rel'),
                 sortinfo=[(CVARSORT, 'x'), ('PER', '3')])
        self.assertEqual(len(n.properties), 1)
        n2 = Node(10001, Pred.stringpred('_unknowncat_n_rel'),
                  sortinfo=OrderedDict([(CVARSORT,'u'), ('PER','3')]))
        self.assertEqual(n.properties, n2.properties)

    def test_lnk(self):
        n = Node(10000, Pred.stringpred('_dog_n_rel'))
        self.assertEqual(n.lnk, None)
        self.assertEqual(n.cfrom, -1)
        self.assertEqual(n.cto, -1)
        n = Node(10000, Pred.stringpred('_dog_n_rel'),
                 lnk=Lnk.charspan(0,1))
        self.assertEqual(n.lnk, Lnk.charspan(0,1))
        self.assertEqual(n.cfrom, 0)
        self.assertEqual(n.cto, 1)

    def test_cvarsort(self):
        n = Node(10000, Pred.stringpred('_dog_n_rel'))
        self.assertEqual(n.cvarsort, None)
        n.cvarsort = 'x'
        self.assertEqual(n.cvarsort, 'x')
        self.assertEqual(n.sortinfo, OrderedDict([(CVARSORT, 'x')]))
        n = Node(10000, Pred.stringpred('_run_v_rel'),
                 sortinfo=OrderedDict([(CVARSORT, 'e')]))
        self.assertEqual(n.cvarsort, 'e')

    def test_get_property(self):
        n = Node(10000, Pred.stringpred('_dog_n_rel'))
        self.assertEqual(n.get_property('PER'), None)
        n = Node(10000, Pred.stringpred('_dog_n_rel'),
                 sortinfo=OrderedDict([(CVARSORT, 'x'), ('PER', '3')]))
        self.assertEqual(n.get_property('PER'), '3')


class TestElementaryPredication(unittest.TestCase):
    def test_construct(self):
        self.assertRaises(TypeError, EP)
        self.assertRaises(TypeError, EP, Pred.stringpred('_dog_n_rel'))
        e = EP(Pred.stringpred('_dog_n_rel'), MrsVariable(vid=1,sort='h'))
        self.assertEqual(e.pred, '_dog_n_rel')
        self.assertEqual(e.label, MrsVariable(vid=1, sort='h'))

    def test_anchor(self):
        e = EP(Pred.stringpred('_dog_n_rel'), MrsVariable(vid=1, sort='h'))
        self.assertEqual(e.anchor, None)
        self.assertEqual(e.nodeid, None)
        e = EP(Pred.stringpred('_dog_n_rel'), MrsVariable(vid=1, sort='h'),
               anchor=MrsVariable(vid=10000, sort=ANCHOR_SORT))
        self.assertEqual(e.anchor, MrsVariable(vid=10000, sort=ANCHOR_SORT))
        self.assertEqual(e.nodeid, 10000)

    def test_properties(self):
        p = Pred.stringpred('_dog_n_rel')
        lbl = MrsVariable(vid=1, sort='h')
        e = EP(p, lbl)
        self.assertEqual(len(e.properties), 0)
        v = MrsVariable(vid=2, sort='x', properties={'num': 'sg'})
        # properties only come from intrinsic arg
        e = EP(p, lbl, args=[Argument.mrs_argument('ARG1', v)])
        self.assertEqual(len(e.properties), 0)
        e = EP(p, lbl, args=[Argument.mrs_argument(IVARG_ROLE, v)])
        self.assertEqual(len(e.properties), 1)
        self.assertEqual(e.properties['num'], 'sg')

    def test_args(self):
        p = Pred.stringpred('_chase_v_rel')
        lbl = MrsVariable(vid=1, sort='h')
        e = EP(p, lbl)
        self.assertEqual(len(e.args), 0)
        v1 = MrsVariable(vid=2, sort='e', properties={'tense': 'pres'})
        e = EP(p, lbl, args=[Argument.mrs_argument(IVARG_ROLE, v1)])
        self.assertEqual(len(e.args), 1)
        self.assertEqual(e.arg_value(IVARG_ROLE), v1)
        v2 = MrsVariable(vid=3, sort='x', properties={'num': 'sg'})
        e = EP(p, lbl, args=[Argument.mrs_argument(IVARG_ROLE, v1),
                             Argument.mrs_argument('ARG1', v2)])
        self.assertEqual(len(e.args), 2)
        self.assertEqual(e.arg_value(IVARG_ROLE), v1)
        self.assertEqual(e.arg_value('ARG1'), v2)
