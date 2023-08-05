# File Storage
- local FS ftw (data locality)
- backups!!
  - https://borgbackup.readthedocs.io/en/stable/
  - something else (see distributed)?
- distributed?
  - Perkeep? https://perkeep.org/doc/compare
  - IPFS?



# IPFS
- looks active

[^ipfs-priv-enc]: https://docs.ipfs.io/concepts/privacy-and-encryption/
[^ipfs-content-addressing]: https://docs.ipfs.io/concepts/content-addressing/

## Vocabulary
- PeerID = Node ID
- CID = Content Identifier (think object UUID) [^ipfs-priv-enc]
- Distributed Hash Table (DHT) for PeerID and CID lookups (public) [^ipfs-content-addressing]

## Privacy
Options [^ipfs-priv-enc]:

- disabling reproviding
- encrypting sensitive content
  - needs a different tool
  - https://docs.ipfs.io/concepts/privacy-and-encryption/#encryption-based-projects-using-ipfs
- running a private IPFS network
  - https://docs.ipfs.io/concepts/privacy-and-encryption/#creating-a-private-network


## DHT rate limit?
IPFS seems to generate a lot of traffic when DHT client (`--routing=dhtclient`) is enabled.
