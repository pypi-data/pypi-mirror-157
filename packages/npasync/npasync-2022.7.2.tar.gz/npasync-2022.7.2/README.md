# npasync

**Description**:  
A wrapper package for python asynchronous programming

**Author**: Nopporn Phantawee

### Version note
2022.7.001: First release
2022.7.002: Updated Readme.md

### Installation
`pip install npasync==2022.7.1`

### Usage sample
```python
# create a Python file with the content below.
from npasync import NPAsync

if __name__ == "__main__":
    n = NPAsync()
    base_url = "https://pokeapi.co/api/v2/pokemon/{}"
    urls = [base_url.format(x) for x in range(1, 21)]
    output = n.request_get(urls=urls)
    print(f"Total output is: {len(output)}")
    print(f"Showing the name of each Pokemon(parsed)")
    for item in output:
        print(f"{item[0]['name']}")
```
