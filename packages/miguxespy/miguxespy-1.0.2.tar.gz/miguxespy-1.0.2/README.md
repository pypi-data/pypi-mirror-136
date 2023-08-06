
Miguxes\_py
===========
<img alt="Twitter Follow" src="https://img.shields.io/twitter/follow/matheuszeen?style=for-the-badge">
<img alt="PyPI" src="https://img.shields.io/pypi/v/miguxespy?style=for-the-badge">

`miguxes_py` é um modulo que traduz português para as seguintes
variações de miguxês:

- arcaico;
- moderno;
- NEO-miguxês.

A principal função do módulo é a função `miguxar(texto, dialeto)`, que
recebe um texto para ser transformado e um dialeto.

Instalação
----------

Pode ser instalada através do pip, utilizando o comando:

> `pip install miguxes_py`

Exemplo de uso:

```python
from miguxes_py.miguxes import miguxar
from miguxes_py.dialetos import DialetoMiguxes

if __name__ == "__main__":
    print(miguxar("Você acha engraçado tirar screenshots dos NFTs das pessoas, hein?""", DialetoMiguxes.MIGUXES_MODERNO))
```

A saída seria:

    vc axa engrassadu tirah screenxots dus nfts das pessoas... hein??!?!

Inspirado no projeto de Aurelio Jargas, que pode ser encontrado em: <https://aurelio.net/coisinha/miguxeitor>
------------------------------------------------------------------------
