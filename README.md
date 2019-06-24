# Blockchain-based E-voting Simulation

## Description

This is a Python-based Django project to simulate a concept of blockchain-based e-voting protocol. This project should be run only on the development server with Debug mode on. The simulation comprises two sections: __"Block"__ and __"Chain"__.

### "Block"

Scenario: a potential voter has to present himself to the voting organizer, showing his ID and other legal documents. Finally, he has to submit a public key i.e., ECC. Assume that he has successfully registered the public key.

Via the ballot page (see screenshot below), the voter needs to enter his pseudonym (UUID 4) and candidate number. The ballot is then signed using a private key. If the submitted ballot is proven to be valid, it will be sealed (mined). In this section, one block contains only the aforementioned ballot. You can examine the whole process in detail using the console.

(The public-private key pair is hard coded and generated externally. See Technical Details below.)

![Ballot page](https://raw.githubusercontent.com/GottfriedCP/Blockchain-based-E-Voting-Simulation/master/screenshots/ballot.PNG)

### "Chain"

In this section, transactions (ballots) with valid data will be generated. They are then sealed into blocks. After that, you can explore the transactions and blocks, try to tamper the records, and verify them.

![Sealed ballot](https://raw.githubusercontent.com/GottfriedCP/Blockchain-based-E-Voting-Simulation/master/screenshots/transactions.PNG)

![Block](https://raw.githubusercontent.com/GottfriedCP/Blockchain-based-E-Voting-Simulation/master/screenshots/block.PNG)

_The screenshot above shows that a node's database (i.e., your node) has been tampered. You will not see this in real blockchain explorer, but this should give you a glimpse of why tampering immutable ledger is futile._

## How to run

1. Get your virtual environment ready (recommended). 
2. Locate the 'requirements.txt' file. Install necessary packages: `pip install -r requirements.txt`.
3. Locate the 'manage.py' file. Run `python manage.py runserver`. Then access http://localhost:8000.
4. From the homepage, either run 'Block' or 'Chain' section by clicking 'Start'.

## Technical Details

The private key used in this demo is located in 'bbevoting_project' folder ('demo_private.pem' file), while the corresponding public key is hard coded in 'settings.py' (look for `PUBLIC_KEY`). You may also set some config vars such as `N_TRANSACTIONS`, `N_TX_PER_BLOCK`, and the puzzle difficulty (`PUZZLE` and `PLENGTH`).

## Screenshots

See the 'screenshots' folder.

## Acknowledgement

For Prof. ABM.

This project uses a modified version of "pymerkletools" by Tierion for creating merkle root using SHA3.

## License

See included MIT License.
