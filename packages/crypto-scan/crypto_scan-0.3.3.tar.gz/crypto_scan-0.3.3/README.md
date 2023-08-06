# Build and update package
1. `rm -rf ./dist ./build`
2. Update version in `setup.py`
3. `python setup.py sdist bdist_wheel`
4. `twine check dist/*` to check error
4. `twine upload dist/*` to deploy pkg


# Use below command to update the latest version
`pip install --no-cache-dir --upgrade crypto-scan`


# Example
```python
from crypto_scan.configs import ETH_CHAIN
from crypto_scan.scan import Scan

scan = Scan(ETH_CHAIN, env['ETHSCAN_API_KEY'])
scan.get_contract(addr)
scan.get_all_trans(addr, startblock=qr.max_block_num)
```