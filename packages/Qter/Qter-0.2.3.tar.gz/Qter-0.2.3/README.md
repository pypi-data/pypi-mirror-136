# Qter
This is a package for a quantum simulator. This package can simulate errors similar to the real quantum device, here error comes with each gate, and similar to the actual device it also uses swap operation if the two-qubit gate is applied between two far available qubits. In this version all qubits are assumed to be straight but soon in the next version we can provide flexibility to chose devise architecture.
### This package makes use of the following module:
1. numpy
1. cmath
1. math
1. random

### How to install Qter
you can just pip install Qter by typing:
```
pip install Qter
```
#### To import Qter 
```
import Qter as Qter
```  
### To Import quantum gate:
To use this quantum simulator you have to first import a quantum gate and save it in the local variable list of quantum gate currently available is:
1. X = Pauli-X
1. I = Identity
1. Y = Pauli-Y
1. Z = Pauli-Z
1. H = Hadamard
1. T = T-gate
1. CX = controlled Pauli-X
1. SW = Swap gate
1. S = S-gate

Code to import Quantum Gate :

```
    H = Qter.H
    Y = Qter.Y
    X = Qter.X
    CX = Qter.CX
```
### To run the simulator
To run this simulator you have to import run and rub it with 6 variables. 
```
x, y = Qter.run(cir, n, count, error, Transpiler)
````
1. **Cir** is an array containing information of circuit as:
```
  cir =  [[H, 0], [H, 2], [H, 3], [X, 3], [CX, [1, 3]], [X, 3], [X, 1], [CX, [1, 3]], [CX, [4, 3]], [CX, [0, 3]]]
```
    Here each gate is applied as a list where the first position is for the name of the gate and the second position is for the position of that gate. If the type of gate is a two-qubit gate then the position of the gate is passed under a list. 
1. **n** is the number of qubits.
1. **Count** is the number of shots or samples you want to take.
1. **Error** is a boolean variable for error. This can take true if you want to error in the circuit if you did not want an Error in your circuit you can just pass False in it.
1. **Transpiler** is a boolean variable for Transpilation of the circuit. This can take true if you want to transpile your circuit, if you did not want to transpile your circuit you can just pass False in it.
1. **err** is a variable for the value of the average error you want.
### This run function returns you two arrays 
* In the first array, each element contains two values, probability, and its corresponding quantum state.
* In the second array, each element contains two values, count, and its corresponding quantum state.
### To Draw your Circuit
the code to draw your circuit
```
from Qter import draw as draw
draw(cir,n) 

```
### To plot Result:
```
from Qter import plot as plot
y=[5,2]
plot(x,y)
```
Here y is size of image 