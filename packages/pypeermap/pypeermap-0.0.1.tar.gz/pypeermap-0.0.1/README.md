# pypeermap

pypeermap is a simple python tool for obtaining all the IP addresses on your local network. 


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pypeermap.

<div align="center">
  <a href="https://github.com/nalsadi/pypeermap">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
</div>


```bash
pip install pypeermap
```

## Usage

```python
import pypeermap

# returns your IP
ip = pypeermap.get_my_ip()

# set scan range
scan_range = pypeermap.perform_scan(ip,'0/24')

# returns list of client names and IP's
pypeermap.get_ip_list(scan_range)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)