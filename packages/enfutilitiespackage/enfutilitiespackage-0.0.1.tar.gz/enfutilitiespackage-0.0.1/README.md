[comment]: <> (Update Repo Name here)
# CR-Boilerplate
[comment]: <> (Add Repo Description here)
Python Template Repository for GCP Cloud Run

## Repo Setup
1. Clone or update the repo along with submodule
   ```shell
   git clone --recurse-submodules git@github.com:groupnexus/CR-Boilerplate.git
   ```
   OR
   ```shell
   git pull
   git submodule init
   git submodule update
   ```

## Local Setup
1. Run the setup script
   ```shell
   sh ./.github/scripts/setup.sh
   ```
2. Follow the setup instruction provided in the link below to setup gcloud CLI
   https://cloud.google.com/sdk/docs/quickstart
4. Install pipenv
   ```
   pip install pipenv
   ```
3. Install python dependencies
   ```
   pipenv install --dev
   ```
4. Start the service
   ```shell
   python run.py
   ```
5. To Run the tests
   ```shell
   pytest
   ```
6. To check test case coverage reports
   ```shell
   coverage run --omit=venv/* -m pytest
   coverage report
   ```

## Docker Setup

1. Follow these [steps](https://docs.docker.com/compose/install/) to Setup Docker and Docker Compose.
2. Run the following command to start Services.
    ```shell
    docker-compose up -d # Run in daemonized/detached mode
    # OR
    docker-compose up # Run with logging in the foreground
    ```
   The following services run in the docker-compose environment:
    - `app`

   The following command will start only the App Service:
      ```shell
      docker-compose up app
      ```
3. Run the following command to stop individual Services:
    ```shell
    docker-compose stop <Service Name> <Service Name>
    ```
4. Run the following command to stop and remove containers:
    ```shell
    docker-compose down
    ```

### Other Useful Commands

1. Command to start Python shell

   To start a new ephemeral containers
    ```shell
    docker-compose run app python
    ```
   To use running container,
    ```shell
    docker-compose exec app python
    ```
   You can use `bash` instead of `python` to start terminal inside the container.

2. Command to install/uninstall a new dependency
   
    To install a common dependency
    ```shell
    pipenv install <package_name>
    ```
   To install a dev dependency
    ```shell
    pipenv install <package_name> --dev
    ```
   To uninstall a dependency
   ```shell
    pipenv uninstall <package_name>
    ```
