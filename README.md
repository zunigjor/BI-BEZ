# BI-BEZ

| Úloha                        | Body |
|------------------------------|------|
| 1 - Mathematica              | 2/2  |
| 2 - Hash                     | 3/3  |
| 3 - Bloková šifra            | 5/5  |
| 4 - Asymetrická kryptografie | 5/5  |

## Úloha 1 - Mathematica
1. Stáhněte si pracovní soubor bez-lab1.nb pro aplikaci Mathematica.
2. Spusťte Mathematiku a otevřete pracovní soubor.
3. Připomeňte si ovládání programu Mathematica (2. slide)
4. Podle návodu v jednotlivých slidech samostatně vypracujte příklady označené „Úkol n:“.
5. U afinní šifry: Kolik existuje unikátních klíčů? Porovnejte s Caesarovou šifrou. Jak byste mohli prostor klíčů ještě zvětšit?
6. U transpoziční šifry je očividně slabým místem způsob doplnění zprávy (padding). Jak byste toto slabé místo ošetřili?

* Napište program, který nalezne libovolnou zprávu, jejíž hash (SHA-384) začíná zleva na posloupnost nulových bitů:
** Počet nulových bitů je zadán celým číslem jako parametr na příkazové řádce.
** Pořadí bitů je big-endian: Bajt 0 od MSB do LSB, Bajt 1 od MSB do LSB, …, poslední bajt od MSB do LSB.
** Program nemá žádné další vstupy, jen výše zmíněný parametr při volání na příkazové řádce.
*** Nutná kontrola tohoto parametru (zda je smysluplný)
** Výstupem jsou dva hexadecimální řetězce oddělené mezerou:
*** Data, pro které byla nalezena příslušná hash
*** Hash
** Návratové hodnoty:
*** 0 pokud je vše v pořádku
*** != 0 pokud nastala chyba
* V případě chyby můžete vypisovat hlášky, důležité ale je, abyste dodrželi, že váš program nevrací nulu.

###### Ukázka 1. Příklad
```
$ ./task2 4
d783ce4fe9c555243034fb87dace4f45 074425fa74e1af9e6c1dbd5cc98da79dfb0f7649a9cf3824214a8a43a8c01f29f76cf2fd4d8da135bd6945c9663fccd9

$ ./task2 2
76c522c2e938840100ac0269e293de60 2c307afeb491d5d68adcfc9cc5cb18f747c35fc46a162339eb8746d7872c1df54f8e757dce3e02b76161e7823283205b

$ ./task2 11
bf1432c8bf66dc0952219d3555de6dbe 00136e6f33af14eb5a139f302194a0f235946813096084723c1da3adbf32df98efd583eeaa56d796752d7f61b2de8119
```
