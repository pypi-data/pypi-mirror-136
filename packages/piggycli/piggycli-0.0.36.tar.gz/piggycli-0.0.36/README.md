# AltPiggyBank
## _A Simple Python CLI Bitcoin Wallet for AWS CloudHSM_
## www.altmirai.com


## Features

- Setup your AWS infrastructure for CloudHSM.
- Query the status, wake, and put your AWS CloudHSM service to sleep.
- Create a bitcoin address, view all addresses, and show all the details of a specific address.
- Send bitcoin.

___
## Disclaimers
- AltPiggyBank is a proof-of-concept that should not be relied upon as stable or without errors.
- AltPiggyBank was developed and tested on macOS. AltPiggyBank may not work properly on other operating systems.
- In the event of an AltPiggyBank failure, you may be required to interact directly with CloudHSM to access cryptoassets held in an address created with AltPiggyBank.
- AltPiggyBank is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and non-infringement. In no event shall the author or copyright holders be liable for any claims, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use of other dealings in the software.

___
## Getting Started with AltPiggyBank

AltPiggyBank consists of two packages:
- piggycli (https://github.com/altmirai/piggycli)
- piggy-scripts (https://github.com/altmirai/piggy-scripts)

Piggycli is the command line interface that you install and interact with on your computer. Piggycli installs and interacts with piggy-scripts on your AWS account.

### Installing AltPiggyBank

Before installing piggycli, install the following:
- Terraform (https://learn.hashicorp.com/tutorials/terraform/install-cli)
- AWS CLI (https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

Install piggycli
```
pip install piggycli
```

### The Setup Command
The setup command sets up and configures your AWS infrastructure required to run CoudHSM.

### Your AWS Account
AltPiggyBank was written and tested on a dedicated AWS account. We recommend creating a seperate AWS account for AltPiggyBank.

- Create and activate a new AWS account (https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)
- Create a user with programatic and administrative access (https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)
- Select the closest AWS region with the lowest CloudHSM per hour-cost (https://aws.amazon.com/cloudhsm/pricing/)
- Set your region on the AWS Mgmt Console to find the AWS region code. Write it down as you will need it later.

### External Storage for AWS Credentails
AltPiggyBank looks for your AWS and CloudHSM credentials on an external drive named Piggy (path: /Volumes/Piggy)

### Run the Setup Command

``` 
piggy setup
````
Required arguments:
- **path** - the path to your external storage.
- **region** - your AWS region code.
- **id** - your AWS access key ID.
- **key** - your AWS secret access key.
- **customer-ca-key-password** - a user generated password of between 7 - 32 digits.
- **crypto-officer-password** - a user generated password of between 7 -32 digits.
 - **crypto-user-username** - a user generated username.
 - **crypto-user-password** - a user generated password of between 7 -32 digits.

You can add arguments after the piggy setup command with a -argument <value>, like this:

```
piggy setup -path <file path> -region <AWS Region Code> -id <AWS access key ID> -key <AWS secret key> -customer-ca-key-password <User generated password> -crypto-officer-password <User generated password> -crypto-user-username <User generated username> -crypto-user-password <User generated password>
```

or, just run:

```
piggy setup
```
and, AltPiggyBank will prompt you for the arguments.

Piggy setup takes between 15 to 20 minutes to complete. 

Once complete, your CloudHSM is active and AWS is charging you for its use. If you don’t plan on using it immediately:

```
piggy status -sleep
```
___
## The Status Command
CloudHSM is a pay-as-you-go service with a per-hour cost of between $1.40 and $2.72 (depending on the region you choose). CloudHSM, however, works differently than most consumer facing pay-as-you-go cloud services.

- CloudHSM must be manually started and stopped. 
- CloudHSM takes between five to ten minutes to start and stop.
- The per-hour cost is charged for each full hour and any partial hour.

As such, It wouldn’t be performant or cost effective for AltPiggyBank to start and stop CloudHSM for each cryptographic operations. So, you must manually manage the state of your CloudHSM service, creating the risk of you forgetting to stop CloudHSM and accruing unnecessary costs. If you forget to stop your CloudHSM service for a month, the cost would be around $1,000 or more.

To find the current state of your CloudHSM service, run:
```
piggy status
```

AltPiggyBank returns:
```
piggy is sleeping
```
when CloudHSM is stopped, and
```
piggy is awake
```
when CloudHSM is active.

Start CloudHSM with:
```
piggy status -wake
```

Stop CloudHSM with:
```
piggy status -sleep
```
___

## The Address Command
### Create an Address
With your piggy external drive mounted and piggy awake, run:
```
piggy address create
```
Note: The current version of AltPiggyBank only supports the P2PKH address format for address creation.

## View all adresses
With your piggy external drive mounted (piggy doesn't need to be awake), run:
```
piggy address list
```

###

Note: The current version of AltPiggyBank calls a free rate limited Blockcypher API for blockchain data.

## View a single address
With your piggy external drive mounted (piggy doesn't need to be awake), run:
```
piggy address show -id <addr id>
```
___
## The Send Command
The current version of AltPiggyBank supports sending bitcoin from one address created by AltPiggyBank to up to two bitcoin addresses (one receiving address and one change).

With your piggy external drive mounted and piggy awake, run:
```
piggy send
```

Piggy send requires the following arguments:

- **from** - the address ID for the address sending bitcoin.
- **to** - the bitcoin address for the address receiving bitcoin.
- **fee** - the mining fee in Satoshi.
- **all** or **some** -  all if sending all bitcoin to receiving address, or some if only sending some.

if **some**:
- **qty** - quantity of bitcoin in Satoshi to send to receiving address.
- **change** - the bitcoin address to send the remain bitcoin in sending address.

You can add arguments to the piggy setup command with a -argument <value>, like this:
```
piggy send -from <addr id> -to <address> -fee <mining fee> -all
```
or
```
piggy send -from <addr id> -to <address> -fee <mining fee> -some -qty <quantity> -change <address>
```

or, just run:

```
piggy send
```
and, AltPiggyBank will prompt you for the arguments.

Piggy send returns a hex formated signed raw bitcoin transaction that you can decode and broadcast using a third-party service or your own bitcoin node. 
