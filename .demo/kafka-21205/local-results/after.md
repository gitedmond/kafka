## KAFKA-21205 live Markdown demonstration

This fork-only PR demonstrates the original formatter and the fix in
[apache/kafka#23691](https://github.com/apache/kafka/pull/23691).

### Indented list

Example list:
 - first item
 - second item

### Code block with a blank line

```python
def example():
    first = 1

    second = 2
    return first + second

```

### Long indented code line

```python
def long_example():
    result = call_with_many_arguments(first_argument, second_argument, third_argument, fourth_argument, fifth_argument)
    return result
```

### Verification

The demonstration restores this exact input between the original and fixed
runs. The fixed formatter must preserve the full description byte for byte,
and a second fixed run must leave it unchanged. See the workflow and the
files in `.demo/kafka-21205/` for reproducible evidence and source versions.
