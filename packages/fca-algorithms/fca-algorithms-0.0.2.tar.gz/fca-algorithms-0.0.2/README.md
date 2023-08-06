# FCA utils

Module for FCA basics such as retrieving concepts, drawing a hasse diagram, etc

## Getting formal concepts

```python
from base_models import Context
from get_lattice import Inclose

c = Context(O, A, I)
concepts = Inclose().get_concepts(c)
```

## Getting association rules


```python
from base_models import Context
from get_lattice import Inclose

c = Context(O, A, I)
Inclose().get_association_rules(c, min_support=0.4, min_confidence=1)
```


## Drawing hasse diagram


```python
from get_lattice import Inclose
from plot.plot import plot_from_hasse
from base_models import Context


c = Context(O, A, I)
hasse_lattice, concepts = Inclose().get_lattice(c)
plot_from_hasse(hasse_lattice, concepts)
```



# TODO

- Make algorithms to be able to work with streams (big files)

