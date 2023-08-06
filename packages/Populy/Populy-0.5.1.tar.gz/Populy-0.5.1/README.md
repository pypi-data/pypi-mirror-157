# Populy

Populy es un paquete de Python que permite llevar a cabo una simulación de tipo *forward evolution*. 
El paquete consta varios módulos con sus respectivas clases que permiten llevar a cabo la creación de 0 de una población, la evolucion de ésta y la obtención de tablas y gráficos del resultado de la evolución.


## Instalación
Es posible acceder mediante [github](https://github.com/R-mario/populy) o con el instalador de paquetes [pip](https://pip.pypa.io/en/stable/).
```cmd
pip install Populy
```
## Uso
```python
from populy.population import Population

# crea un objeto de la clase Population
pop = Population(size=1000, 
                ploidy=2)

# genera individuos en la población
pop.generateIndividuals()

# hace evolucionar a la Población
pop.evolvePop(gens=200)
```
Para una explicación más detallada consultar el cuaderno [Guía de uso](Guia de uso.ipynb)

## Mybinder
Si quieres acceder a una serie de *Jupyter notebooks* orientadas a la iniciación a la programación interactiva y la simulación evolutiva pulsa el siguiente botón.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/R-mario/Populy-notebooks/HEAD)

## Licencia
[MIT](https://choosealicense.com/licenses/mit/)