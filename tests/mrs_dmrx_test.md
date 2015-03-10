
# Unit tests for the `dmrx` module

To run, do this at the command prompt:

    $ python3 -m doctest tests/mrs_dmrx_test.md

Note: nothing will be shown if tests pass. You can add a verbose flag
(`-v`) to see all results.

## Loading the `dmrx` module

The `dmrx` module is a library of functions, not a script, so import it:

```python
>>> from delphin.mrs import dmrx

```

## Parsing

"It rains"

```python
>>> m1 = next(dmrx.loads('''<dmrs-list>
... <dmrs cfrom="-1" cto="-1">
... <node cfrom="3" cto="9" nodeid="10000">
...   <realpred lemma="rain" pos="v" sense="1" />
...   <sortinfo cvarsort="e" mood="indicative" perf="-" prog="-" sf="prop" tense="pres" />
... </node>
... <link from="0" to="10000"><rargname /><post>H</post></link>
... </dmrs>
... </dmrs-list>'''))
>>> # variables are constructed
>>> m1.ltop  # doctest: +ELLIPSIS
<MrsVariable object (h...>
>>> len(m1.nodes)
1
>>> m1.nodes[0].pred  # doctest: +ELLIPSIS
<Pred object _rain_v_1_rel ...>
>>> sorted(m1.nodes[0].sortinfo.items())
[('cvarsort', 'e'), ('mood', 'indicative'), ('perf', '-'), ('prog', '-'), ('sf', 'prop'), ('tense', 'pres')]
>>> len(m1.links)
1
>>> m1.links[0]  # doctest: +ELLIPSIS
<Link object (#0 :/H> #10000) at ...>

```

"Abrams sleeps"

```python
>>> m2 = next(dmrx.loads('''<dmrs-list>
... <dmrs cfrom="-1" cto="-1">
... <node cfrom="0" cto="6" nodeid="10000"><gpred>proper_q_rel</gpred><sortinfo /></node>
... <node carg="&quot;Abrams&quot;" cfrom="0" cto="6" nodeid="10001"><gpred>named_rel</gpred><sortinfo cvarsort="x" ind="+" num="sg" pers="3" /></node>
... <node cfrom="7" cto="14" nodeid="10002"><realpred lemma="sleep" pos="v" sense="1" /><sortinfo cvarsort="e" mood="indicative" perf="-" prog="-" sf="prop" tense="pres" /></node>
... <link from="0" to="10002"><rargname /><post>H</post></link>
... <link from="10000" to="10001"><rargname>RSTR</rargname><post>H</post></link>
... <link from="10002" to="10001"><rargname>ARG1</rargname><post>NEQ</post></link>
... </dmrs>
... </dmrs-list>'''))
>>> len(m2.nodes)
3
>>> m2.nodes[0].pred  # doctest: +ELLIPSIS
<Pred object proper_q_rel ...>
>>> m2.nodes[1].pred  # doctest: +ELLIPSIS
<Pred object named_rel ...>
>>> sorted(m2.nodes[1].sortinfo.items())
[('cvarsort', 'x'), ('ind', '+'), ('num', 'sg'), ('pers', '3')]
>>> m2.nodes[2].pred  # doctest: +ELLIPSIS
<Pred object _sleep_v_1_rel ...>
>>> sorted(m2.nodes[2].sortinfo.items())
[('cvarsort', 'e'), ('mood', 'indicative'), ('perf', '-'), ('prog', '-'), ('sf', 'prop'), ('tense', 'pres')]
>>> len(m2.links)
3
>>> m2.links[0]  # doctest: +ELLIPSIS
<Link object (#0 :/H> #10002) at ...>
>>> m2.links[1]  # doctest: +ELLIPSIS
<Link object (#10000 :RSTR/H> #10001) at ...>
>>> m2.links[2]  # doctest: +ELLIPSIS
<Link object (#10002 :ARG1/NEQ> #10001) at ...>

```

## Serialization

The default prints everything on one line.

```python
>>> print(dmrx.dumps([m1]))  # doctest: +ELLIPSIS
<dmrs-list><dmrs cfrom="-1" cto="-1"...><node cfrom="3" cto="9" nodeid="10000"><realpred lemma="rain" pos="v" sense="1" /><sortinfo cvarsort="e" mood="indicative" perf="-" prog="-" sf="prop" tense="pres" /></node><link from="0" to="10000"><rargname /><post>H</post></link></dmrs></dmrs-list>

```

Using the `pretty_print` parameter adds newlines.

```python
>>> print(dmrx.dumps([m1], pretty_print=True))  # doctest: +ELLIPSIS
<dmrs-list>
<dmrs cfrom="-1" cto="-1">
<node cfrom="3" cto="9" nodeid="10000"><realpred lemma="rain" pos="v" sense="1" /><sortinfo cvarsort="e" mood="indicative" perf="-" prog="-" sf="prop" tense="pres" /></node>
<link from="0" to="10000"><rargname /><post>H</post></link>
</dmrs>
</dmrs-list>

```

```python
>>> print(dmrx.dumps([m2], pretty_print=True))  # doctest: +ELLIPSIS
<dmrs-list>
<dmrs cfrom="-1" cto="-1">
<node cfrom="0" cto="6" nodeid="10000"><gpred>proper_q_rel</gpred><sortinfo /></node>
<node carg="&quot;Abrams&quot;" cfrom="0" cto="6" nodeid="10001"><gpred>named_rel</gpred><sortinfo cvarsort="x" ind="+" num="sg" pers="3" /></node>
<node cfrom="7" cto="14" nodeid="10002"><realpred lemma="sleep" pos="v" sense="1" /><sortinfo cvarsort="e" mood="indicative" perf="-" prog="-" sf="prop" tense="pres" /></node>
<link from="0" to="10002"><rargname /><post>H</post></link>
<link from="10000" to="10001"><rargname>RSTR</rargname><post>H</post></link>
<link from="10002" to="10001"><rargname>ARG1</rargname><post>NEQ</post></link>
</dmrs>
</dmrs-list>

```
