<br>

# Nait

Provides functions and classes for creating and<br>
training neural networks.

<br>

---

* Model
* Model.train
* Model.predict
* Model.mutate
* Layer
* Layer.forward
* Layer.mutate
* Neuron
* Neuron.parse
* Neuron.mutate
* Activation
* Activation.calculate
* evaluate
* save
* load

---

## Model
*class*

### Syntax

`Model(layers)` 

### Arguments

* layers `list`

---

## Model.train
*method*

### Syntax

`train(x=[], y=[], epochs=5000, rate=1, batch_size=10, sample_size=None, square_loss=True, visual=True, loss_function=None)` 

### Arguments

* x `list`
* y `list`
* epochs `int`
* rate `int / float`
* batch_size `int`
* sample_size `int`
* square_loss `bool`
* visual `bool`
* loss_function `function`

---

## Model.predict
*method*

### Syntax

`predict(inputs)`

### Arguments

* inputs `list`

---

## Model.mutate
*method*

### Syntax

`mutate(rate)`

### Arguments

* rate `int / float`

---

## Layer
*class*

### Syntax

`Layer(inputs=4, neurons=4, activation="linear")`

### Arguments

* inputs `int`
* neurons `int`
* activation `"linear" / "step" / "relu" / "tanh" / "hardmax" / "sigmoid" / "softmax" / "leaky relu"`

---

## Layer.forward
*method*

### Syntax

`forward(inputs)`

### Arguments

* inputs `list`

---

## Layer.mutate
*method*

### Syntax

`mutate(rate)`

### Arguments

* rate `int / float`

---

## Neuron
*class*

### Syntax

`Neuron(weights, bias)`

### Arguments

* weights `list`
* bias `int / float`

---

## Neuron.parse
*method*

### Syntax

`parse(inputs)`

### Arguments

* inputs `list`

---

## Neuron.mutate
*method*

### Syntax

`mutate(rate)`

### Arguments

* rate `int / float`

---

## Activation
*class*

### Syntax

`Activation(function)`

### Arguments

* function `"linear" / "step" / "relu" / "tanh" / "hardmax" / "sigmoid" / "softmax" / "leaky relu"`

---

## Activation.calculate
*method*

### Syntax

`calculate(x)`

### Arguments

* x `int / float`

---

## evaluate
*function*

### Syntax

`evaluate(network, x, y)`

### Arguments

* network `Model`
* x `list`
* y `list`

---

## save
*function*

### Syntax

`save(model, path)`

### Arguments

* model `Model`
* path `str`

---

## load
*function*

### Syntax

`load(path)`

### Arguments

* path `str`

---

<br>

# Changelog - Nait 3.0.5

---

* Renamed Network to Model
* Added square loss

---

<br>