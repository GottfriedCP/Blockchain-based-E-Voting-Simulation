# Blockchain-based E-voting Simulation

## Description

This is a Python-based Django web project to simulate a concept of blockchain-based e-voting protocol. This project should be run on the development server with Debug mode on. The simulation comprises two parts: "Block" and "Chain".

### "Block"

Submit the voter's pseudonym (UUID version 4) and the voter's choice as a ballot, which is then signed using a private key. (The public key must be registered first.) The ballot and the signature are then verified. Finally, the ballot is sealed (mined). In this part of the demo, one block contains the ballot (as transaction). The mining process is shown using the console.

### "Chain"

Generate N transactions (ballots) with valid data. Seal them into blocks. You can then explore the transactions and blocks, and validate them.

## Technical Details

In the file settings.py inside the project configurations folder, you may set some vars such as `N_TRANSACTIONS`, `N_TX_PER_BLOCK`, and the puzzle difficulty. A demo public key is also stored there as text; the matching private key file is also included.

This project uses a modified version of "pymerkletools" by Tierion for creating merkle root using SHA3.

Other details will be added later.

Also see the included reqs.txt.

## Screenshots

See the 'screenshots' folder.

## Acknowledgement

For Prof. ABM

## License

See included MIT License.