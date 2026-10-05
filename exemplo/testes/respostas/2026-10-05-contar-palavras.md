# Me ensina a contar palavras de um texto

### Pronto
1. `contar("a b a")` devolve `{"a": 2, "b": 1}`.
2. Texto vazio devolve `{}`.

Suposição (R6): "palavra" = pedaço separado por espaço; não trato pontuação nesta versão.

### Menor versão
```python
def contar(texto):
    r = {}
    for p in texto.split():
        r[p] = r.get(p, 0) + 1
    return r
```

### Previsão
`contar("a b a")` → `{'a': 2, 'b': 1}`; `contar("")` → `{}`.

### Saída real
```
$ python3 -c "from contar import contar; print(contar('a b a'), contar(''))"
{'a': 2, 'b': 1} {}
```
Bateu com a previsão (R3, R4).

### Versão quebrada
Com `texto.split(" ")`, dois espaços seguidos geram uma "palavra" vazia:
```
$ python3 -c "print('a  b'.split(' '))"
['a', '', 'b']
```
Causa: `split(" ")` não junta separadores repetidos. Corrigido voltando para `split()` (R5).

### Relatório
| passo | rodou | saiu | regra |
|---|---|---|---|
| menor versão | `contar('a b a')` | `{'a': 2, 'b': 1}` | R2 |
| previsão × saída | o mesmo | bateu | R3, R4 |
| versão quebrada | `'a  b'.split(' ')` | `['a', '', 'b']` | R5 |
