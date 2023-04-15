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

## Úloha 2 - Hash
* Napište program, který nalezne libovolnou zprávu, jejíž hash (SHA-384) začíná zleva na posloupnost nulových bitů:
  * Počet nulových bitů je zadán celým číslem jako parametr na příkazové řádce.
  * Pořadí bitů je big-endian: Bajt 0 od MSB do LSB, Bajt 1 od MSB do LSB, …, poslední bajt od MSB do LSB.
  * Program nemá žádné další vstupy, jen výše zmíněný parametr při volání na příkazové řádce.
    * Nutná kontrola tohoto parametru (zda je smysluplný)
  * Výstupem jsou dva hexadecimální řetězce oddělené mezerou:
    1. Data, pro které byla nalezena příslušná hash
    2. Hash
  * Návratové hodnoty:
    * 0 pokud je vše v pořádku
    * != 0 pokud nastala chyba
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

## Úloha 3 - Bloková šifra
* Základní popis programu s popisem TGA formátu viz cvičení.
* Jako šifru zvolte 128b variantu AES a používejte PKCS padding (v openssl je nastaven jako default)
* Program se bude volat s následujícími přepínači/argumenty (dodržte pořadí, nebo ho pevně nevyžadujte):
  * -e / -d šifrování/dešifrování
  * ecb / cbc operační mód ecb/cbc
  * název vstupního souboru (zadává se celý název souboru - včetně přípony)

###### Ukázka 1. Příklad volání
```
$ ./task3 -e ecb homer-simpson.tga

$ ./task3 -d ecb homer-simpson_ecb.tga
```
* Výstup:
  * V případě chyby žádný výstupní soubor
  * Zašifrovaný soubor s příponou _ecb.tga/_cbc.tga (celý název je tedy např. '(původní_jméno)_ecb.tga')
  * Dešifrovaný soubor s příponou _dec.tga (celý název je tedy např. '(původní_jméno)_ecb_dec.tga')

###### Ukázka 2. Příklad názvů
```
homer-simpson.tga -> (zašifrujeme v CBC módu) -> homer-simpson_cbc.tga
homer-simpson_cbc.tga -> (dešifrujeme) -> homer-simpson_cbc_dec.tga
```
* Návratové hodnoty:
  * 0 vše OK
  * !=0 chyba
* Při zpracování souboru nesmíte načítat celý obrázek do paměti a ten pak dále zpracovávat, ale dělejte to po částech. Cílem je vyzkoušet si práci postupného zpracování pomocí funkce EncryptUpdate. Můžete si např. zadefinovat, že budete zpracovávat části po 1KB.
* Hlídejte si zpracování hlavičky TGA souboru, kdykoliv něco nesedí, program ukončete s chybou.
  * Např. pozor na správnost načtení samotné hlavičky TGA souboru
  * Začátek mapy barev za koncem souboru
  * …
* Vždy porovnávejte původní a dešifrovaný soubor, jestli je stejný! (např. diffem)
* Kromě samotného programu odevzdejte popis rozdílu mezi ECB a CBC u zašifrovaných souborů (ve vztahu k původním).

## Úloha 4 - Asymetrická kryptografie
* Program se bude volat s následujícími přepínači/argumenty (dodržte pořadí, nebo ho pevně nevyžadujte):
  * -e šifrování
  * -d dešifrování
  * cesta k veřejnému/soukromému klíči
  * soubor k šifrování/dešifrování
  * výstupní soubor (šifrovaný/dešifrovaný soubor)

###### Ukázka 1. Příklad volání
```
$ ./task4 -e pubkey.pem file encrypted_file

$ ./task4 -d privkey.pem encrypted_file decrypted_file
```
* Výstup:
  * V případě chyby žádný výstupní soubor
  * Zašifrovaný/dešifrovaný soubor
* Návratové hodnoty:
  * 0 vše OK
  * !=0 chyba
* Hlídejte správnost načtení veřejného/soukromého klíče
* Kontrolujte návratové hodnoty fcí, které provádějí kryptografické operace
* Při šifrování souboru je potřeba si vytvořit vhodnou vlastní hlavičku zašifrovaného souboru, pomocí které pak budete moct dešifrovat.
  * Tzn. všechny informace nutné pro dešifrování (klíč pro symetrickou šifru, IV, …​)
* Vždy porovnávejte původní a dešifrovaný soubor, jestli je stejný! (např. diffem)
* Inicializujte generátor náhodných čísel!
* Než se mi úkol budete pokoušet odevzdat, tak váš program otestujte!
  * Váš program musí být schopen pracovat s RSA klíči různé velikosti, ne jen pevně dané délky (např 2048b jak je v ukázce na eduxu)
