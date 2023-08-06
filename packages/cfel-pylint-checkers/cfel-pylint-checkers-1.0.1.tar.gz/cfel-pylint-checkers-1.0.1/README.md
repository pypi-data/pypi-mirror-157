# cfel-pylint-checkers

## Installation

Just `pip install cfel-pylint-checkers` should suffice. Then you can enable the appropriate checkers as plugins by editing your `.pylintrc` file, extending the `load-plugins` line. For example:

```
load-plugins=cfel_pylint_checkers.no_direct_dict_access
```

## Checkers
### `no-direct-dict-access`

This disallows the use of dictionary access using the `[]` operator *for reading*. Meaning, this is no longer allowed:

```python
mydict = { "foo": 3 }

print(mydict["bar"])
```

As you can see, this code produces an error, since we’re accessing `"bar"` but the `mydict` dictionary only contains the key `"foo"`. You have to use `.get` to make this safe:

```python
mydict = { "foo": 3 }

print(mydict.get("bar"))
```

Which produces `None` if the key doesn’t exist. You can even specify a default value:

```python
mydict = { "foo": 3 }

print(mydict.get("bar", 0))
```

Mutating use of `operator[]` is, of course, still possible. This is *fine*:

```python
mydict = { "foo": 3 }

mydict["bar"] = 4
```
