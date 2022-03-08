# Scry

Build your vision.

## What is Scry

Scry is a language that I started writing after being inspired by
[Tsoding's Porth](https://gitlab.com/tsoding/porth), and writing my
first assembly programs.

It aims to be a statically typed stack based language but maybe with
some cool modern features? We will see how it goes.

## How to run Scry

Currently this is very early development, not quite ready for use.
Nonetheless, you can clone this repo and use it to run your own Scry
programs.

Scry requires as least Python version 3.8.

```bash
pip install git+https://github.com/Jonxslays/Scry.git
```

After that running your Scry program is as simple as:

```bash
python -m scry path/to/script.scry
```

## Example Scry program

```scry
push    int     100
push    int     50
add
print

var     string  name
move    name    "Jonxslays"
push    string  "My name is ${name}"
drop    name
print
```

```bash
# output
150
My name is Jonxslays
```

## License

Scry is license under the
[MIT License](https://github.com/Jonxslays/Scry/blob/master/LICENSE)
