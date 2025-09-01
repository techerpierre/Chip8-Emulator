## How to build:

```bash
    make all
```

/*
Voici les grandes étapes classiques de la compilation d’un langage vers du code exécutable :

1️⃣ Analyse lexicale (Lexer / Scanner)

On prend le texte source et on le découpe en tokens (unités lexicales).

Exemple : LD V0, 10 → ["LD", "V0", ",", "10"].

But : transformer une chaîne de caractères en un flux compréhensible par l’ordinateur.

2️⃣ Analyse syntaxique (Parser)

À partir des tokens, on construit un arbre syntaxique abstrait (AST).

Exemple : LD V0, 10 → LoadRegister(register=V0, value=10).

Vérifie si la syntaxe est correcte selon la grammaire du langage.

3️⃣ Analyse sémantique

Vérifie que le code a un sens logique :

Les variables sont déclarées avant d’être utilisées.

Les types correspondent (int vs float).

Les registres/champs sont valides pour CHIP-8.

Ajoute souvent des annotations sur l’AST.

4️⃣ Génération de code intermédiaire (optionnel)

Certains compilateurs produisent d’abord un code intermédiaire (ex. bytecode).

Pour ton CHIP-8, ça pourrait être directement les opcodes.

5️⃣ Optimisation

Améliore le code généré :

Supprimer les instructions inutiles.

Fusionner des opérations.

Pour un petit CPU comme CHIP-8, cette étape est souvent minimale.

6️⃣ Génération du code final

Transforme l’AST ou le code intermédiaire en code exécutable ou ROM binaire.

Pour CHIP-8, ça signifie créer un fichier .ch8 contenant les instructions en binaire.

7️⃣ Émission / écriture

Le code final est écrit dans un fichier, prêt à être exécuté par l’émulateur.
*/

## Instructions list:

| Token       | Description                | Exemple                                       |
| ----------- | -------------------------- | --------------------------------------------- |
| `CLS`       | Clear screen               | `CLS`                                         |
| `RET`       | Retour de sous‑routine     | `RET`                                         |
| `JP`        | Jump                       | `JP 0x200`                                    |
| `CALL`      | Appel de sous‑routine      | `CALL 0x300`                                  |
| `SE`        | Skip if equal              | `SE V0, 0x0A` ou `SE V0, V1`                  |
| `SNE`       | Skip if not equal          | `SNE V0, 0x0A` ou `SNE V0, V1`                |
| `LD`        | Load                       | `LD V0, 0x10` ou `LD I, 0x210` ou `LD V0, V1` |
| `ADD`       | Addition                   | `ADD V0, 0x05` ou `ADD I, V0`                 |
| `OR`        | Bitwise OR                 | `OR V0, V1`                                   |
| `AND`       | Bitwise AND                | `AND V0, V1`                                  |
| `XOR`       | Bitwise XOR                | `XOR V0, V1`                                  |
| `SUB`       | Subtract                   | `SUB V0, V1`                                  |
| `SHR`       | Shift right                | `SHR V0` (ou `V0, V1` selon implémentation)   |
| `SUBN`      | Reverse subtract           | `SUBN V0, V1`                                 |
| `SHL`       | Shift left                 | `SHL V0` (ou `V0, V1`)                        |
| `RND`       | Random number              | `RND V0, 0xFF`                                |
| `DRW`       | Draw sprite                | `DRW V0, V1, 5`                               |
| `SKP`       | Skip if key pressed        | `SKP V0`                                      |
| `SKNP`      | Skip if key not pressed    | `SKNP V0`                                     |
| `LD_DT`     | Load delay timer           | `LD V0, DT`                                   |
| `LD_K`      | Wait key press             | `LD V0, K`                                    |
| `LD_ST`     | Set delay timer            | `LD DT, V0`                                   |
| `LD_SOUND`  | Set sound timer            | `LD ST, V0`                                   |
| `ADD_I`     | Add to index               | `ADD I, V0`                                   |
| `LD_F`      | Load font sprite           | `LD F, V0`                                    |
| `LD_B`      | Store BCD                  | `LD B, V0`                                    |
| `LD_I_TO_V` | Store registers in memory  | `LD [I], V0`                                  |
| `LD_V_TO_I` | Read registers from memory | `LD V0, [I]`                                  |

*/

/*
    0x00EE
    0x1000
    0x2000
    0xB000
*/