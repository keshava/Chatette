# Syntax specifications

## 1. Overview

*Chatette* is a Python script that can generate an input file for *Rasa NLU* from a file containing templates written in a Domain Specific Language. This document describes this DSL.

This DSL is a superset of *Chatito*'s DSL, described [here](https://github.com/rodrigopivi/Chatito/blob/master/spec.md).

Here is an example of such a template file.

```
; This template file defines examples of sentences people would say to introduce themselves
%[&introduce](2)
    ~[hi] ~[i am] @[name][, nice to meet you?]
    ~[hi] my name{'s/ is} @[name]

~[hi]
    hi
    hello
    howdy

~[i am]
    {i/I} am
    {i/I}'m

@[name]
    John
    Robert = Robert
    Bob = Robert
```

This will generate a file containing data such as the one shown hereafter. This data is made up of examples sentences which are labelled as having a certain intent and optionnally contain one or several entities corresponding to the value of a slot. Read *Rasa NLU*'s data format [here](http://rasa.com/docs/nlu/0.13.1/dataformat/) for more information.
```json
{
  "rasa_nlu_data": {
    "common_examples": [
      {
        "entities": [
          {
            "end": 13,
            "entity": "name",
            "start": 7,
            "value": "Robert"
          }
        ],
        "intent": "introduce",
        "text": "Hi i'm Robert"
      },
      {
        "entities": [
          {
            "end": 19,
            "entity": "name",
            "start": 16,
            "value": "Robert"
          }
        ],
        "intent": "introduce",
        "text": "Howdy my name's Bob"
      }
    ],
    "entity_synonyms": [
      {
        "synonyms": [
          "Robert",
          "Bob"
        ],
        "value": "Robert"
      }
    ],
    "regex_features": []
  }
}
```

Template files can be encoded in any charset, while JSON files will always be UTF-8 encoded.

## 2. Language syntax

As visible in the example shown above, a file is composed of several definitions, made up of a declaration and a set of rules, one rule per line.
The declaration is the unindented part, while the set of rules are indented. The indentation must be coherent inside a rule, i.e. each rule in a definition must be indented in the same way. However, different indentations may be used for different definitions.

Everything that follows a semi-colon (`;`) is considered to be a comment and is thus ignored.

We show here a skeleton of this.
```
; Whole line comment
DECLARATION1
    RULE1
    RULE2
DECLARATION2  ; Other comment
  RULE1
  RULE2
```

Semi-colons are not the only characters with a special meaning in the DSL. If you want to use special characters as normal characters, they should be escaped by prepending a backslash (`\`) to them. This is true anywhere in the template documents, except in comments.

Here is an exhaustive list of characters which should be escaped:
|   |   |
|---|---|
| Semi-colon | `;` |
| Percent | `%` |
| Tilde | `~` |
| At | `@` |
| Question | mark `?` |
| Hashtag | `#` |
| Slash | `/` |
| Dollar sign `$`
| Ampersand | `&` |
| Square brackets | `[` and `]` |
| Curly braces | `{` and `}` |
| Equal symbol | `=` |
| Pipe | `|` |
| Backslash | `\` |

Note that not escaping these characters might not be problematic in certain cases, but it is more prudent to do it in all cases. Escaping a character outside of this list will simply be ignored by the parser which will act as if there was no backslash there.

### 2.1. Declarations

As we said, each definition starts with a declaration which is made in the following way: a special character to distinguish the different types of definitions, followed by an identifier in-between square brackets.
Identifier can be made of any characters, including whitespaces. To use characters from the previous table in identifier, escape them. The only forbidden characters are the line feed (`\n`) and carriage return (`\r`).

The identifier of a definition will be the way to reference this definition elsewhere in the template files. Note that a declaration doesn't have to be done before being referenced and doesn't even have to be done in the same file as its references, as long as the declaration exists somewhere.

Some modifiers may be added to declarations to affect what they will generate. Those modifications are made using special characters, put besides the identifier (inside the brackets).
Three modifiers for declarations are currently supported:

- Case generation (in short *casegen*) using `&`

  If this modifier is used, everything that is generated by this definition will randomly begin with an uppercase or lowercase letter. The ampersand must be the first thing inside the square brackets, for example:
  ```
  ~[&declaration]
    ...
  ```

- Variation naming using `#` and a variation identifier

   This modifier can be used to differentiate different forms of the same declaration. You can thus make several definitions for the same identifier and use them in different places. For example, you might want to make a singular and a plural variation for a single definition, as shown next:
   ```
   ~[def#singular]
    ...
   ~[def#plural]
    ...
   ```

   The hashtag must be placed after the declaration name and the variation identifier must be placed after the `#`. An empty variation name is not allowed.

 - Argument support using `$` and an argument name

    This modifier allows to tell that certain parts of the rules can be replaced by a provided word or group of word. This is very useful when you have two definitions that would be the same if there wasn't a certain word inside that was used.

    The dollar sign must be placed after the declaration name and the identifier for the argument has to be placed after that. As for any other identifiers, arguments identifiers can be made up of any characters except line breaks (and special characters should be escaped).

    Inside rules, you would reference the argument simply by writing it, prepended by a dollar sign.
    For example:
    ```
    ~[greet$NAME]
        hello $NAME
    ```