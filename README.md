# Key Protect overview

This sample app demonstrates how to use the IBM Key Protect service for Bluemix. A secret message has been encrypted for you in the `secret message.txt` file. You can decrypt the secret message using secrets stored in your Key Protect service. Once you retrieve the secrets, the AES 256 encrypted secret message is revealed. To find out more about how the service works, go to the [Bluemix docs](https://console.ng.bluemix.net/docs/services/keymgmt/index.html).

This sample app shows how to directly interact with the service by using API calls to create, retrieve, and delete secrets. lchemy-Key-Protect/bluemix-public-samples)

## How it works

1.  Secrets are added to your Key Protect instance when the sample app starts running. In your normal development workflow, the secrets would already be in the service and the only thing provided would be the secret references.

2.  Provide the required authentication information, 

3.  Push the app into Bluemix

4.  The **Decrypt the secret message!** button appears.

5.  Once you click the button, wait a few seconds for the keys to be retrieved from Key Protect.  The app uses the keys to decrypt the `secret message.txt` file.

6.  The app reveals the unencrypted message in the UI.  You may also view the message in the `revealed_msg.txt` file, which is created after pressing the button.

### Code structure
The files below are used by the sample app to demonstrate how the service works. They are for the purposes of the sample app only, as the contents would generally be too sensitive to store openly.

| File | Description |
|------|--------|
| encryption_keys.json | Contains the keys used for encryption. Encryption keys can consist of a phrase or randomly generated value of anything desired. Encryption keys can be uploaded directly into the Key Protect service by a privileged user.|
| iv.txt | Contains the initialization vector used in the AES algorithm to encrypt the secret message. The contents is usually directly uploaded into Key Protect service by a privileged user. |
| secret message.txt | Holds the message that was encrypted using AES with the `encryption_key.json` and `iv.txt` files. |


## Running the app on Bluemix
1. Create a Bluemix account. [Sign up][bluemix_signup_url] in Bluemix or use an existing account.

2. Download and install the [Cloud Foundry CLI][cloud_foundry], which is used to interact with Bluemix from the command line.

3. In a terminal window, clone the app to your local environment using the following command.

  ```
  git clone git@github.com/IBM-Bluemix/key-protect-helloworld-python.git
  ```


4. In the newly created directory, edit the `manifest.yml` file and change the `<application-name>` to something unique.

  ```none
    applications:
    - path: .
      memory: 256M
      instances: 1
      name: <application-name>
      memory: 128M
  ```
  The name you use determines your application URL initially, e.g. `<application-name>.mybluemix.net`.

5. Run the **login** command to connect to Bluemix.
  ```sh
  cf api https://api.ng.bluemix.net
  cf login -u <your_user_ID>
  ```

6. Create an instance of the Key Protect service in Bluemix.

  ```sh
  cf create-service ibm_key_management LITE sample-key-protect-service
  ```

7. Edit the `auth.json` file with your Bluemix user information.

  ```javascript
  {
      "host": "ibm-key-protect.edge.bluemix.net",
      "token": "Bearer <your token>",
      "org": "<your Bluemix organization GUID>",
      "space": "<your Bluemix space GUID>"
  }
  ```

  Fill in the blank values. You can retrieve these values using the Cloud Foundry CLI as described below.

  1. For `token`, run the following command to get your authorization token.

    ```sh
    cf oauth-token
    ```

  2. For `org`, run the following command to get your Bluemix organization GUID. If you need to look up the name of your organization, you can run `cf target` first.

    ```sh
    cf org <your_organization_name> --guid
    ```

  3. For `space`, run the following command to get your Bluemix space GUID. If you need to look up the name of your space, you can run `cf target` first.

    ```sh
    cf space <your_space_name> --guid
    ```

8. Push the sample app to Bluemix.

  ```sh
  cf push
  ```

## Running the sample applications locally

1. If you do not already have a Bluemix account, [sign up for one][bluemix_signup_url].

2. Create a space under your Bluemix organization or use an existing space.

3. In terminal, clone the app to your local environment with the following command.

  ```sh
  git clone git@github.com/IBM-Bluemix/key-protect-helloworld-python.git (should be replaced by bluemix repo)
  ```

4. In the newly created directory, install the required dependencies.

  ```sh
  pip install -r requirements.txt
  ```

5. Run the **login** command to connect to Bluemix in the command line tool.

  ```sh
  cf api https://api.ng.bluemix.net
  cf login -u <your user ID>
  ```

6. Create an instance of the Key Protect service in Bluemix.

  ```sh
  cf create-service ibm_key_management LITE sample-key-protect-service
  ```

7. Edit the `auth.json` file with your Bluemix user information.

  ```javascript
  {
      "host": "ibm-key-protect.edge.bluemix.net",
      "token": "",
      "org": "",
      "space": ""
  }
  ```

  Fill in the blank values. You can retrieve these values using the Cloud Foundry CLI as described below.

  1. For `token`, run the following command to get your authorization token.

    ```sh
    cf oauth-token
    ```

  2. For `org`, run the following command to get your Bluemix organization GUID. If you need to look up the name of your organization, you can run `cf target` first.

    ```sh
    cf org <your organization name> --guid
    ```

  3. For `space`, run the following command to get your Bluemix space GUID. If you need to look up the name of your space, you can run `cf target` first.

    ```sh
    cf space <your space name> --guid
    ```

8. Run the `welcome.py` code.

  ```sh
  ./welcome.py
  ```
[cloud_foundry]:https://github.com/cloudfoundry/cli

[bluemix_signup_url]: https://console.ng.bluemix.net/registration/

## License

  This sample code is licensed under Apache 2.0. See the [license file](LICENSE.txt) for more information.

  This sample code uses jQuery, distributed under MIT license.
